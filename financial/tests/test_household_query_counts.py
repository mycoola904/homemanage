from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Household, HouseholdMember


User = get_user_model()


class HouseholdQueryCountTests(TestCase):
    def test_accounts_index_query_count_stays_reasonable_under_household_scope(self):
        user = User.objects.create_user("queryuser", "query@example.com", "pass-1234")
        household = Household.objects.create(name="Query Household", slug="query-household", created_by=user)
        HouseholdMember.objects.create(household=household, user=user, role=HouseholdMember.Role.OWNER, is_primary=True)
        for idx in range(5):
            Account.objects.create(
                user=user,
                household=household,
                name=f"Account {idx}",
                account_type=AccountType.CHECKING,
                status=AccountStatus.ACTIVE,
                current_balance=100 + idx,
            )

        self.client.force_login(user)
        with CaptureQueriesContext(connection) as query_context:
            response = self.client.get(reverse("financial:accounts-index"))
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(query_context), 12)
