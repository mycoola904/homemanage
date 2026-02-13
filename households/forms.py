from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from households.models import Household, HouseholdMember


class HouseholdCreateForm(forms.Form):
    name = forms.CharField(max_length=255)


class SettingsUserCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput)
    household_ids = forms.ModelMultipleChoiceField(
        queryset=Household.objects.none(),
        required=True,
        label="Households",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["household_ids"].queryset = Household.objects.filter(is_archived=False).order_by("name")

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        if password:
            validate_password(password)
        if not cleaned_data.get("household_ids"):
            raise ValidationError("Select at least one household.")
        return cleaned_data


class MembershipAddForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)
    role = forms.ChoiceField(choices=HouseholdMember.Role.choices, required=False)


class MembershipRemoveForm(forms.Form):
    user_id = forms.IntegerField(min_value=1)


def get_user_queryset():
    return get_user_model().objects.order_by("username")
