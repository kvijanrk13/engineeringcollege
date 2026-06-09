from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0026_projectdownloadpayment_receipt_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='delivery_drive_link',
            field=models.URLField(blank=True, max_length=1000),
        ),
    ]
