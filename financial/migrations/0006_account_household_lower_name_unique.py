from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ("financial", "0005_monthly_bill_payment_funding_account"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="account",
            name="financial_account_user_lower_name_unique",
        ),
        migrations.AddConstraint(
            model_name="account",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                models.F("household"),
                name="financial_account_household_lower_name_unique",
            ),
        ),
    ]
