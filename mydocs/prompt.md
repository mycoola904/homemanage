# Build the Bill Pay feature

## Account Model
````python
class Account(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name="accounts",
		on_delete=models.CASCADE,
	)
	household = models.ForeignKey(
		Household,
		related_name="accounts",
		on_delete=models.PROTECT,
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
	minimum_amount_due = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		blank=True,
		null=True,
	)
	online_access_url = models.URLField(blank=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
````

## User Story

The user clicks on Bill Pay in the Sidebar menu.  The Monthly Bill Pay table is displayed in the main content section.  The table is populated with all liability accounts (account_type(s): credit_card, loan, and other) for the month.  Each row shows the account name, institution, payment due day, minimum amount due, online access url. The table is sorted by the due day from smallest to largest.  Included in each row is an editable field to record the actual payment made and a checkbox to record that it was paid.  After a row is edited, the record is saved to the database for that day and month as being paid.