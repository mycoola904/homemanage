from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView

from financial.forms import AccountForm, AccountImportForm, BillPayRowForm, CategoryForm, TransactionForm
from financial.models import Account, Transaction, UserAccountQuerysetMixin
from households.services.households import resolve_current_household
from financial.services.account_import import AccountImportValidationError, import_accounts_from_csv
from financial.services.accounts import (
	AccountSummaryRow,
	build_account_preview,
	serialize_account_rows,
)
from financial.services.bill_pay import (
	BILL_PAY_DEFAULT_FOCUS_FIELD,
	BILL_PAY_FOCUS_ACTUAL_PAYMENT,
	BILL_PAY_FOCUS_PAID,
	BILL_PAY_KEYBOARD_INTENT_CANCEL,
	build_bill_pay_row,
	build_bill_pay_rows,
	get_or_initialize_monthly_payment,
	liability_accounts_for_household,
	month_to_query_value,
	normalize_bill_pay_focus_field,
	normalize_bill_pay_keyboard_intent,
	parse_month_param,
	upsert_monthly_payment,
)
from financial.services.transactions import serialize_transaction_rows


ACCOUNT_IMPORT_PANEL_ID = "account-import-panel"
ACCOUNT_IMPORT_HX_TARGET = "#account-import-panel"
ACCOUNT_IMPORT_HX_SWAP = "innerHTML"
BILL_PAY_TABLE_BODY_ID = "bill-pay-table-body"


def _get_current_household_or_redirect(request):
	context = resolve_current_household(request)
	if context.redirect is not None:
		return None, context.redirect
	return context.household, None


def _get_account_or_404(household, pk) -> Account:
	return get_object_or_404(Account, pk=pk, household=household)


def _table_copy() -> dict[str, str]:
	return {
		"empty_state_title": "No accounts yet",
		"empty_state_body": "Add your first checking, savings, or loan account to get started.",
	}


def _accounts_table_component_context(request, household) -> dict:
	accounts = Account.objects.for_household(household)
	rows = serialize_account_rows(accounts)
	copy = _table_copy()
	return {
		"rows": rows,
		"has_accounts": bool(rows),
		"add_account_url": reverse("financial:accounts-new"),
		"empty_state_title": copy["empty_state_title"],
		"empty_state_body": copy["empty_state_body"],
	}


def _render_preview_response(
	request,
	household,
	account: Account,
	*,
	include_row_oob: bool = False,
	include_table_oob: bool = False,
	status: int = 200,
) -> HttpResponse:
	preview_html = render_to_string(
		"financial/accounts/_preview.html",
		{
			"preview": build_account_preview(account),
			"preview_panel_id": "account-preview-panel",
		},
		request=request,
	)
	if include_row_oob:
		row_html = render_to_string(
			"components/financial/account_row.html",
			{"row": AccountSummaryRow.from_account(account), "swap_oob": True},
			request=request,
		)
		preview_html += row_html
	if include_table_oob:
		table_html = render_to_string(
			"components/financial/accounts_table.html",
			{
				**_accounts_table_component_context(request, household),
				"swap_oob": True,
			},
			request=request,
		)
		preview_html += table_html
	return HttpResponse(preview_html, status=status)


def _render_accounts_table_fragment(request) -> str:
	household, _ = _get_current_household_or_redirect(request)
	return render_to_string(
		"components/financial/accounts_table.html",
		_accounts_table_component_context(request, household),
		request=request,
	)


def _transactions_body_context(account: Account) -> dict:
	transactions = Transaction.objects.for_account(account).ordered()
	rows = serialize_transaction_rows(transactions)
	return {
		"transaction_rows": rows,
		"has_transactions": bool(rows),
	}


def _render_transactions_body(request, account: Account, *, status: int = 200) -> HttpResponse:
	context = _transactions_body_context(account)
	return render(
		request,
		"financial/accounts/transactions/_body.html",
		context,
		status=status,
	)


