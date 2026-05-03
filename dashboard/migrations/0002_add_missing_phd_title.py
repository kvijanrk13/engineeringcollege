from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='phd_title',
            field=models.CharField(max_length=500, blank=True, null=True),
        ),
    ]