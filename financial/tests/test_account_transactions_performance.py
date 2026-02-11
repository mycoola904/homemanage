import time
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType, Transaction, TransactionType

User = get_user_model()


class AccountTransactionsPerformanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("perf-user", "perf@example.com", "perf-pass-123")
        self.account = Account.objects.create(
            user=self.user,
            name="Performance Checking",
            institution="Perf Bank",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("5000.00"),
        )
        self.detail_url = reverse("financial:accounts-detail", args=[self.account.id])

    def test_transactions_panel_renders_with_200_rows(self):
        start_date = date(2026, 1, 1)
        transactions = []
        for idx in range(200):
            transactions.append(
                Transaction(
                    account=self.account,
                    posted_on=start_date + timedelta(days=idx % 14),
                    description=f"Load Test {idx:03d}",
                    transaction_type=TransactionType.EXPENSE if idx % 2 == 0 else TransactionType.DEPOSIT,
                    amount=Decimal("5.00") + Decimal(idx),
                )
            )
        Transaction.objects.bulk_create(transactions)

        self.client.force_login(self.user)
        start = time.perf_counter()
        response = self.client.get(self.detail_url)
        duration = time.perf_counter() - start

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            duration,
            2.0,
            msg=f"/accounts/<uuid>/ took {duration:.3f}s which exceeds the 2s budget",
        )
        self.assertContains(response, "Load Test", count=200)