def _render_transactions_missing(request, account_id) -> HttpResponse:
	return render(
		request,
		"financial/accounts/transactions/_missing.html",
		{"account_id": account_id},
		status=200,
	)


def _bill_pay_context(request, household, *, month_param: str | None = None) -> dict:
	selected_month = parse_month_param(month_param)
	accounts = liability_accounts_for_household(household)
	rows = build_bill_pay_rows(accounts, selected_month)
	return {
		"rows": rows,
		"has_rows": bool(rows),
		"selected_month": month_to_query_value(selected_month),
		"table_body_id": BILL_PAY_TABLE_BODY_ID,
	}


def _render_bill_pay_table_body(request, household, *, month_param: str | None = None, status: int = 200) -> HttpResponse:
	try:
		context = _bill_pay_context(request, household, month_param=month_param)
	except ValueError:
		return render(
			request,
			"financial/bill_pay/_table_body.html",
			{
				"rows": [],
				"has_rows": False,
				"selected_month": timezone.localdate().strftime("%Y-%m"),
				"table_body_id": BILL_PAY_TABLE_BODY_ID,
				"table_error": "Invalid month format.",
			},
			status=400,
		)
	return render(request, "financial/bill_pay/_table_body.html", context, status=status)


def _render_bill_pay_row_missing(request, account_id, *, status: int = 404) -> HttpResponse:
	return render(
		request,
		"financial/bill_pay/_row_missing.html",
		{"account_id": account_id},
		status=status,
	)


def _render_bill_pay_row_display(request, *, account: Account, month_param: str) -> HttpResponse:
	month = parse_month_param(month_param)
	row = build_bill_pay_row(account=account, month=month)
	return render(request, "financial/bill_pay/_row.html", {"row": row})


def _bill_pay_focus_field_from_request(request, *, default: str | None = None) -> str:
	requested = request.POST.get("focus_field") or request.GET.get("focus_field")
	return normalize_bill_pay_focus_field(requested, default=default)


def _bill_pay_keyboard_intent_from_request(request) -> str | None:
	requested = request.POST.get("keyboard_intent")
	return normalize_bill_pay_keyboard_intent(requested)


def _first_bill_pay_error_focus_field(form: BillPayRowForm) -> str:
	if form.errors.get("actual_payment_amount"):
		return BILL_PAY_FOCUS_ACTUAL_PAYMENT
	if form.errors.get("paid"):
		return BILL_PAY_FOCUS_PAID
	return BILL_PAY_DEFAULT_FOCUS_FIELD


def _bill_pay_row_edit_context(*, row, form: BillPayRowForm, form_id: str, focus_field: str) -> dict:
	return {
		"row": row,
		"form": form,
		"post_hx_url": row.save_url,
		"form_id": form_id,
		"focus_field": focus_field,
		"no_funding_options": not form.fields["funding_account"].queryset.exists(),
	}


def _render_bill_pay_row_edit(request, *, account: Account, month_param: str, focus_field: str, status: int = 200) -> HttpResponse:
	month = parse_month_param(month_param)
	row = build_bill_pay_row(account=account, month=month)
	instance = get_or_initialize_monthly_payment(account=account, month=month)
	form = BillPayRowForm(instance=instance, account=account, month=month)
	form_id = f"bill-pay-form-{account.id}"
	form.fields["funding_account"].widget.attrs["form"] = form_id
	form.fields["actual_payment_amount"].widget.attrs["form"] = form_id
	form.fields["paid"].widget.attrs["form"] = form_id
	form.fields["actual_payment_amount"].widget.attrs["data-focus-field"] = BILL_PAY_FOCUS_ACTUAL_PAYMENT
	form.fields["paid"].widget.attrs["data-focus-field"] = BILL_PAY_FOCUS_PAID
	form.fields["actual_payment_amount"].widget.attrs["data-tab-order"] = "2"
	form.fields["paid"].widget.attrs["data-tab-order"] = "3"
	context = _bill_pay_row_edit_context(row=row, form=form, form_id=form_id, focus_field=focus_field)
	return render(
		request,
		"financial/bill_pay/_row_edit.html",
		context,
		status=status,
	)


