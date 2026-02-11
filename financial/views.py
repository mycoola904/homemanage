from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DetailView, ListView

from financial.forms import AccountForm
from financial.models import Account, UserAccountQuerysetMixin
from financial.services.accounts import (
	AccountSummaryRow,
	build_account_preview,
	serialize_account_rows,
)


def _get_account_or_404(user, pk) -> Account:
	return get_object_or_404(Account, pk=pk, user=user)


def _table_copy() -> dict[str, str]:
	return {
		"empty_state_title": "No accounts yet",
		"empty_state_body": "Add your first checking, savings, or loan account to get started.",
	}


def _accounts_table_component_context(request) -> dict:
	accounts = Account.objects.for_user(request.user)
	rows = serialize_account_rows(accounts)
	copy = _table_copy()
	return {
		"rows": rows,
		"has_accounts": bool(rows),
		"add_account_url": reverse("financial:accounts-new"),
		"empty_state_title": copy["empty_state_title"],
		"empty_state_body": copy["empty_state_body"],
	}


def _render_preview_response(request, account: Account, *, include_row_oob: bool = False, status: int = 200) -> HttpResponse:
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
	return HttpResponse(preview_html, status=status)


def _render_accounts_table_fragment(request) -> str:
	return render_to_string(
		"components/financial/accounts_table.html",
		_accounts_table_component_context(request),
		request=request,
	)


class AccountsIndexView(LoginRequiredMixin, UserAccountQuerysetMixin, ListView):
	"""Render the server-driven accounts table with deterministic ordering."""

	model = Account
	template_name = "financial/accounts/index.html"
	context_object_name = "accounts"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		table_context = _accounts_table_component_context(self.request)
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
		form.instance.user = self.request.user
		response = super().form_valid(form)
		messages.success(self.request, "Account created successfully.")
		return response

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(
			page_title="Add Account",
			submit_label="Create account",
			cancel_url=reverse("financial:accounts-index"),
		)
		return context


class AccountDetailView(LoginRequiredMixin, UserAccountQuerysetMixin, DetailView):
	model = Account
	template_name = "financial/accounts/detail.html"
	context_object_name = "account"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(
			page_title=self.object.name,
			preview=build_account_preview(self.object),
		)
		return context


@login_required
@require_http_methods(["GET"])
def account_preview(request, pk):
	try:
		account = _get_account_or_404(request.user, pk)
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
	account = _get_account_or_404(request.user, pk)
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
			},
		)

	form = AccountForm(request.POST, instance=account, user=request.user)
	if form.is_valid():
		account = form.save()
		return _render_preview_response(request, account, include_row_oob=True)

	return render(
		request,
		"financial/accounts/_form.html",
		{
			"form": form,
			"submit_label": "Save changes",
			"post_hx_url": post_hx_url,
			"cancel_hx_url": reverse("financial:accounts-preview", args=[account.id]),
		},
		status=422,
	)


@login_required
@require_http_methods(["GET"])
def account_delete_confirm(request, pk):
	try:
		account = _get_account_or_404(request.user, pk)
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
	try:
		account = _get_account_or_404(request.user, pk)
	except Http404:
		return render(
			request,
			"financial/accounts/_preview_missing.html",
			{"account_id": pk},
			status=404,
		)

	account.delete()
	table_html = _render_accounts_table_fragment(request)
	preview_reset = render_to_string(
		"components/financial/account_preview_panel.html",
		{"panel_id": "account-preview-panel", "swap_oob": True},
		request=request,
	)
	return HttpResponse(table_html + preview_reset)
