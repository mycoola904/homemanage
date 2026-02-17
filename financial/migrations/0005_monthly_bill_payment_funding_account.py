from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("financial", "0004_monthly_bill_payment"),
    ]

    operations = [
        migrations.AddField(
            model_name="monthlybillpayment",
            name="funding_account",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="funded_monthly_bill_payments",
                to="financial.account",
            ),
        ),
    ]
