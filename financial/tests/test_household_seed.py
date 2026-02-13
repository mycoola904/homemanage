from django.core.management import call_command
from django.test import TestCase

from financial.models import Account, Transaction
from households.models import Household, HouseholdMember


class HouseholdSeedCommandTests(TestCase):
    def test_seed_households_is_repeatable(self):
        call_command("seed_households")
        call_command("seed_households")

        household_names = set(Household.objects.values_list("name", flat=True))
        self.assertEqual(household_names, {"Our Household", "Mother-in-law Household"})
        self.assertEqual(HouseholdMember.objects.count(), 2)
        self.assertEqual(Account.objects.count(), 2)
        self.assertEqual(Transaction.objects.count(), 2)
