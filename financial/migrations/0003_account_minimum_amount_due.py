from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("financial", "0002_account_online_access_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="minimum_amount_due",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]