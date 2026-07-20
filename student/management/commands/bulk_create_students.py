import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import Student, Department


class Command(BaseCommand):
    help = 'Bulk create/reset student users from 25C11A6601 to 25C11A6665'

    def handle(self, *args, **options):
        department, _ = Department.objects.get_or_create(name='CSE')
        created_users = 0
        updated_users = 0
        existing_users = 0

        for i in range(6601, 6666):
            username = f'25C11A{i}'
            password = username
            first_name = f'Student'
            last_name = str(i)

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )

            if created:
                user.set_password(password)
                user.save()
                Student.objects.get_or_create(
                    student_id=user,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'department': department,
                    }
                )
                created_users += 1
            else:
                user.set_password(password)
                user.save()
                Student.objects.update_or_create(
                    student_id=user,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'department': department,
                    }
                )
                updated_users += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_users} student users'))
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_users} student users'))
