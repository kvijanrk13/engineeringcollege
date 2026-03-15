# dashboard/migrations/0014_faculty_caste_subcaste_nationality.py
# ============================================================
# ONLY adds the 3 fields that are missing from the Faculty model.
# jntuh_id, aicte_id, orcid_id, apaar_id, ssc_year, inter_year,
# ug_degree, pg_degree, phd_degree etc. already exist in the DB.
# ============================================================

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_faculty_extra_fields'),  # your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='caste',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='faculty',
            name='sub_caste',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='faculty',
            name='nationality',
            field=models.CharField(blank=True, default='Indian', max_length=100, null=True),
        ),
    ]