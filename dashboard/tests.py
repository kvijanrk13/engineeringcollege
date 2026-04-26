import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from dashboard.models import CloudinaryUpload, FDP, Faculty, ResearchPublication


class DashboardTests(TestCase):
    def test_login_page(self):
        response = self.client.get(reverse('dashboard:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ANURAG Engineering College')

    @patch('dashboard.views.generate_faculty_pdf', return_value=HttpResponse(b'%PDF-1.4 test'))
    @patch('dashboard.views.is_cloudinary_configured', return_value=True)
    @patch('dashboard.views.cloudinary.uploader.upload')
    def test_add_faculty_handles_non_contiguous_multi_upload_indexes(
        self,
        mock_upload,
        _mock_cloudinary_enabled,
        _mock_generate_pdf,
    ):
        user = get_user_model().objects.create_user(
            username='tester',
            email='tester@example.com',
            password='secret123',
        )
        self.client.force_login(user)

        def fake_upload(_uploaded_file, *args, **kwargs):
            public_id = kwargs['public_id']
            resource_type = kwargs.get('resource_type', 'auto')
            return {
                'secure_url': f'https://example.com/{public_id}',
                'public_id': public_id,
                'resource_type': resource_type,
            }

        mock_upload.side_effect = fake_upload

        response = self.client.post(
            reverse('dashboard:add_faculty'),
            data={
                'staff_name': 'Test Faculty',
                'employee_code': 'T9001',
                'father_name': 'Father Name',
                'mother_name': 'Mother Name',
                'gender': 'Male',
                'mobile': '9999999999',
                'email': 'faculty@example.com',
                'department': 'IT',
                'designation': 'Assistant Professor',
                'ssc_percent': '0',
                'inter_percent': '0',
                'ug_percentage': '0',
                'pg_percentage': '0',
                'research_publications_json': json.dumps([
                    {
                        'research_type': 'journal',
                        'title': 'Proof Linked Publication',
                        'authors': 'Author One',
                        'academic_year': '2023-2024',
                        'publication_year': 2024,
                        'journal_name': 'Journal of Testing',
                        'status': 'published',
                    }
                ]),
                'btech_projects_json': '[]',
                'results_json': '[]',
                'fdp_entries_json': json.dumps([
                    {
                        'fdp_type': 'fdp',
                        'title': 'Agentic AI Workshop',
                        'academic_year': '2024-2025',
                        'from_date': '2024-06-01',
                        'to_date': '2024-06-02',
                    }
                ]),
                'research_proofs_data': json.dumps([
                    {'academic_year': '2023-2024', 'file_name': 'research-proof.pdf'}
                ]),
                'fdp_certificates_data': json.dumps([
                    {'academic_year': '2024-2025', 'file_name': 'fdp-cert.pdf'}
                ]),
                'other_documents_data': '[]',
                'research_proof_files_2': SimpleUploadedFile(
                    'research-proof.pdf',
                    b'%PDF-1.4 research proof',
                    content_type='application/pdf',
                ),
                'fdp_cert_files_2': SimpleUploadedFile(
                    'fdp-cert.pdf',
                    b'%PDF-1.4 fdp certificate',
                    content_type='application/pdf',
                ),
            },
        )

        self.assertEqual(response.status_code, 302)

        faculty = Faculty.objects.get(employee_code='T9001')
        publication = ResearchPublication.objects.get(faculty=faculty)
        fdp = FDP.objects.get(faculty=faculty)

        self.assertEqual(
            faculty.research_proof_url,
            'https://example.com/research_proof_T9001_2',
        )
        self.assertEqual(faculty.research_proof_academic_year, '2023-2024')
        self.assertEqual(
            publication.proof_document_url,
            'https://example.com/research_proof_T9001_2',
        )

        self.assertEqual(
            faculty.fdp_certificate_url,
            'https://example.com/fdp_cert_T9001_2',
        )
        self.assertEqual(faculty.fdp_certificate_academic_year, '2024-2025')
        self.assertEqual(
            fdp.certificate_url,
            'https://example.com/fdp_cert_T9001_2',
        )

        self.assertTrue(
            CloudinaryUpload.objects.filter(
                faculty=faculty,
                upload_type='research_proof',
                cloudinary_url='https://example.com/research_proof_T9001_2',
            ).exists()
        )
        self.assertTrue(
            CloudinaryUpload.objects.filter(
                faculty=faculty,
                upload_type='fdp_certificate',
                cloudinary_url='https://example.com/fdp_cert_T9001_2',
            ).exists()
        )
