# dashboard/migrations/0016_fix_pdf_url_final.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0013_student_pdf_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='pdf_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]