from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("etors", "0006_cab_privacy_security")]

    operations = [
        migrations.AddField(model_name="booking", name="train_insurance_policy", field=models.CharField(blank=True, max_length=24)),
        migrations.AddField(model_name="booking", name="train_insurance_premium", field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=8)),
        migrations.AddField(model_name="cabbooking", name="cab_insurance_policy", field=models.CharField(blank=True, max_length=24)),
        migrations.AddField(model_name="cabbooking", name="cab_insurance_premium", field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=8)),
    ]
