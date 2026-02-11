from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from financial.models import Account, AccountStatus, AccountType, Transaction, TransactionType

User = get_user_model()


class TransactionSignMatrixTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.accounts = {
            AccountType.CHECKING: Account.objects.create(
                user=self.user,
                name="Checking",
                institution="Civic",
                account_type=AccountType.CHECKING,
                status=AccountStatus.ACTIVE,
                current_balance=Decimal("100.00"),
            ),
            AccountType.SAVINGS: Account.objects.create(
                user=self.user,
                name="Savings",
                institution="Civic",
                account_type=AccountType.SAVINGS,
                status=AccountStatus.ACTIVE,
                current_balance=Decimal("200.00"),
            ),
            AccountType.CREDIT_CARD: Account.objects.create(
                user=self.user,
                name="Card",
                institution="Civic",
                account_type=AccountType.CREDIT_CARD,
                status=AccountStatus.ACTIVE,
                current_balance=Decimal("300.00"),
            ),
            AccountType.LOAN: Account.objects.create(
                user=self.user,
                name="Loan",
                institution="Civic",
                account_type=AccountType.LOAN,
                status=AccountStatus.ACTIVE,
                current_balance=Decimal("400.00"),
            ),
            AccountType.OTHER: Account.objects.create(
                user=self.user,
                name="Other",
                institution="Civic",
                account_type=AccountType.OTHER,
                status=AccountStatus.ACTIVE,
                current_balance=Decimal("500.00"),
            ),
        }

    def test_sign_matrix_applies_to_amount(self):
        cases = [
            (AccountType.CHECKING, TransactionType.DEPOSIT, Decimal("10.00")),
            (AccountType.CHECKING, TransactionType.EXPENSE, Decimal("-10.00")),
            (AccountType.CHECKING, TransactionType.TRANSFER, Decimal("-10.00")),
            (AccountType.CHECKING, TransactionType.ADJUSTMENT, Decimal("10.00")),
            (AccountType.SAVINGS, TransactionType.DEPOSIT, Decimal("10.00")),
            (AccountType.SAVINGS, TransactionType.EXPENSE, Decimal("-10.00")),
            (AccountType.SAVINGS, TransactionType.TRANSFER, Decimal("-10.00")),
            (AccountType.SAVINGS, TransactionType.ADJUSTMENT, Decimal("10.00")),
            (AccountType.CREDIT_CARD, TransactionType.PAYMENT, Decimal("-10.00")),
            (AccountType.CREDIT_CARD, TransactionType.CHARGE, Decimal("10.00")),
            (AccountType.CREDIT_CARD, TransactionType.ADJUSTMENT, Decimal("-10.00")),
            (AccountType.LOAN, TransactionType.PAYMENT, Decimal("-10.00")),
            (AccountType.LOAN, TransactionType.CHARGE, Decimal("10.00")),
            (AccountType.LOAN, TransactionType.ADJUSTMENT, Decimal("-10.00")),
            (AccountType.OTHER, TransactionType.PAYMENT, Decimal("-10.00")),
            (AccountType.OTHER, TransactionType.CHARGE, Decimal("10.00")),
            (AccountType.OTHER, TransactionType.ADJUSTMENT, Decimal("-10.00")),
        ]

        for account_type, transaction_type, expected in cases:
            with self.subTest(account_type=account_type, transaction_type=transaction_type):
                transaction = Transaction.objects.create(
                    account=self.accounts[account_type],
                    posted_on="2026-02-01",
                    description="Matrix",
                    transaction_type=transaction_type,
                    amount=Decimal("10.00"),
                )
                transaction.refresh_from_db()
                self.assertEqual(transaction.amount, expected)
