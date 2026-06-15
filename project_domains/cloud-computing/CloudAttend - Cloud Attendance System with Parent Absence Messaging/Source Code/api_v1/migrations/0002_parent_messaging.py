from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ParentContact',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_name', models.CharField(max_length=160)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('preferred_channel', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp')], default='email', max_length=20)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent_contact', to='api_v1.student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParentNotification',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(max_length=20)),
                ('recipient', models.CharField(max_length=160)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Sent', 'Sent'), ('Failed', 'Failed'), ('Acknowledged', 'Acknowledged')], default='Pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('acknowledgement_reason', models.CharField(blank=True, max_length=120)),
                ('acknowledgement_note', models.TextField(blank=True)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_notifications', to='api_v1.attendance')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_parent_notifications', to=settings.AUTH_USER_MODEL)),
                ('parent_contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='api_v1.parentcontact')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
