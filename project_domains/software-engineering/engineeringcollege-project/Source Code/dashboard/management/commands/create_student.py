"""
Django management command: create_student

Usage:
    python manage.py create_student --ht-no=23C11A1215 --name="Student Name" --email=email@college.edu
    python manage.py create_student --from-csv=students.csv
    python manage.py create_student --sample  # Create sample students
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from dashboard.models import Student
import csv
import sys
from datetime import datetime


class Command(BaseCommand):
    help = 'Create new student profiles with automatic certificate field initialization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ht-no',
            type=str,
            help='HT Number of the student (unique identifier)',
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Full name of the student',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address of the student',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number of the student',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year of study (1-4)',
        )
        parser.add_argument(
            '--sem',
            type=int,
            help='Semester (1-8)',
        )
        parser.add_argument(
            '--from-csv',
            type=str,
            help='CSV file with student data (columns: ht_no, student_name, email, phone, year, sem)',
        )
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Create sample student profiles',
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Verify all students in database',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all students in database',
        )

    def handle(self, *args, **options):
        if options['verify']:
            self.verify_students()
        elif options['list']:
            self.list_students()
        elif options['sample']:
            self.create_sample_students()
        elif options['from_csv']:
            self.create_from_csv(options['from_csv'])
        elif options['ht_no'] and options['name']:
            self.create_single_student(options)
        else:
            self.stdout.write(self.style.WARNING('No valid options provided. Use --help for more information.'))

    def create_single_student(self, options):
        """Create a single student."""
        student_data = {
            'ht_no': options['ht_no'],
            'student_name': options['name'],
        }
        
        if options.get('email'):
            student_data['email'] = options['email']
        if options.get('phone'):
            student_data['student_phone'] = options['phone']
        if options.get('year'):
            student_data['year'] = options['year']
        if options.get('sem'):
            student_data['sem'] = options['sem']
        
        try:
            student, created = Student.objects.get_or_create(
                ht_no=student_data['ht_no'],
                defaults=student_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created student: {student.student_name} '
                        f'(HT No: {student.ht_no}, ID: {student.id})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Student already exists: {student.student_name} '
                        f'(HT No: {student.ht_no}, ID: {student.id})'
                    )
                )
        except Exception as e:
            raise CommandError(f'Error creating student: {e}')

    def create_from_csv(self, csv_file):
        """Create students from CSV file."""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                created_count = 0
                skipped_count = 0
                
                for row in reader:
                    if not row.get('ht_no') or not row.get('student_name'):
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠ Skipping row - missing ht_no or student_name: {row}'
                            )
                        )
                        skipped_count += 1
                        continue
                    
                    student_data = {
                        'ht_no': row['ht_no'].strip(),
                        'student_name': row['student_name'].strip(),
                    }
                    
                    if row.get('email'):
                        student_data['email'] = row['email'].strip()
                    if row.get('phone'):
                        student_data['student_phone'] = row['phone'].strip()
                    if row.get('year'):
                        student_data['year'] = int(row['year']) if row['year'].isdigit() else None
                    if row.get('sem'):
                        student_data['sem'] = int(row['sem']) if row['sem'].isdigit() else None
                    
                    try:
                        student, created = Student.objects.get_or_create(
                            ht_no=student_data['ht_no'],
                            defaults=student_data
                        )
                        
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✓ Created: {student.student_name} ({student.ht_no})'
                                )
                            )
                            created_count += 1
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⚠ Already exists: {student.student_name} ({student.ht_no})'
                                )
                            )
                            skipped_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Error creating {row.get("ht_no")}: {e}'
                            )
                        )
                        skipped_count += 1
                
                self.stdout.write('\n' + '=' * 70)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Summary: Created {created_count} students, '
                        f'Skipped {skipped_count} rows'
                    )
                )
                self.stdout.write('=' * 70)
        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')
        except Exception as e:
            raise CommandError(f'Error reading CSV: {e}')

    def create_sample_students(self):
        """Create sample student profiles."""
        sample_students = [
            {
                'ht_no': '23C11A1215',
                'student_name': 'SAMPLE STUDENT 15',
                'email': 'sample15@college.edu',
                'student_phone': '9876543215',
                'year': 4,
                'sem': 7,
                'cgpa': '8.5',
            },
            {
                'ht_no': '23C11A1216',
                'student_name': 'SAMPLE STUDENT 16',
                'email': 'sample16@college.edu',
                'student_phone': '9876543216',
                'year': 4,
                'sem': 7,
                'cgpa': '8.2',
            },
            {
                'ht_no': '23C11A1217',
                'student_name': 'SAMPLE STUDENT 17',
                'email': 'sample17@college.edu',
                'student_phone': '9876543217',
                'year': 4,
                'sem': 7,
                'cgpa': '7.9',
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for student_data in sample_students:
            try:
                student, created = Student.objects.get_or_create(
                    ht_no=student_data['ht_no'],
                    defaults=student_data
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created: {student.student_name} ({student.ht_no}, ID: {student.id})'
                        )
                    )
                    created_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Already exists: {student.student_name} ({student.ht_no}, ID: {student.id})'
                        )
                    )
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error creating {student_data.get("ht_no")}: {e}'
                    )
                )
                skipped_count += 1
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: Created {created_count} students, Skipped {skipped_count}'
            )
        )
        self.stdout.write('=' * 70)

    def list_students(self):
        """List all students in database."""
        students = Student.objects.all().order_by('id')
        
        if not students.exists():
            self.stdout.write(self.style.WARNING('No students found in database.'))
            return
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'STUDENTS IN DATABASE ({students.count()} total)')
        self.stdout.write('=' * 70 + '\n')
        
        for student in students:
            self.stdout.write(
                f'ID: {student.id:3d} | HT No: {student.ht_no:15s} | {student.student_name}'
            )
            self.stdout.write(
                f'      Email: {student.email or "N/A"} | Phone: {student.student_phone or "N/A"}'
            )
            self.stdout.write(f'      Year: {student.year}, Sem: {student.sem}\n')

    def verify_students(self):
        """Verify student structures."""
        students = Student.objects.all()
        
        if not students.exists():
            self.stdout.write(self.style.WARNING('No students found in database.'))
            return
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('STUDENT STRUCTURE VERIFICATION')
        self.stdout.write('=' * 70 + '\n')
        
        cert_fields = [
            'cert_achieve', 'cert_intern', 'cert_courses',
            'cert_sdp', 'cert_extra', 'cert_placement', 'cert_national'
        ]
        
        for student in students:
            self.stdout.write(f'{student.student_name} (ID: {student.id}, HT No: {student.ht_no})')
            
            cert_count = sum(1 for field in cert_fields if getattr(student, field, None) or getattr(student, f'{field}_url', None))
            photo_count = 1 if student.photo or student.photo_url else 0
            
            self.stdout.write(
                f'  Certificates: {cert_count}/{len(cert_fields)} | '
                f'Photo: {"✓" if photo_count else "○"} | '
                f'PDF: {"✓" if student.pdf_generated else "○"}\n'
            )
