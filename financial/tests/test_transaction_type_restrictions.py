from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from financial.models import Account, AccountStatus, AccountType, Transaction, TransactionType

User = get_user_model()


class TransactionTypeRestrictionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.checking = Account.objects.create(
            user=self.user,
            name="Checking",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=Decimal("100.00"),
        )

    def test_disallowed_transaction_type_rejected(self):
        txn = Transaction(
            account=self.checking,
            posted_on="2026-02-01",
            description="Payment",
            transaction_type=TransactionType.PAYMENT,
            amount=Decimal("10.00"),
        )
        with self.assertRaises(ValidationError):
            txn.full_clean()

    def test_negative_or_zero_amount_rejected(self):
        txn_zero = Transaction(
            account=self.checking,
            posted_on="2026-02-02",
            description="Zero",
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("0"),
        )
        with self.assertRaises(ValidationError):
            txn_zero.full_clean()

        txn_negative = Transaction(
            account=self.checking,
            posted_on="2026-02-03",
            description="Negative",
            transaction_type=TransactionType.DEPOSIT,
            amount=Decimal("-5.00"),
        )
        with self.assertRaises(ValidationError):
            txn_negative.full_clean()
