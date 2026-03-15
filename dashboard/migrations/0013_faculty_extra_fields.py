# dashboard/migrations/0013_faculty_extra_fields.py
# ============================================================
# Place at: dashboard/migrations/0013_faculty_extra_fields.py
# This adds ALL missing Faculty model fields in one migration.
# After deploying, Render will run this automatically on startup
# if you have: python manage.py migrate in your build command.
# ============================================================

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_alter_cloudinaryupload_options_and_more'),
    ]

    operations = [

        # ── Professional IDs ──────────────────────────────────────────
        migrations.AddField(
            model_name='faculty',
            name='jntuh_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='faculty',
            name='aicte_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='faculty',
            name='orcid_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='faculty',
            name='apaar_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),

        # ── Personal extras ───────────────────────────────────────────
        migrations.AddField(
            model_name='faculty',
            name='sub_caste',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='faculty',
            name='nationality',
            field=models.CharField(blank=True, default='Indian', max_length=100),
        ),
        migrations.AddField(
            model_name='faculty',
            name='exp_anurag',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='faculty',
            name='exp_other',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]