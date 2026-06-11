from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_projectdownloadpayment_project_identity'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='admin_note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='payment_method',
            field=models.CharField(
                choices=[('PHONEPE', 'PhonePe Gateway'), ('RECEIPT', 'Manual Receipt')],
                default='PHONEPE',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='receipt_filename',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='receipt_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='receipt_student_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='receipt_student_name',
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='receipt_student_phone',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='receipt_uploaded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
