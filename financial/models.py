import uuid
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, IntegerField, When
from django.db.models.functions import Lower


ROUTING_NUMBER_VALIDATOR = RegexValidator(
	regex=r"^\d{0,9}$",
	message="Enter the routing number digits only.",
)


class AccountType(models.TextChoices):
	CHECKING = "checking", "Checking"
	SAVINGS = "savings", "Savings"
	CREDIT_CARD = "credit_card", "Credit Card"
	LOAN = "loan", "Loan"
	OTHER = "other", "Other"


class AccountStatus(models.TextChoices):
	ACTIVE = "active", "Active"
	CLOSED = "closed", "Closed"
	PENDING = "pending", "Pending"


class TransactionDirection(models.TextChoices):
	DEBIT = "debit", "Debit"
	CREDIT = "credit", "Credit"


class TransactionType(models.TextChoices):
	DEPOSIT = "deposit", "Deposit"
	EXPENSE = "expense", "Expense"
	TRANSFER = "transfer", "Transfer"
	ADJUSTMENT = "adjustment", "Adjustment"
	PAYMENT = "payment", "Payment"
	CHARGE = "charge", "Charge"

	@classmethod
	def allowed_values_for_account(cls, account_type: str) -> list[str]:
		allowed_map = {
			AccountType.CHECKING: [
				cls.DEPOSIT,
				cls.EXPENSE,
				cls.TRANSFER,
				cls.ADJUSTMENT,
			],
			AccountType.SAVINGS: [
				cls.DEPOSIT,
				cls.EXPENSE,
				cls.TRANSFER,
				cls.ADJUSTMENT,
			],
			AccountType.CREDIT_CARD: [
				cls.PAYMENT,
				cls.CHARGE,
				cls.ADJUSTMENT,
			],
			AccountType.LOAN: [
				cls.PAYMENT,
				cls.CHARGE,
				cls.ADJUSTMENT,
			],
			AccountType.OTHER: [
				cls.PAYMENT,
				cls.CHARGE,
				cls.ADJUSTMENT,
			],
		}
		return [value for value in allowed_map.get(account_type, [])]

	@classmethod
	def allowed_for_account(cls, account_type: str) -> list[tuple[str, str]]:
		allowed_values = set(cls.allowed_values_for_account(account_type))
		return [(value, label) for value, label in cls.choices if value in allowed_values]


class AccountQuerySet(models.QuerySet):
	"""Reusable queryset helpers for deterministic ordering and scoping."""

	def with_account_type_order(self):
		"""Annotate a numeric weight for ordering account types."""

		order_map = [
			(AccountType.CHECKING, 0),
			(AccountType.SAVINGS, 1),
			(AccountType.CREDIT_CARD, 2),
			(AccountType.LOAN, 3),
			(AccountType.OTHER, 4),
		]
		whens = [When(account_type=value, then=rank) for value, rank in order_map]
		return self.annotate(
			_account_type_order=Case(
				*whens,
				default=len(order_map),
				output_field=IntegerField(),
			)
		)

	def ordered(self) -> "AccountQuerySet":
		return self.with_account_type_order().order_by("_account_type_order", "name", "created_at")

	def for_user(self, user) -> "AccountQuerySet":
		if user is None or not getattr(user, "is_authenticated", False):
			return self.none()
		return self.ordered().filter(user=user)


class UserAccountQuerysetMixin:
	"""Mixin for class-based views that should scope Accounts to request.user."""

	def get_queryset(self):  # pragma: no cover - CBV glue
		base_qs = super().get_queryset()
		return base_qs.for_user(self.request.user)


AccountManager = models.Manager.from_queryset(AccountQuerySet)


