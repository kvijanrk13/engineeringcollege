from decimal import Decimal

from django.db.models import Count, Q


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


def seat_number(train, journey_date):
    available = train_availability(train, journey_date)
    allocated = train.seat_capacity - available + 1
    return f"S{allocated:03d}"


def format_currency(value):
    return f"₹{Decimal(value):,.2f}"
