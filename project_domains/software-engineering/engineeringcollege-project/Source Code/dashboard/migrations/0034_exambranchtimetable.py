from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('dashboard', '0033_suspiciousactivity')]

    operations = [
        migrations.CreateModel(
            name='ExamBranchTimetable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program', models.CharField(default='B.Tech', max_length=80)),
                ('branch', models.CharField(max_length=40)),
                ('year', models.CharField(max_length=10)),
                ('semester', models.CharField(max_length=10)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['branch', 'year', 'semester']},
        ),
        migrations.AddConstraint(
            model_name='exambranchtimetable',
            constraint=models.UniqueConstraint(fields=('program', 'branch', 'year', 'semester'), name='unique_exam_branch_timetable'),
        ),
    ]