def _transaction_form_context(
	*,
	form: TransactionForm,
	category_form: CategoryForm,
	post_hx_url: str,
	cancel_hx_url: str,
	category_post_url: str,
	transaction_id: str | None = None,
) -> dict:
	return {
		"form": form,
		"category_form": category_form,
		"post_hx_url": post_hx_url,
		"cancel_hx_url": cancel_hx_url,
		"category_post_url": category_post_url,
		"transaction_id": transaction_id,
	}


def _get_account_for_transactions(request, household, pk) -> Account | None:
	return Account.objects.filter(pk=pk, household=household).first()


def _get_transaction_for_account(account: Account, transaction_id) -> Transaction | None:
	return Transaction.objects.filter(account=account, pk=transaction_id).first()


@login_required
@require_http_methods(["GET", "POST"])
def account_import_page(request):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response

	is_htmx = request.headers.get("HX-Request") == "true"
	if request.method == "GET":
		form = AccountImportForm()
		context = {
			"form": form,
			"post_hx_url": reverse("financial:accounts-import"),
			"template_download_url": reverse("financial:accounts-import-template"),
			"import_panel_id": ACCOUNT_IMPORT_PANEL_ID,
			"import_hx_target": ACCOUNT_IMPORT_HX_TARGET,
			"import_hx_swap": ACCOUNT_IMPORT_HX_SWAP,
			"summary_message": "",
			"import_errors": [],
		}
		if is_htmx:
			return render(request, "financial/accounts/_import_panel.html", context)
		return render(request, "financial/accounts/import.html", context)

	form = AccountImportForm(request.POST, request.FILES)
	if not form.is_valid():
		context = {
			"form": form,
			"post_hx_url": reverse("financial:accounts-import"),
			"template_download_url": reverse("financial:accounts-import-template"),
			"import_panel_id": ACCOUNT_IMPORT_PANEL_ID,
			"import_hx_target": ACCOUNT_IMPORT_HX_TARGET,
			"import_hx_swap": ACCOUNT_IMPORT_HX_SWAP,
			"summary_message": "",
			"import_errors": ["Upload a CSV file to continue."],
		}
		if is_htmx:
			return render(request, "financial/accounts/_import_panel.html", context, status=422)
		return render(request, "financial/accounts/import.html", context, status=422)

	try:
		result = import_accounts_from_csv(
			uploaded_file=form.cleaned_data["import_file"],
			user=request.user,
			household=household,
		)
		context = {
			"form": AccountImportForm(),
			"post_hx_url": reverse("financial:accounts-import"),
			"template_download_url": reverse("financial:accounts-import-template"),
			"import_panel_id": ACCOUNT_IMPORT_PANEL_ID,
			"import_hx_target": ACCOUNT_IMPORT_HX_TARGET,
			"import_hx_swap": ACCOUNT_IMPORT_HX_SWAP,
			"summary_message": f"Imported {result.imported_rows} of {result.total_rows} rows.",
			"import_errors": [],
		}
		if is_htmx:
			return render(request, "financial/accounts/_import_panel.html", context)
		return render(request, "financial/accounts/import.html", context)
	except AccountImportValidationError as exc:
		context = {
			"form": form,
			"post_hx_url": reverse("financial:accounts-import"),
			"template_download_url": reverse("financial:accounts-import-template"),
			"import_panel_id": ACCOUNT_IMPORT_PANEL_ID,
			"import_hx_target": ACCOUNT_IMPORT_HX_TARGET,
			"import_hx_swap": ACCOUNT_IMPORT_HX_SWAP,
			"summary_message": "",
			"import_errors": exc.errors,
		}
		if is_htmx:
			return render(request, "financial/accounts/_import_panel.html", context, status=422)
		return render(request, "financial/accounts/import.html", context, status=422)


