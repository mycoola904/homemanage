from django.urls import path

from households.views import (
    settings_household_create,
    settings_index,
    settings_membership_add,
    settings_membership_remove,
    settings_user_create,
)
from pages.views import HouseholdHomeView, no_household_access, switch_household

app_name = "household"

urlpatterns = [
    path("", HouseholdHomeView.as_view(), name="home"),
    path("switch/", switch_household, name="switch"),
    path("no-access/", no_household_access, name="no-household-access"),
    path("settings/", settings_index, name="settings-index"),
    path("settings/households/", settings_household_create, name="settings-households-create"),
    path("settings/users/", settings_user_create, name="settings-users-create"),
    path(
        "settings/households/<uuid:household_id>/memberships/",
        settings_membership_add,
        name="settings-memberships-add",
    ),
    path(
        "settings/households/<uuid:household_id>/memberships/<int:user_id>/remove/",
        settings_membership_remove,
        name="settings-memberships-remove",
    ),
]
