from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0024_projectdownloadpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='domain_slug',
            field=models.SlugField(default='software-engineering', max_length=80),
        ),
        migrations.AddField(
            model_name='projectdownloadpayment',
            name='project_slug',
            field=models.SlugField(default='engineeringcollege-project', max_length=120),
        ),
    ]
