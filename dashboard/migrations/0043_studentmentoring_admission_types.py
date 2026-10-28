from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0042_studentmentoring_semester_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmentoring',
            name='readmitted_student',
            field=models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='', max_length=3),
        ),
        migrations.AddField(
            model_name='studentmentoring',
            name='lateral_entry_student',
            field=models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='', max_length=3),
        ),
    ]