class Account(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name="accounts",
		on_delete=models.CASCADE,
	)
	name = models.CharField(max_length=255)
	institution = models.CharField(max_length=255, blank=True)
	account_type = models.CharField(max_length=20, choices=AccountType.choices)
	account_number = models.CharField(max_length=64, blank=True, null=True)
	routing_number = models.CharField(
		max_length=9,
		blank=True,
		null=True,
		validators=[ROUTING_NUMBER_VALIDATOR],
	)
	interest_rate = models.DecimalField(
		max_digits=6,
		decimal_places=3,
		blank=True,
		null=True,
	)
	status = models.CharField(
		max_length=20,
		choices=AccountStatus.choices,
		default=AccountStatus.ACTIVE,
	)
	current_balance = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		default=Decimal("0.00"),
	)
	credit_limit_or_principal = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		blank=True,
		null=True,
	)
	statement_close_date = models.DateField(blank=True, null=True)
	payment_due_day = models.PositiveSmallIntegerField(blank=True, null=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = AccountManager()

	class Meta:
		ordering = ("account_type", "name", "created_at")
		constraints = [
			models.UniqueConstraint(
				Lower("name"),
				"user",
				name="financial_account_user_lower_name_unique",
			)
		]

	def clean(self):
		super().clean()
		if not self.account_type:
			return

		routing_allowed = {AccountType.CHECKING, AccountType.SAVINGS}
		interest_allowed = {AccountType.CREDIT_CARD, AccountType.LOAN, AccountType.OTHER}

		if self.account_type in routing_allowed:
			if self.routing_number == "":
				self.routing_number = None
		else:
			if self.routing_number:
				raise ValidationError({"routing_number": "Routing numbers are only for checking or savings accounts."})
			self.routing_number = None

		if self.account_type in interest_allowed:
			pass
		else:
			if self.interest_rate is not None:
				raise ValidationError({"interest_rate": "Interest rates are only for credit or loan accounts."})
			self.interest_rate = None
		if self.payment_due_day is not None:
			if not 1 <= self.payment_due_day <= 31:
				raise ValidationError({"payment_due_day": "Day must be between 1 and 31."})

	def __str__(self):
		return f"{self.name} ({self.get_account_type_display()})"


class TransactionQuerySet(models.QuerySet):
	"""Reusable queryset helpers for deterministic transaction ordering."""

	def ordered(self) -> "TransactionQuerySet":
		return self.order_by("-posted_on", "-created_at", "-id")

	def for_account(self, account) -> "TransactionQuerySet":
		if account is None:
			return self.none()
		return self.filter(account=account)


TransactionManager = models.Manager.from_queryset(TransactionQuerySet)


class Transaction(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	account = models.ForeignKey(
		Account,
		related_name="transactions",
		on_delete=models.CASCADE,
	)
	posted_on = models.DateField()
	description = models.CharField(max_length=255)
	transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	category = models.ForeignKey(
		"Category",
		related_name="transactions",
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
	)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	objects = TransactionManager()

	class Meta:
		ordering = ("-posted_on", "-created_at", "-id")
		indexes = [
			models.Index(
				fields=["account", "posted_on", "created_at", "id"],
				name="fin_txn_acct_posted_created_id",
			),
		]

	def clean(self):
		super().clean()
		if self.account is None or not self.transaction_type:
			return

		allowed = TransactionType.allowed_values_for_account(self.account.account_type)
		if self.transaction_type not in allowed:
			raise ValidationError({
				"transaction_type": "This transaction type is not allowed for the account.",
			})

		if self.amount is None:
			return
		if self.amount <= Decimal("0"):
			raise ValidationError({"amount": "Amount must be greater than 0."})

		sign_map = {
			AccountType.CHECKING: {
				TransactionType.DEPOSIT: Decimal("1"),
				TransactionType.EXPENSE: Decimal("-1"),
				TransactionType.TRANSFER: Decimal("-1"),
				TransactionType.ADJUSTMENT: Decimal("1"),
			},
			AccountType.SAVINGS: {
				TransactionType.DEPOSIT: Decimal("1"),
				TransactionType.EXPENSE: Decimal("-1"),
				TransactionType.TRANSFER: Decimal("-1"),
				TransactionType.ADJUSTMENT: Decimal("1"),
			},
			AccountType.CREDIT_CARD: {
				TransactionType.PAYMENT: Decimal("-1"),
				TransactionType.CHARGE: Decimal("1"),
				TransactionType.ADJUSTMENT: Decimal("-1"),
			},
			AccountType.LOAN: {
				TransactionType.PAYMENT: Decimal("-1"),
				TransactionType.CHARGE: Decimal("1"),
				TransactionType.ADJUSTMENT: Decimal("-1"),
			},
			AccountType.OTHER: {
				TransactionType.PAYMENT: Decimal("-1"),
				TransactionType.CHARGE: Decimal("1"),
				TransactionType.ADJUSTMENT: Decimal("-1"),
			},
		}
		sign = sign_map[self.account.account_type][self.transaction_type]
		self.amount = abs(self.amount) * sign

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)


class Category(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name="transaction_categories",
		on_delete=models.CASCADE,
	)
	name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				Lower("name"),
				"user",
				name="financial_category_user_lower_name_unique",
			)
		]

	def __str__(self):
		return self.name
