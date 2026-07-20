from django.db import migrations
from django.contrib.auth.models import User


def update_cse_student_passwords(apps, schema_editor):
    Department = apps.get_model('student', 'Department')
    Student = apps.get_model('student', 'Student')

    dept, _ = Department.objects.get_or_create(name='CSE')

    for i in range(6601, 6666):
        username = f'25C11A{i}'
        password = str(i)

        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            continue

        Student.objects.get_or_create(
            student_id_id=user.id,
            defaults={
                'first_name': 'Student',
                'last_name': str(i),
                'department': dept,
            }
        )


class Migration(migrations.Migration):
    dependencies = [
        ('student', '0002_create_cse_students'),
    ]

    operations = [
        migrations.RunPython(update_cse_student_passwords),
    ]
