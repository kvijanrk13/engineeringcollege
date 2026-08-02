from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("etors", "0007_booking_and_cab_insurance")]

    operations = [
        migrations.AlterField(
            model_name="cabbooking",
            name="cab_type",
            field=models.CharField(
                choices=[
                    ("BIKE", "Bike (1 passenger)"),
                    ("AUTO", "Auto Rickshaw (3 passengers)"),
                    ("MINI", "Mini (4 passengers)"),
                    ("SEDAN", "Sedan (4 passengers)"),
                    ("SUV", "SUV (6 passengers)"),
                    ("TEMPO", "Tempo Traveller (12 passengers)"),
                    ("BUS", "Bus (30 passengers)"),
                ],
                max_length=8,
            ),
        ),
    ]
