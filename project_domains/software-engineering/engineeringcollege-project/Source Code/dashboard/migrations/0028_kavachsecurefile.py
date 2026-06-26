from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0027_projectdownloadpayment_delivery_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='KavachSecureFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_id', models.CharField(db_index=True, max_length=24, unique=True)),
                ('sender_name', models.CharField(blank=True, max_length=120)),
                ('receiver_name', models.CharField(blank=True, max_length=120)),
                ('original_filename', models.CharField(max_length=255)),
                ('encrypted_file', models.FileField(upload_to='kavach/encrypted/')),
                ('file_size', models.PositiveIntegerField(default=0)),
                ('content_type', models.CharField(blank=True, max_length=120)),
                ('aes_key', models.CharField(max_length=64)),
                ('aes_nonce', models.CharField(max_length=32)),
                ('access_code_hash', models.CharField(db_index=True, max_length=64)),
                ('encryption_algorithm', models.CharField(default='AES-GCM', max_length=20)),
                ('download_count', models.PositiveIntegerField(default=0)),
                ('last_downloaded_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
