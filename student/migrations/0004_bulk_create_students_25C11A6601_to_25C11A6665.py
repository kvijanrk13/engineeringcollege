from django.db import migrations
from django.contrib.auth.models import User


def update_student_passwords(apps, schema_editor):
    Department = apps.get_model('student', 'Department')
    Student = apps.get_model('student', 'Student')

    dept, _ = Department.objects.get_or_create(name='CSE')

    for i in range(6601, 6666):
        username = f'25C11A{i}'
        password = username

        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name='Student',
                last_name=str(i),
            )
            Student.objects.get_or_create(
                student_id=user,
                defaults={
                    'first_name': 'Student',
                    'last_name': str(i),
                    'department': dept,
                }
            )

    librarian_user, _ = User.objects.get_or_create(
        username='anrklibrary',
        defaults={
            'is_superuser': True,
            'is_staff': True,
            'is_active': True,
        }
    )
    librarian_user.set_password('anrklibrary')
    librarian_user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_update_cse_passwords'),
    ]

    operations = [
        migrations.RunPython(update_student_passwords),
    ]
