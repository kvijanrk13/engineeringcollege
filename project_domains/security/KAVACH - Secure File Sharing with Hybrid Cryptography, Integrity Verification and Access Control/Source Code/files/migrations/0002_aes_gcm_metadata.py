# Generated for KAVACH Step 4: AES-GCM encrypted file storage

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plaintextfile",
            name="uploaded_file",
            field=models.FileField(upload_to="encrypted_files/"),
        ),
        migrations.AddField(
            model_name="plaintextfile",
            name="aes_key",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="plaintextfile",
            name="aes_nonce",
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name="plaintextfile",
            name="encryption_algorithm",
            field=models.CharField(default="AES-GCM", max_length=20),
        ),
    ]
