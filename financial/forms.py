from decimal import Decimal

from django import forms

from financial.models import Account, Category, Transaction, TransactionType


class AccountForm(forms.ModelForm):
    """Model-backed form used for create/edit flows."""

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        if self._user is None and getattr(self.instance, "user_id", None):
            self._user = self.instance.user

        account_type = (
            self.data.get("account_type")
            or self.initial.get("account_type")
            or getattr(self.instance, "account_type", None)
        )
        routing_allowed = {"checking", "savings"}
        interest_allowed = {"credit_card", "loan", "other"}

        self.hidden_field_names: list[str] = []
        if account_type:
            if account_type not in routing_allowed:
                self.hidden_field_names.append("routing_number")
            if account_type not in interest_allowed:
                self.hidden_field_names.append("interest_rate")

    class Meta:
        model = Account
        fields = [
            "name",
            "institution",
            "account_type",
            "account_number",
            "routing_number",
            "interest_rate",
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

    def clean(self):
        cleaned_data = super().clean()
        account_type = cleaned_data.get("account_type")
        if not account_type:
            return cleaned_data

        routing_number = cleaned_data.get("routing_number")
        interest_rate = cleaned_data.get("interest_rate")

        if account_type not in {"checking", "savings"}:
            if routing_number:
                self.add_error(
                    "routing_number",
                    "Routing numbers are only for checking or savings accounts.",
                )
                self.add_error(
                    None,
                    "Routing numbers are only for checking or savings accounts.",
                )
            cleaned_data["routing_number"] = None

        if account_type not in {"credit_card", "loan", "other"}:
            if interest_rate is not None:
                self.add_error(
                    "interest_rate",
                    "Interest rates are only for credit or loan accounts.",
                )
                self.add_error(
                    None,
                    "Interest rates are only for credit or loan accounts.",
                )
            cleaned_data["interest_rate"] = None

        return cleaned_data


class TransactionForm(forms.ModelForm):
    """Model-backed form for inline transaction creation."""

    class Meta:
        model = Transaction
        fields = [
            "posted_on",
            "description",
            "transaction_type",
            "amount",
            "category",
            "notes",
        ]
        widgets = {
            "posted_on": forms.DateInput(attrs={"type": "date"}),
            "transaction_type": forms.RadioSelect(choices=TransactionType.choices),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, account=None, user=None, **kwargs):
        self._account = account
        self._user = user
        super().__init__(*args, **kwargs)

        if self._account is not None:
            self.instance.account = self._account

        if self._account is not None:
            self.fields["transaction_type"].choices = TransactionType.allowed_for_account(
                self._account.account_type,
            )

        if self._user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=self._user).order_by("name")

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


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        self.fields["name"].error_messages["required"] = "Enter a category name."

    class Meta:
        model = Category
        fields = ["name"]

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Enter a category name.")
        if self._user is None:
            return name

        conflict_qs = Category.objects.filter(user=self._user, name__iexact=name)
        if conflict_qs.exists():
            raise forms.ValidationError("You already have a category with this name.")
        return name
