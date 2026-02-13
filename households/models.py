import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Household(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, unique=True, blank=True)
	is_archived = models.BooleanField(default=False)
	timezone = models.CharField(max_length=64, blank=True)
	currency_code = models.CharField(max_length=3, default="USD")
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name="created_households",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("name", "created_at")

	def __str__(self):
		return self.name


class HouseholdMember(models.Model):
	class Role(models.TextChoices):
		OWNER = "owner", "Owner"
		ADMIN = "admin", "Admin"
		MEMBER = "member", "Member"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	household = models.ForeignKey(
		Household,
		related_name="memberships",
		on_delete=models.CASCADE,
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name="household_memberships",
		on_delete=models.CASCADE,
	)
	role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
	is_primary = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["household", "user"], name="financial_householdmember_unique_household_user"),
			models.UniqueConstraint(
				fields=["user"],
				condition=Q(is_primary=True),
				name="financial_householdmember_user_single_primary",
			),
		]

	def clean(self):
		super().clean()
		if self.role != self.Role.OWNER and self.pk:
			owner_count = HouseholdMember.objects.filter(household=self.household, role=self.Role.OWNER).exclude(pk=self.pk).count()
			if owner_count == 0:
				raise ValidationError({"role": "A household must retain at least one owner."})

	def delete(self, *args, **kwargs):
		if self.role == self.Role.OWNER:
			owner_count = HouseholdMember.objects.filter(household=self.household, role=self.Role.OWNER).exclude(pk=self.pk).count()
			if owner_count == 0:
				raise ValidationError({"role": "A household must retain at least one owner."})
		return super().delete(*args, **kwargs)

	def __str__(self):
		return f"{self.user} @ {self.household}"
