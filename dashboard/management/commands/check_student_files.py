from django.core.management.base import BaseCommand
from dashboard.models import Student

class Command(BaseCommand):
    help = 'Check student photos and certificates status'

    def handle(self, *args, **options):
        students = Student.objects.all()

        self.stdout.write(f'Total students: {students.count()}\n')

        for student in students:
            self.stdout.write(f'Student: {student.student_name} (ID: {student.id})')

            # Check photo
            if student.photo_url:
                self.stdout.write(f'  Photo URL: {student.photo_url}')
            elif student.photo:
                self.stdout.write(f'  Photo file: {student.photo.url} (exists: {student.photo.path if hasattr(student.photo, "path") else "N/A"})')
            else:
                self.stdout.write('  Photo: None')

            # Check certificates
            certs = []
            cert_fields = [
                ('cert_achieve', 'cert_achieve_url', 'Achievement'),
                ('cert_intern', 'cert_intern_url', 'Internship'),
                ('cert_courses', 'cert_courses_url', 'Courses'),
                ('cert_sdp', 'cert_sdp_url', 'SDP'),
                ('cert_extra', 'cert_extra_url', 'Extracurricular'),
                ('cert_placement', 'cert_placement_url', 'Placement'),
                ('cert_national', 'cert_national_url', 'National'),
            ]

            for field, url_field, name in cert_fields:
                file_obj = getattr(student, field, None)
                url_obj = getattr(student, url_field, None)
                if file_obj or url_obj:
                    certs.append(name)

            if certs:
                self.stdout.write(f'  Certificates: {", ".join(certs)}')
            else:
                self.stdout.write('  Certificates: None')

            self.stdout.write('')