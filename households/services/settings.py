from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from households.models import Household, HouseholdMember


def normalize_household_name(name: str) -> str:
    return " ".join((name or "").strip().split())


def household_name_exists(name: str) -> bool:
    normalized = normalize_household_name(name)
    if not normalized:
        return False
    existing_names = Household.objects.values_list("name", flat=True)
    return any(normalize_household_name(existing).casefold() == normalized.casefold() for existing in existing_names)


def _build_unique_slug(base_name: str) -> str:
    base_slug = slugify(base_name) or "household"
    slug = base_slug
    index = 2
    while Household.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{index}"
        index += 1
    return slug


def create_household(*, name: str, created_by=None) -> Household:
    normalized = normalize_household_name(name)
    if not normalized:
        raise ValidationError({"name": "Household name is required."})
    if household_name_exists(normalized):
        raise ValidationError({"name": "A household with this name already exists."})
    household = Household.objects.create(
        name=normalized,
        slug=_build_unique_slug(normalized),
        created_by=created_by,
    )
    return household


def create_user_with_memberships(*, username: str, email: str, password: str, household_ids: list[str]):
    if Household.objects.count() == 0:
        raise ValidationError("Create a household before creating user accounts.")
    if not household_ids:
        raise ValidationError("Select at least one household.")

    UserModel = get_user_model()
    if UserModel.objects.filter(username=username).exists():
        raise ValidationError({"username": "Username already exists."})
    if UserModel.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": "Email already exists."})

    households = list(Household.objects.filter(id__in=household_ids, is_archived=False))
    if len(households) != len(set(household_ids)):
        raise ValidationError({"household_ids": "One or more selected households are invalid."})

    with transaction.atomic():
        user = UserModel.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        HouseholdMember.objects.bulk_create(
            [
                HouseholdMember(household=household, user=user, role=HouseholdMember.Role.MEMBER)
                for household in households
            ]
        )
    return user


def add_membership(*, household: Household, user, role: str = HouseholdMember.Role.MEMBER):
    membership, created = HouseholdMember.objects.get_or_create(
        household=household,
        user=user,
        defaults={"role": role},
    )
    if not created and membership.role != role:
        membership.role = role
        membership.save(update_fields=["role", "updated_at"])
    return membership, created


def remove_membership(*, household: Household, user) -> bool:
    membership = HouseholdMember.objects.filter(household=household, user=user).first()
    if membership is None:
        return False
    membership.delete()
    return True
