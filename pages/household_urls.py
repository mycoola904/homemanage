from django.urls import path

from pages.views import HouseholdHomeView, no_household_access, switch_household

app_name = "household"

urlpatterns = [
    path("", HouseholdHomeView.as_view(), name="home"),
    path("switch/", switch_household, name="switch"),
    path("no-access/", no_household_access, name="no-household-access"),
]
