from datetime import date
from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class TransactionTypeBackfillTests(TransactionTestCase):
    migrate_from = [("financial", "0002_transaction")]
    migrate_to = [("financial", "0003_account_transaction_evolution")]

    def setUp(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        apps = self.executor.loader.project_state(self.migrate_from).apps

        User = apps.get_model("auth", "User")
        Account = apps.get_model("financial", "Account")
        Transaction = apps.get_model("financial", "Transaction")

        user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        checking = Account.objects.create(
            user=user,
            name="Checking",
            institution="Civic",
            account_type="checking",
            status="active",
            current_balance=Decimal("100.00"),
        )
        credit_card = Account.objects.create(
            user=user,
            name="Card",
            institution="Civic",
            account_type="credit_card",
            status="active",
            current_balance=Decimal("250.00"),
        )

        self.txn_ids = {
            "checking_credit": Transaction.objects.create(
                account=checking,
                posted_on=date(2026, 2, 1),
                description="Checking credit",
                direction="credit",
                amount=Decimal("10.00"),
            ).id,
            "checking_debit": Transaction.objects.create(
                account=checking,
                posted_on=date(2026, 2, 2),
                description="Checking debit",
                direction="debit",
                amount=Decimal("5.00"),
            ).id,
            "card_credit": Transaction.objects.create(
                account=credit_card,
                posted_on=date(2026, 2, 3),
                description="Card credit",
                direction="credit",
                amount=Decimal("20.00"),
            ).id,
            "card_debit": Transaction.objects.create(
                account=credit_card,
                posted_on=date(2026, 2, 4),
                description="Card debit",
                direction="debit",
                amount=Decimal("7.00"),
            ).id,
        }

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        self.apps = self.executor.loader.project_state(self.migrate_to).apps

    def test_backfill_direction_to_transaction_type(self):
        Transaction = self.apps.get_model("financial", "Transaction")

        self.assertEqual(
            Transaction.objects.get(id=self.txn_ids["checking_credit"]).transaction_type,
            "deposit",
        )
        self.assertEqual(
            Transaction.objects.get(id=self.txn_ids["checking_debit"]).transaction_type,
            "expense",
        )
        self.assertEqual(
            Transaction.objects.get(id=self.txn_ids["card_credit"]).transaction_type,
            "charge",
        )
        self.assertEqual(
            Transaction.objects.get(id=self.txn_ids["card_debit"]).transaction_type,
            "payment",
        )


class HouseholdBackfillMigrationTests(TransactionTestCase):
    migrate_from = [("financial", "0004_alter_account_routing_number")]
    migrate_to = [("financial", "0005_household_account_household_transaction_household_and_more")]

    def setUp(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        apps = self.executor.loader.project_state(self.migrate_from).apps

        User = apps.get_model("auth", "User")
        Account = apps.get_model("financial", "Account")
        Transaction = apps.get_model("financial", "Transaction")

        user = User.objects.create_user("migrate-user", "migrate@example.com", "pass-1234")
        account = Account.objects.create(
            user=user,
            name="Legacy Checking",
            institution="Legacy Bank",
            account_type="checking",
            status="active",
            current_balance=Decimal("250.00"),
        )
        self.transaction_id = Transaction.objects.create(
            account=account,
            posted_on=date(2026, 2, 12),
            description="Legacy txn",
            transaction_type="expense",
            amount=Decimal("5.00"),
        ).id

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        self.apps = self.executor.loader.project_state(self.migrate_to).apps

    def test_household_backfill_assigns_account_and_transaction_scope(self):
        Household = self.apps.get_model("financial", "Household")
        HouseholdMember = self.apps.get_model("financial", "HouseholdMember")
        Account = self.apps.get_model("financial", "Account")
        Transaction = self.apps.get_model("financial", "Transaction")

        self.assertEqual(Household.objects.count(), 1)
        self.assertEqual(HouseholdMember.objects.count(), 1)

        account = Account.objects.get(name="Legacy Checking")
        transaction = Transaction.objects.get(id=self.transaction_id)
        self.assertIsNotNone(account.household_id)
        self.assertEqual(transaction.household_id, account.household_id)
