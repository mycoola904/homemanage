from decimal import Decimal

from django import forms

from financial.models import Account, Transaction, TransactionDirection


class AccountForm(forms.ModelForm):
    """Model-backed form used for create/edit flows."""

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        if self._user is None and getattr(self.instance, "user_id", None):
            self._user = self.instance.user

    class Meta:
        model = Account
        fields = [
            "name",
            "institution",
            "account_type",
            "number_last4",
            "status",
            "current_balance",
            "credit_limit_or_principal",
            "statement_close_date",
            "payment_due_day",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
            "statement_close_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        user = self._user or getattr(self.instance, "user", None)
        if not name or user is None:
            return name

        conflict_qs = Account.objects.filter(user=user, name__iexact=name)
        if self.instance.pk:
            conflict_qs = conflict_qs.exclude(pk=self.instance.pk)
        if conflict_qs.exists():
            raise forms.ValidationError("You already have an account with this name.")
        return name


class TransactionForm(forms.ModelForm):
    """Model-backed form for inline transaction creation."""

    class Meta:
        model = Transaction
        fields = [
            "posted_on",
            "description",
            "direction",
            "amount",
            "notes",
        ]
        widgets = {
            "posted_on": forms.DateInput(attrs={"type": "date"}),
            "direction": forms.RadioSelect(choices=TransactionDirection.choices),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_description(self):
        description = (self.cleaned_data.get("description") or "").strip()
        if not description:
            raise forms.ValidationError("Enter a description.")
        return description

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            return amount
        if amount <= Decimal("0"):
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount
