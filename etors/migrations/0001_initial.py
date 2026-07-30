import django.core.validators
import django.db.models.deletion
from decimal import Decimal

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Station",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=8, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("city", models.CharField(max_length=80)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Train",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=6, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("departure_time", models.TimeField()),
                ("arrival_time", models.TimeField()),
                ("duration", models.CharField(max_length=30)),
                ("running_days", models.CharField(default="Daily", help_text="Display value such as Daily or Mon, Wed, Fri", max_length=20)),
                ("seat_capacity", models.PositiveIntegerField(default=120)),
                ("sleeper_fare", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(1)])),
                ("ac_fare", models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(1)])),
                ("active", models.BooleanField(default=True)),
                ("destination", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="arriving_trains", to="etors.station")),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="departing_trains", to="etors.station")),
            ],
            options={"ordering": ("departure_time", "number")},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pnr", models.CharField(editable=False, max_length=10, unique=True)),
                ("journey_date", models.DateField()),
                ("travel_class", models.CharField(choices=[("SL", "Sleeper"), ("3A", "AC 3 Tier")], max_length=2)),
                ("contact_name", models.CharField(max_length=100)),
                ("contact_email", models.EmailField(max_length=254)),
                ("contact_phone", models.CharField(max_length=15)),
                ("total_fare", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("CONFIRMED", "Confirmed"), ("CANCELLED", "Cancelled")], default="CONFIRMED", max_length=12)),
                ("booked_at", models.DateTimeField(auto_now_add=True)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
                ("train", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="etors.train")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="etors_bookings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-booked_at",)},
        ),
        migrations.CreateModel(
            name="Passenger",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("age", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("gender", models.CharField(choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], max_length=1)),
                ("berth_preference", models.CharField(blank=True, max_length=30)),
                ("seat_number", models.CharField(max_length=12)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="passengers", to="etors.booking")),
            ],
        ),
    ]
