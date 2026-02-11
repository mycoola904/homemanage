import uuid
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Case, IntegerField, When
from django.db.models.functions import Lower


LAST4_VALIDATOR = RegexValidator(
	regex=r"^\d{0,4}$",
	message="Enter the last four digits or leave this field blank.",
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
	number_last4 = models.CharField(max_length=4, blank=True, validators=[LAST4_VALIDATOR])
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
		if self.payment_due_day is not None:
			if not 1 <= self.payment_due_day <= 31:
				raise ValidationError({"payment_due_day": "Day must be between 1 and 31."})

	def __str__(self):
		return f"{self.name} ({self.get_account_type_display()})"
