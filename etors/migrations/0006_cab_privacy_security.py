import uuid

from django.db import migrations, models
from django.utils import timezone


def initialize_existing_cab_security(apps, schema_editor):
    CabBooking = apps.get_model("etors", "CabBooking")
    for cab in CabBooking.objects.filter(dispatch_token__isnull=True):
        cab.dispatch_token = uuid.uuid4()
        cab.pickup_otp_hash = "!expired-existing-booking"
        cab.pickup_otp_expires_at = timezone.now()
        cab.save(update_fields=["dispatch_token", "pickup_otp_hash", "pickup_otp_expires_at"])


class Migration(migrations.Migration):
    dependencies = [("etors", "0005_alter_booking_travel_class")]

    operations = [
        migrations.AddField(
            model_name="cabbooking",
            name="dispatch_token",
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="cabbooking",
            name="pickup_otp_expires_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="cabbooking",
            name="pickup_otp_hash",
            field=models.CharField(default="", editable=False, max_length=128),
        ),
        migrations.AddField(
            model_name="cabbooking",
            name="pickup_verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(initialize_existing_cab_security, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="cabbooking",
            name="dispatch_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="cabbooking",
            name="pickup_otp_expires_at",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="cabbooking",
            name="pickup_otp_hash",
            field=models.CharField(editable=False, max_length=128),
        ),
    ]
