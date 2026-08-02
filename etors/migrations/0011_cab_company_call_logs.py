from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("etors", "0010_deferred_cab_upi_payment")]

    operations = [
        migrations.CreateModel(
            name="CabCallLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(editable=False, max_length=18, unique=True)),
                ("company_number", models.CharField(default="1800 100 200", editable=False, max_length=20)),
                ("recording_reference", models.CharField(editable=False, max_length=24, unique=True)),
                ("status", models.CharField(choices=[("ACTIVE", "Call in progress"), ("COMPLETED", "Call completed")], default="ACTIVE", max_length=12)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("cab_booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="call_logs", to="etors.cabbooking")),
            ],
            options={"ordering": ("-started_at",)},
        ),
    ]