@login_required
@require_http_methods(["GET"])
def account_import_panel(request):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	if household is None:
		return HttpResponse(status=404)
	return render(
		request,
		"financial/accounts/_import_panel.html",
		{
			"form": AccountImportForm(),
			"post_hx_url": reverse("financial:accounts-import"),
			"template_download_url": reverse("financial:accounts-import-template"),
			"import_panel_id": ACCOUNT_IMPORT_PANEL_ID,
			"import_hx_target": ACCOUNT_IMPORT_HX_TARGET,
			"import_hx_swap": ACCOUNT_IMPORT_HX_SWAP,
			"summary_message": "",
			"import_errors": [],
		},
	)


@login_required
@require_http_methods(["GET"])
def account_import_template(request):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	if household is None:
		return HttpResponse(status=404)

	template_path = Path(__file__).resolve().parent / "fixtures" / "account_import_template.csv"
	if not template_path.exists():
		return HttpResponse("Template CSV is unavailable.", status=404)

	return FileResponse(
		template_path.open("rb"),
		as_attachment=True,
		filename="account_import_template.csv",
		content_type="text/csv",
	)


class AccountsIndexView(LoginRequiredMixin, UserAccountQuerysetMixin, ListView):
	"""Render the server-driven accounts table with deterministic ordering."""

	model = Account
	template_name = "financial/accounts/index.html"
	context_object_name = "accounts"

	def get_context_data(self, **kwargs):
		household, _ = _get_current_household_or_redirect(self.request)
		context = super().get_context_data(**kwargs)
		table_context = _accounts_table_component_context(self.request, household)
		context.update(
			account_rows=table_context["rows"],
			has_accounts=table_context["has_accounts"],
			add_account_url=table_context["add_account_url"],
			empty_state_title=table_context["empty_state_title"],
			empty_state_body=table_context["empty_state_body"],
			preview_panel_id="account-preview-panel",
			page_title="Accounts",
		)
		return context

	def get_queryset(self):
		household, _ = _get_current_household_or_redirect(self.request)
		return Account.objects.for_household(household)

	def dispatch(self, request, *args, **kwargs):
		_, redirect_response = _get_current_household_or_redirect(request)
		if redirect_response is not None:
			return redirect_response
		return super().dispatch(request, *args, **kwargs)


@login_required
@require_http_methods(["GET"])
def bill_pay_index(request):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	context = _bill_pay_context(request, household, month_param=request.GET.get("month"))
	context.update(
		page_title="Bill Pay",
		table_body_url=reverse("financial:bill-pay-table-body"),
	)
	return render(request, "financial/bill_pay/index.html", context)


@login_required
@require_http_methods(["GET"])
def bill_pay_table_body(request):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	return _render_bill_pay_table_body(request, household, month_param=request.GET.get("month"))


