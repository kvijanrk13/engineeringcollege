import secrets
import string
import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Station(models.Model):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=80)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Train(models.Model):
    number = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=120)
    source = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="departing_trains"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="arriving_trains"
    )
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration = models.CharField(max_length=30)
    running_days = models.CharField(
        max_length=20,
        default="Daily",
        help_text="Display value such as Daily or Mon, Wed, Fri",
    )
    seat_capacity = models.PositiveIntegerField(default=120)
    sleeper_fare = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(1)]
    )
    ac_fare = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(1)]
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("departure_time", "number")

    def __str__(self):
        return f"{self.number} - {self.name}"


class Booking(models.Model):
    CLASS_CHOICES = (
        ("GN", "General"),
        ("SL", "Sleeper"),
        ("1A", "AC First Class (1A)"),
        ("2A", "AC 2 Tier (2A)"),
        ("3A", "AC 3 Tier (3A)"),
        ("3E", "AC 3 Economy (3E)"),
    )
    STATUS_CHOICES = (("CONFIRMED", "Confirmed"), ("CANCELLED", "Cancelled"))

    pnr = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="etors_bookings",
    )
    train = models.ForeignKey(Train, on_delete=models.PROTECT, related_name="bookings")
    journey_date = models.DateField()
    travel_class = models.CharField(max_length=2, choices=CLASS_CHOICES)
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    train_insurance_policy = models.CharField(max_length=24, blank=True)
    train_insurance_premium = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default="CONFIRMED"
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-booked_at",)

    def save(self, *args, **kwargs):
        if not self.pnr:
            alphabet = string.digits
            while True:
                candidate = "".join(secrets.choice(alphabet) for _ in range(10))
                if not Booking.objects.filter(pnr=candidate).exists():
                    self.pnr = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PNR {self.pnr} - {self.train.number}"


class Passenger(models.Model):
    GENDER_CHOICES = (("M", "Male"), ("F", "Female"), ("O", "Other"))

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="passengers"
    )
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    berth_preference = models.CharField(max_length=30, blank=True)
    seat_number = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.name} - {self.seat_number}"


class CabBooking(models.Model):
    CAB_CHOICES = (
        ("BIKE", "Bike (1 passenger)"),
        ("AUTO", "Auto Rickshaw (3 passengers)"),
        ("MINI", "Mini (4 passengers)"),
        ("SEDAN", "Sedan (4 passengers)"),
        ("SUV", "SUV (6 passengers)"),
        ("TEMPO", "Tempo Traveller (12 passengers)"),
        ("BUS", "Bus (30 passengers)"),
    )
    STATUS_CHOICES = (
        ("SCHEDULED", "Scheduled"),
        ("ARRIVED", "Arrived at station"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="cab_booking",
    )
    reference = models.CharField(max_length=12, unique=True, editable=False)
    dispatch_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pickup_otp_hash = models.CharField(max_length=128, editable=False)
    pickup_otp_expires_at = models.DateTimeField()
    pickup_verified_at = models.DateTimeField(null=True, blank=True)
    cab_type = models.CharField(max_length=8, choices=CAB_CHOICES)
    pickup_station = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name="cab_pickups",
    )
    drop_address = models.CharField(max_length=240)
    train_arrival_at = models.DateTimeField()
    cab_arrival_at = models.DateTimeField()
    fare = models.DecimalField(max_digits=8, decimal_places=2)
    cab_insurance_policy = models.CharField(max_length=24, blank=True)
    cab_insurance_premium = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20)
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default="SCHEDULED",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("cab_arrival_at",)

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                candidate = "CAB" + "".join(secrets.choice(string.digits) for _ in range(7))
                if not CabBooking.objects.filter(reference=candidate).exists():
                    self.reference = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Private cab dispatch {self.reference}"
