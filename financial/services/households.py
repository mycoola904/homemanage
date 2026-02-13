from __future__ import annotations

from dataclasses import dataclass

from django.http import HttpResponseRedirect
from django.urls import reverse

from financial.models import Household, HouseholdMember


CURRENT_HOUSEHOLD_SESSION_KEY = "current_household_id"


@dataclass(frozen=True)
class HouseholdContext:
    household: Household | None
    redirect: HttpResponseRedirect | None = None


def memberships_for_user(user):
    if user is None or not getattr(user, "is_authenticated", False):
        return HouseholdMember.objects.none()
    return HouseholdMember.objects.select_related("household").filter(user=user, household__is_archived=False)


def select_household_for_user(user) -> Household | None:
    membership = (
        memberships_for_user(user)
        .order_by("-is_primary", "created_at", "household__name", "household_id")
        .first()
    )
    return membership.household if membership else None


def get_user_households(user):
    return [membership.household for membership in memberships_for_user(user).order_by("household__name")]


def set_current_household(request, household: Household | None) -> None:
    if household is None:
        request.session.pop(CURRENT_HOUSEHOLD_SESSION_KEY, None)
        return
    request.session[CURRENT_HOUSEHOLD_SESSION_KEY] = str(household.id)


def resolve_current_household(request) -> HouseholdContext:
    if not request.user.is_authenticated:
        return HouseholdContext(household=None)

    session_household_id = request.session.get(CURRENT_HOUSEHOLD_SESSION_KEY)
    if session_household_id:
        membership = memberships_for_user(request.user).filter(household_id=session_household_id).first()
        if membership:
            return HouseholdContext(household=membership.household)

    fallback_household = select_household_for_user(request.user)
    if fallback_household is None:
        set_current_household(request, None)
        return HouseholdContext(household=None)

    set_current_household(request, fallback_household)
    return HouseholdContext(household=fallback_household)


def can_switch_to_household(user, household_id) -> bool:
    return memberships_for_user(user).filter(household_id=household_id).exists()