@login_required
@require_http_methods(["GET", "POST"])
def bill_pay_row(request, account_id):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	month_param = request.GET.get("month")
	if not month_param:
		return _render_bill_pay_row_missing(request, account_id, status=404)
	try:
		month = parse_month_param(month_param)
	except ValueError:
		return _render_bill_pay_row_missing(request, account_id, status=404)

	try:
		account = _get_account_or_404(household, account_id)
	except Http404:
		return _render_bill_pay_row_missing(request, account_id, status=404)

	if account.account_type not in {"credit_card", "loan", "other"}:
		return _render_bill_pay_row_missing(request, account_id, status=404)

	focus_field = _bill_pay_focus_field_from_request(request)

	if request.method == "GET":
		return _render_bill_pay_row_edit(request, account=account, month_param=month_param, focus_field=focus_field)

	keyboard_intent = _bill_pay_keyboard_intent_from_request(request)
	if keyboard_intent == BILL_PAY_KEYBOARD_INTENT_CANCEL:
		return _render_bill_pay_row_display(request, account=account, month_param=month_param)

	instance = get_or_initialize_monthly_payment(account=account, month=month)
	form = BillPayRowForm(request.POST, instance=instance, account=account, month=month)
	row = build_bill_pay_row(account=account, month=month)
	form_id = f"bill-pay-form-{account.id}"
	form.fields["funding_account"].widget.attrs["form"] = form_id
	form.fields["actual_payment_amount"].widget.attrs["form"] = form_id
	form.fields["paid"].widget.attrs["form"] = form_id
	form.fields["actual_payment_amount"].widget.attrs["data-focus-field"] = BILL_PAY_FOCUS_ACTUAL_PAYMENT
	form.fields["paid"].widget.attrs["data-focus-field"] = BILL_PAY_FOCUS_PAID
	form.fields["actual_payment_amount"].widget.attrs["data-tab-order"] = "2"
	form.fields["paid"].widget.attrs["data-tab-order"] = "3"
	if form.is_valid():
		saved = form.save(commit=False)
		payment = upsert_monthly_payment(
			account=account,
			month=month,
			funding_account=saved.funding_account,
			actual_payment_amount=saved.actual_payment_amount,
			paid=saved.paid,
		)
		_ = payment
		return _render_bill_pay_row_display(request, account=account, month_param=month_param)

	context = _bill_pay_row_edit_context(
		row=row,
		form=form,
		form_id=form_id,
		focus_field=_first_bill_pay_error_focus_field(form),
	)
	return render(
		request,
		"financial/bill_pay/_row_edit.html",
		context,
		status=422,
	)


class AccountCreateView(LoginRequiredMixin, CreateView):
	"""Full-page account creation flow (redirects back to index)."""

	model = Account
	form_class = AccountForm
	template_name = "financial/accounts/new.html"
	success_url = reverse_lazy("financial:accounts-index")

	def get_form_kwargs(self):  # pragma: no cover - CBV hook
		kwargs = super().get_form_kwargs()
		kwargs["user"] = self.request.user
		return kwargs

	def form_valid(self, form):
		household, redirect_response = _get_current_household_or_redirect(self.request)
		if redirect_response is not None:
			return redirect_response
		form.instance.user = self.request.user
		form.instance.household = household
		response = super().form_valid(form)
		messages.success(self.request, "Account created successfully.")
		return response

	def dispatch(self, request, *args, **kwargs):
		_, redirect_response = _get_current_household_or_redirect(request)
		if redirect_response is not None:
			return redirect_response
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		form = context.get("form")
		context.update(
			page_title="Add Account",
			submit_label="Create account",
			cancel_url=reverse("financial:accounts-index"),
			hidden_field_names=getattr(form, "hidden_field_names", []),
		)
		return context


class AccountDetailView(LoginRequiredMixin, UserAccountQuerysetMixin, DetailView):
	model = Account
	template_name = "financial/accounts/detail.html"
	context_object_name = "account"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		transactions_context = _transactions_body_context(self.object)
		context.update(
			page_title=self.object.name,
			preview=build_account_preview(self.object),
			transactions_new_url=reverse("financial:account-transactions-new", args=[self.object.id]),
			transactions_body_url=reverse("financial:account-transactions-body", args=[self.object.id]),
			**transactions_context,
		)
		return context

	def get_queryset(self):
		household, _ = _get_current_household_or_redirect(self.request)
		return Account.objects.for_household(household)

	def dispatch(self, request, *args, **kwargs):
		_, redirect_response = _get_current_household_or_redirect(request)
		if redirect_response is not None:
			return redirect_response
		return super().dispatch(request, *args, **kwargs)


