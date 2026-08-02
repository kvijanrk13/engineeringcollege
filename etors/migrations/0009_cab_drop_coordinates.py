from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("etors", "0008_expand_cab_vehicle_types")]

    operations = [
        migrations.AddField(
            model_name="cabbooking",
            name="drop_latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="cabbooking",
            name="drop_longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
