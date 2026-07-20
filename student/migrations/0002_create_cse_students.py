from django.db import migrations


def create_cse_students(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Department = apps.get_model('student', 'Department')
    Student = apps.get_model('student', 'Student')

    dept, _ = Department.objects.get_or_create(name='CSE')

    for i in range(6601, 6666):
        username = f'25C11A{i}'
        password = str(i)

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@anurag.ac.in',
                'first_name': 'Student',
                'last_name': str(i),
                'is_staff': False,
                'is_active': True,
            }
        )

        user.set_password(password)
        user.save()

        Student.objects.get_or_create(
            student_id=user,
            defaults={
                'first_name': 'Student',
                'last_name': str(i),
                'department': dept,
            }
        )


class Migration(migrations.Migration):
    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_cse_students),
    ]