@login_required
@require_http_methods(["GET"])
def account_preview(request, pk):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	try:
		account = _get_account_or_404(household, pk)
	except Http404:
		return render(
			request,
			"financial/accounts/_preview_missing.html",
			{"account_id": pk},
			status=404,
		)

	context = {
		"preview": build_account_preview(account),
		"preview_panel_id": "account-preview-panel",
	}
	return render(request, "financial/accounts/_preview.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def account_edit(request, pk):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	account = _get_account_or_404(household, pk)
	post_hx_url = reverse("financial:accounts-edit", args=[account.id])
	if request.method == "GET":
		form = AccountForm(instance=account, user=request.user)
		return render(
			request,
			"financial/accounts/_form.html",
			{
				"form": form,
				"submit_label": "Save changes",
				"post_hx_url": post_hx_url,
				"cancel_hx_url": reverse("financial:accounts-preview", args=[account.id]),
				"hidden_field_names": getattr(form, "hidden_field_names", []),
			},
		)

	form = AccountForm(request.POST, instance=account, user=request.user)
	if form.is_valid():
		account = form.save()
		return _render_preview_response(request, household, account, include_table_oob=True)

	return render(
		request,
		"financial/accounts/_form.html",
		{
			"form": form,
			"submit_label": "Save changes",
			"post_hx_url": post_hx_url,
			"cancel_hx_url": reverse("financial:accounts-preview", args=[account.id]),
			"hidden_field_names": getattr(form, "hidden_field_names", []),
		},
		status=422,
	)


@login_required
@require_http_methods(["GET"])
def account_delete_confirm(request, pk):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	try:
		account = _get_account_or_404(household, pk)
	except Http404:
		return render(
			request,
			"financial/accounts/_preview_missing.html",
			{"account_id": pk},
			status=404,
		)
	return render(
		request,
		"financial/accounts/_delete_confirm.html",
		{
			"account": account,
			"preview_panel_id": "account-preview-panel",
		},
	)


@login_required
@require_http_methods(["POST"])
def account_delete(request, pk):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	try:
		account = _get_account_or_404(household, pk)
	except Http404:
		return render(
			request,
			"financial/accounts/_preview_missing.html",
			{"account_id": pk},
			status=404,
		)

	account.delete()
	table_html = render_to_string(
		"components/financial/accounts_table.html",
		{
			**_accounts_table_component_context(request, household),
			"swap_oob": True,
		},
		request=request,
	)
	preview_reset = render_to_string(
		"financial/accounts/_preview_empty.html",
		request=request,
	)
	return HttpResponse(preview_reset + table_html)


@login_required
@require_http_methods(["GET"])
def account_transactions_body(request, pk):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	account = _get_account_for_transactions(request, household, pk)
	if account is None:
		return _render_transactions_missing(request, pk)
	return _render_transactions_body(request, account)


@login_required
@require_http_methods(["GET", "POST"])
def account_transactions_new(request, pk):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	account = _get_account_for_transactions(request, household, pk)
	if account is None:
		return _render_transactions_missing(request, pk)

	post_hx_url = reverse("financial:account-transactions-new", args=[account.id])
	cancel_hx_url = reverse("financial:account-transactions-body", args=[account.id])
	category_post_url = reverse("financial:account-transactions-category-new", args=[account.id])
	if request.method == "GET":
		form = TransactionForm(
			initial={"posted_on": timezone.localdate(), "account": account.id},
			account=account,
			user=request.user,
		)
		category_form = CategoryForm(user=request.user)
		return render(
			request,
			"financial/accounts/transactions/_form.html",
			_transaction_form_context(
				form=form,
				category_form=category_form,
				post_hx_url=post_hx_url,
				cancel_hx_url=cancel_hx_url,
				category_post_url=category_post_url,
			),
		)

	form = TransactionForm(request.POST, account=account, user=request.user)
	if form.is_valid():
		transaction = form.save(commit=False)
		transaction.account = form.cleaned_data["account"]
		transaction.household = transaction.account.household
		transaction.save()
		return _render_transactions_body(request, transaction.account)

	category_form = CategoryForm(user=request.user)

	return render(
		request,
		"financial/accounts/transactions/_form.html",
		_transaction_form_context(
			form=form,
			category_form=category_form,
			post_hx_url=post_hx_url,
			cancel_hx_url=cancel_hx_url,
			category_post_url=category_post_url,
		),
		status=422,
	)


@login_required
@require_http_methods(["GET", "POST"])
def account_transactions_edit(request, pk, transaction_id):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	account = _get_account_for_transactions(request, household, pk)
	if account is None:
		return _render_transactions_missing(request, pk)

	transaction = _get_transaction_for_account(account, transaction_id)
	if transaction is None:
		return _render_transactions_body(request, account, status=404)

	post_hx_url = reverse("financial:account-transactions-edit", args=[account.id, transaction.id])
	cancel_hx_url = reverse("financial:account-transactions-body", args=[account.id])
	category_post_url = reverse("financial:account-transactions-category-new", args=[account.id])

	if request.method == "GET":
		form = TransactionForm(instance=transaction, account=account, user=request.user)
		category_form = CategoryForm(user=request.user)
		return render(
			request,
			"financial/accounts/transactions/_form.html",
			_transaction_form_context(
				form=form,
				category_form=category_form,
				post_hx_url=post_hx_url,
				cancel_hx_url=cancel_hx_url,
				category_post_url=category_post_url,
			),
		)

	form = TransactionForm(request.POST, instance=transaction, account=account, user=request.user)
	if form.is_valid():
		updated_transaction = form.save(commit=False)
		if updated_transaction.account.household_id != household.id:
			form.add_error("account", "Selected account is outside the active household.")
		else:
			updated_transaction.household = updated_transaction.account.household
			updated_transaction.save()
			return _render_transactions_body(request, updated_transaction.account)

	category_form = CategoryForm(user=request.user)
	return render(
		request,
		"financial/accounts/transactions/_form.html",
		_transaction_form_context(
			form=form,
			category_form=category_form,
			post_hx_url=post_hx_url,
			cancel_hx_url=cancel_hx_url,
			category_post_url=category_post_url,
		),
		status=422,
	)


@login_required
@require_http_methods(["POST"])
def account_transactions_category_new(request, pk):
	household, redirect_response = _get_current_household_or_redirect(request)
	if redirect_response is not None:
		return redirect_response
	account = _get_account_for_transactions(request, household, pk)
	if account is None:
		return _render_transactions_missing(request, pk)

	transaction_id = request.POST.get("transaction_id")
	transaction = None
	if transaction_id:
		transaction = _get_transaction_for_account(account, transaction_id)
		if transaction is None:
			return _render_transactions_body(request, account, status=404)

	if transaction is None:
		post_hx_url = reverse("financial:account-transactions-new", args=[account.id])
	else:
		post_hx_url = reverse(
			"financial:account-transactions-edit",
			args=[account.id, transaction.id],
		)
	cancel_hx_url = reverse("financial:account-transactions-body", args=[account.id])
	category_post_url = reverse("financial:account-transactions-category-new", args=[account.id])

	category_form = CategoryForm(request.POST, user=request.user)
	data = request.POST.copy()
	if category_form.is_valid():
		category = category_form.save(commit=False)
		category.user = request.user
		category.save()
		data["category"] = str(category.id)
		transaction_form = TransactionForm(
			data,
			instance=transaction,
			account=account,
			user=request.user,
		)
		category_form = CategoryForm(user=request.user)
		return render(
			request,
			"financial/accounts/transactions/_form.html",
			_transaction_form_context(
				form=transaction_form,
				category_form=category_form,
				post_hx_url=post_hx_url,
				cancel_hx_url=cancel_hx_url,
				category_post_url=category_post_url,
				transaction_id=str(transaction.id) if transaction else None,
			),
		)

	transaction_form = TransactionForm(
		data,
		instance=transaction,
		account=account,
		user=request.user,
	)
	return render(
		request,
		"financial/accounts/transactions/_form.html",
		_transaction_form_context(
			form=transaction_form,
			category_form=category_form,
			post_hx_url=post_hx_url,
			cancel_hx_url=cancel_hx_url,
			category_post_url=category_post_url,
			transaction_id=str(transaction.id) if transaction else None,
		),
		status=400,
	)
