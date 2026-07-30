from datetime import time
from decimal import Decimal

from django.db import migrations


STATIONS = [
    ("SC", "Secunderabad Junction", "Hyderabad"),
    ("NDLS", "New Delhi", "New Delhi"),
    ("BZA", "Vijayawada Junction", "Vijayawada"),
    ("MAS", "MGR Chennai Central", "Chennai"),
    ("SBC", "KSR Bengaluru City", "Bengaluru"),
    ("VSKP", "Visakhapatnam Junction", "Visakhapatnam"),
]

TRAINS = [
    ("12723", "Telangana Express", "SC", "NDLS", time(6, 25), time(7, 40), "25h 15m", Decimal("650"), Decimal("1780")),
    ("12724", "Telangana Express", "NDLS", "SC", time(16, 0), time(17, 10), "25h 10m", Decimal("650"), Decimal("1780")),
    ("12760", "Charminar Express", "SC", "MAS", time(18, 0), time(8, 10), "14h 10m", Decimal("440"), Decimal("1190")),
    ("12759", "Charminar Express", "MAS", "SC", time(18, 10), time(8, 20), "14h 10m", Decimal("440"), Decimal("1190")),
    ("12727", "Godavari Express", "VSKP", "SC", time(17, 20), time(5, 45), "12h 25m", Decimal("390"), Decimal("1040")),
    ("12728", "Godavari Express", "SC", "VSKP", time(17, 30), time(5, 50), "12h 20m", Decimal("390"), Decimal("1040")),
    ("12785", "Kacheguda Mysuru Express", "SC", "SBC", time(19, 5), time(8, 0), "12h 55m", Decimal("420"), Decimal("1120")),
    ("12786", "Kacheguda Express", "SBC", "SC", time(14, 20), time(4, 10), "13h 50m", Decimal("420"), Decimal("1120")),
    ("12711", "Pinakini Express", "BZA", "MAS", time(6, 10), time(13, 0), "6h 50m", Decimal("240"), Decimal("690")),
    ("12712", "Pinakini Express", "MAS", "BZA", time(14, 10), time(21, 5), "6h 55m", Decimal("240"), Decimal("690")),
]


def seed_data(apps, schema_editor):
    Station = apps.get_model("etors", "Station")
    Train = apps.get_model("etors", "Train")
    stations = {}
    for code, name, city in STATIONS:
        station, _ = Station.objects.get_or_create(
            code=code, defaults={"name": name, "city": city}
        )
        stations[code] = station
    for number, name, source, destination, departure, arrival, duration, sleeper, ac in TRAINS:
        Train.objects.get_or_create(
            number=number,
            defaults={
                "name": name,
                "source": stations[source],
                "destination": stations[destination],
                "departure_time": departure,
                "arrival_time": arrival,
                "duration": duration,
                "running_days": "Daily",
                "seat_capacity": 120,
                "sleeper_fare": sleeper,
                "ac_fare": ac,
                "active": True,
            },
        )


def remove_seed_data(apps, schema_editor):
    apps.get_model("etors", "Train").objects.filter(
        number__in=[train[0] for train in TRAINS]
    ).delete()
    apps.get_model("etors", "Station").objects.filter(
        code__in=[station[0] for station in STATIONS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("etors", "0001_initial")]
    operations = [migrations.RunPython(seed_data, remove_seed_data)]
