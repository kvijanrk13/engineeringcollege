from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("etors", "0004_cabbooking")]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="travel_class",
            field=models.CharField(
                choices=[
                    ("GN", "General"),
                    ("SL", "Sleeper"),
                    ("1A", "AC First Class (1A)"),
                    ("2A", "AC 2 Tier (2A)"),
                    ("3A", "AC 3 Tier (3A)"),
                    ("3E", "AC 3 Economy (3E)"),
                ],
                max_length=2,
            ),
        ),
    ]
