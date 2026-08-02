from datetime import datetime, timedelta
from decimal import Decimal
import secrets

from django.db.models import Count, Q
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from .models import Booking, CabBooking


CAB_FARES = {
    "BIKE": Decimal("150.00"),
    "AUTO": Decimal("250.00"),
    "MINI": Decimal("350.00"),
    "SEDAN": Decimal("500.00"),
    "SUV": Decimal("750.00"),
    "TEMPO": Decimal("1200.00"),
    "BUS": Decimal("2500.00"),
}
TRAIN_INSURANCE_PER_BERTH = Decimal("0.45")
CAB_INSURANCE_PREMIUM = Decimal("10.00")


def insurance_policy(prefix):
    return prefix + "-" + "".join(secrets.choice("0123456789") for _ in range(12))

DUMMY_CABS = {
    "BIKE": ("Ravi Kumar", "9876501001", "TS 09 BK 2401"),
    "AUTO": ("Sana Begum", "9876501002", "AP 16 AU 5182"),
    "MINI": ("Arjun Reddy", "9876501003", "TS 08 MN 7306"),
    "SEDAN": ("Meera Singh", "9876501004", "AP 16 SD 4420"),
    "SUV": ("Kiran Rao", "9876501005", "TS 09 SV 8861"),
    "TEMPO": ("Imran Ali", "9876501006", "AP 16 TT 1212"),
    "BUS": ("Vijay Sharma", "9876501007", "TS 08 BS 3030"),
}


def train_availability(train, journey_date):
    reserved = (
        train.bookings.filter(
            journey_date=journey_date,
            status="CONFIRMED",
        ).aggregate(
            count=Count("passengers", filter=Q(passengers__isnull=False))
        )["count"]
        or 0
    )
    return max(train.seat_capacity - reserved, 0)


def fare_for(train, travel_class):
    multipliers = {
        "GN": (train.sleeper_fare, Decimal("0.60")),
        "SL": (train.sleeper_fare, Decimal("1.00")),
        "3E": (train.ac_fare, Decimal("0.90")),
        "3A": (train.ac_fare, Decimal("1.00")),
        "2A": (train.ac_fare, Decimal("1.40")),
        "1A": (train.ac_fare, Decimal("2.00")),
    }
    base_fare, multiplier = multipliers.get(
        travel_class, (train.sleeper_fare, Decimal("1.00"))
    )
    return (base_fare * multiplier).quantize(Decimal("0.01"))


def fare_options_for(train):
    return [
        (label, fare_for(train, code))
        for code, label in Booking.CLASS_CHOICES
    ]


def cab_fare_for(cab_type):
    return CAB_FARES.get(cab_type, Decimal("0.00"))


def cab_schedule_for(train, journey_date):
    departure_at = datetime.combine(journey_date, train.departure_time)
    arrival_at = datetime.combine(journey_date, train.arrival_time)
    if arrival_at <= departure_at:
        arrival_at += timedelta(days=1)
    train_arrival_at = timezone.make_aware(arrival_at)
    return train_arrival_at, train_arrival_at - timedelta(minutes=20)


def create_cab_booking(booking, cab_type, drop_address, drop_latitude=None, drop_longitude=None):
    train_arrival_at, cab_arrival_at = cab_schedule_for(
        booking.train,
        booking.journey_date,
    )
    driver_name, driver_phone, vehicle_number = DUMMY_CABS[cab_type]
    pickup_otp = "".join(secrets.choice("0123456789") for _ in range(6))
    cab_booking = CabBooking.objects.create(
        booking=booking,
        cab_type=cab_type,
        pickup_station=booking.train.destination,
        drop_address=drop_address,
        drop_latitude=drop_latitude or None,
        drop_longitude=drop_longitude or None,
        train_arrival_at=train_arrival_at,
        cab_arrival_at=cab_arrival_at,
        fare=cab_fare_for(cab_type),
        cab_insurance_policy=insurance_policy("CABINS"),
        cab_insurance_premium=CAB_INSURANCE_PREMIUM,
        driver_name=driver_name,
        driver_phone=driver_phone,
        vehicle_number=vehicle_number,
        pickup_otp_hash=make_password(pickup_otp),
        pickup_otp_expires_at=train_arrival_at + timedelta(hours=2),
        payment_deadline=train_arrival_at + timedelta(minutes=30),
    )
    cab_booking.pickup_otp = pickup_otp
    return cab_booking


def cab_amount_due(cab):
    return cab.fare + cab.cab_insurance_premium


def reconcile_cab_payment(cab):
    if cab.payment_status == "PENDING" and timezone.now() > cab.payment_deadline:
        cab.payment_status = "DRIVER_DEDUCTION"
        cab.driver_salary_deduction = cab_amount_due(cab)
        cab.save(update_fields=["payment_status", "driver_salary_deduction"])
    return cab


def seat_number(train, journey_date):
    available = train_availability(train, journey_date)
    allocated = train.seat_capacity - available + 1
    return f"S{allocated:03d}"


def format_currency(value):
    return f"₹{Decimal(value):,.2f}"
