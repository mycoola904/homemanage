from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("financial", "0003_account_minimum_amount_due"),
    ]

    operations = [
        migrations.CreateModel(
            name="MonthlyBillPayment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("month", models.DateField()),
                ("actual_payment_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("paid", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="monthly_bill_payments",
                        to="financial.account",
                    ),
                ),
            ],
            options={
                "ordering": ("month", "account_id"),
                "indexes": [models.Index(fields=["month", "account"], name="fin_billpay_month_account_idx")],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("account", "month"),
                        name="financial_monthly_bill_payment_account_month_unique",
                    )
                ],
            },
        ),
    ]
