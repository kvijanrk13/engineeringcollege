from decimal import Decimal

from django.db import migrations, models
from django.utils import timezone


def preserve_existing_cab_payments(apps, schema_editor):
    CabBooking = apps.get_model("etors", "CabBooking")
    CabBooking.objects.all().update(payment_status="PAID_UPI", payment_method="UPI")


class Migration(migrations.Migration):
    dependencies = [("etors", "0009_cab_drop_coordinates")]

    operations = [
        migrations.AddField(model_name="cabbooking", name="payment_deadline", field=models.DateTimeField(default=timezone.now), preserve_default=False),
        migrations.AddField(model_name="cabbooking", name="payment_status", field=models.CharField(choices=[("PENDING", "Awaiting pickup OTP and UPI payment"), ("PAID_UPI", "Paid by dummy UPI"), ("DRIVER_DEDUCTION", "Deducted from driver salary"), ("CANCELLED", "Payment cancelled")], default="PENDING", max_length=20)),
        migrations.AddField(model_name="cabbooking", name="payment_method", field=models.CharField(blank=True, max_length=8)),
        migrations.AddField(model_name="cabbooking", name="paid_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="cabbooking", name="driver_salary_deduction", field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=8)),
        migrations.RunPython(preserve_existing_cab_payments, migrations.RunPython.noop),
    ]
