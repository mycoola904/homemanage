from decimal import Decimal

from django import forms

from financial.models import Account, Category, Transaction, TransactionType


class AccountImportForm(forms.Form):
    """Foundational CSV upload form for account import flow."""

    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

    import_file = forms.FileField(
        label="Import file",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".csv",
                "onchange": "document.getElementById('selected-import-filename').textContent = this.files.length ? this.files[0].name : 'No file selected';",
            }
        ),
    )

    def clean_import_file(self):
        uploaded_file = self.cleaned_data.get("import_file")
        if uploaded_file is None:
            return uploaded_file
        if uploaded_file.size > self.MAX_FILE_SIZE_BYTES:
            raise forms.ValidationError("Import file must be 5 MB or smaller.")
        if not uploaded_file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Upload a CSV file.")
        return uploaded_file


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
            "account",
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

        active_account = self._account or getattr(self.instance, "account", None)

        if active_account is not None:
            self.fields["transaction_type"].choices = TransactionType.allowed_for_account(
                active_account.account_type,
            )

        if self._user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=self._user).order_by("name")

        if active_account is not None:
            self.fields["account"].queryset = Account.objects.filter(household=active_account.household).order_by("name")
            self.fields["account"].initial = active_account.id
            self.fields["account"].required = False
        elif self._user is not None:
            self.fields["account"].queryset = Account.objects.filter(user=self._user).order_by("name")

    def clean_account(self):
        account = self.cleaned_data.get("account")
        if account is None and self._account is not None:
            return self._account
        if account is None:
            raise forms.ValidationError("Select an account.")

        if self._account is not None and account.household_id != self._account.household_id:
            raise forms.ValidationError("Selected account is outside the active household.")
        return account

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
