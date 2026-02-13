from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView

from financial.forms import AccountForm, CategoryForm, TransactionForm
from financial.models import Account, Transaction, UserAccountQuerysetMixin
from households.services.households import resolve_current_household
from financial.services.accounts import (
	AccountSummaryRow,
	build_account_preview,
	serialize_account_rows,
)
from financial.services.transactions import serialize_transaction_rows


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
