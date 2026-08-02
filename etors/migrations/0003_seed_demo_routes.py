from datetime import time
from decimal import Decimal

from django.db import migrations


STATIONS = [
    ("KMM", "Khammam", "Khammam"),
    ("BZA", "Vijayawada Junction", "Vijayawada"),
    ("SC", "Secunderabad Junction", "Hyderabad"),
]

# These are deliberately numbered as ETORS demonstration services rather than
# real Indian Railways trains.
TRAINS = [
    ("09001", "Khammam Vijayawada Demo Express", "KMM", "BZA", time(6, 30), time(9, 15), "2h 45m", Decimal("180"), Decimal("480")),
    ("09002", "Vijayawada Khammam Demo Express", "BZA", "KMM", time(17, 0), time(19, 45), "2h 45m", Decimal("180"), Decimal("480")),
    ("09003", "Vijayawada Secunderabad Demo Express", "BZA", "SC", time(6, 0), time(11, 30), "5h 30m", Decimal("260"), Decimal("720")),
    ("09004", "Secunderabad Vijayawada Demo Express", "SC", "BZA", time(14, 30), time(20, 0), "5h 30m", Decimal("260"), Decimal("720")),
    ("09005", "Khammam Secunderabad Demo Express", "KMM", "SC", time(7, 15), time(11, 45), "4h 30m", Decimal("220"), Decimal("620")),
    ("09006", "Secunderabad Khammam Demo Express", "SC", "KMM", time(16, 0), time(20, 30), "4h 30m", Decimal("220"), Decimal("620")),
]


def seed_demo_routes(apps, schema_editor):
    Station = apps.get_model("etors", "Station")
    Train = apps.get_model("etors", "Train")

    stations = {}
    for code, name, city in STATIONS:
        station, _ = Station.objects.update_or_create(
            code=code,
            defaults={"name": name, "city": city},
        )
        stations[code] = station

    for number, name, source, destination, departure, arrival, duration, sleeper, ac in TRAINS:
        Train.objects.update_or_create(
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


class Migration(migrations.Migration):
    dependencies = [("etors", "0002_seed_railway_data")]
    operations = [migrations.RunPython(seed_demo_routes, migrations.RunPython.noop)]
