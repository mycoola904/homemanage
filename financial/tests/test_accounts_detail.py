from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType

User = get_user_model()


class AccountDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.account = Account.objects.create(
            user=self.user,
            name="Hybrid Auto Loan",
            institution="Metro Finance",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=15000,
            notes="2019 crossover",
        )

    def test_owner_can_view_detail_page(self):
        self.client.force_login(self.user)
        url = reverse("financial:accounts-detail", args=[self.account.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hybrid Auto Loan")
        self.assertContains(response, "Transactions (Coming Soon)")

    def test_other_users_receive_404(self):
        other = User.objects.create_user("jamie", "jamie@example.com", "pass-9876")
        self.client.force_login(other)
        url = reverse("financial:accounts-detail", args=[self.account.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
