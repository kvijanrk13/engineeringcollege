from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Count, Q
from django.utils import timezone

from .models import CabBooking


CAB_FARES = {
    "MINI": Decimal("350.00"),
    "SEDAN": Decimal("500.00"),
    "SUV": Decimal("750.00"),
}

DUMMY_CABS = (
    ("Ravi Kumar", "9876501001", "TS 09 ET 2401"),
    ("Sana Begum", "9876501002", "AP 16 ET 5182"),
    ("Arjun Reddy", "9876501003", "TS 08 ET 7306"),
)


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
    return train.ac_fare if travel_class == "3A" else train.sleeper_fare


def cab_fare_for(cab_type):
    return CAB_FARES.get(cab_type, Decimal("0.00"))


def cab_schedule_for(train, journey_date):
    departure_at = datetime.combine(journey_date, train.departure_time)
    arrival_at = datetime.combine(journey_date, train.arrival_time)
    if arrival_at <= departure_at:
        arrival_at += timedelta(days=1)
    train_arrival_at = timezone.make_aware(arrival_at)
    return train_arrival_at, train_arrival_at - timedelta(minutes=20)


def create_cab_booking(booking, cab_type, drop_address):
    train_arrival_at, cab_arrival_at = cab_schedule_for(
        booking.train,
        booking.journey_date,
    )
    driver_name, driver_phone, vehicle_number = DUMMY_CABS[
        int(booking.pnr[-2:]) % len(DUMMY_CABS)
    ]
    return CabBooking.objects.create(
        booking=booking,
        cab_type=cab_type,
        pickup_station=booking.train.destination,
        drop_address=drop_address,
        train_arrival_at=train_arrival_at,
        cab_arrival_at=cab_arrival_at,
        fare=cab_fare_for(cab_type),
        driver_name=driver_name,
        driver_phone=driver_phone,
        vehicle_number=vehicle_number,
    )


def seat_number(train, journey_date):
    available = train_availability(train, journey_date)
    allocated = train.seat_capacity - available + 1
    return f"S{allocated:03d}"


def format_currency(value):
    return f"₹{Decimal(value):,.2f}"
