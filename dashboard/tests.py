import io
import json
import hashlib
import os
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse

from dashboard import views as dashboard_views
from dashboard.models import (
    Certificate, CloudinaryUpload, FDP, Faculty, ProjectDownloadPayment,
    ResearchPublication, Student,
)
from dashboard.pdf_generation import (
    FACULTY_PDF_TEMPLATE,
    STUDENT_PDF_TEMPLATE,
)

from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas


def make_test_image_bytes(fmt='JPEG', color=(32, 96, 180)):
    buffer = io.BytesIO()
    Image.new('RGB', (60, 80), color=color).save(buffer, format=fmt)
    return buffer.getvalue()


def make_test_pdf_bytes(label='Test PDF'):
    buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(buffer)
    pdf_canvas.drawString(72, 720, label)
    pdf_canvas.showPage()
    pdf_canvas.save()
    return buffer.getvalue()


class DashboardTests(TestCase):
    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_login_page(self):
        response = self.client.get(reverse('dashboard:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Engineering College')

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_mobile_dashboard_page_is_available_without_admin_login(self):
        response = self.client.get(reverse('dashboard:mobile_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Engineering College')
        self.assertContains(response, 'Department Command Center')

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID='test-client-id',
        GOOGLE_OAUTH_CLIENT_SECRET='test-client-secret',
        SECURE_SSL_REDIRECT=False,
    )
    @patch('dashboard.views.requests.get')
    @patch('dashboard.views.requests.post')
    def test_mobile_google_callback_survives_lost_browser_session(self, mock_post, mock_get):
        student = Student.objects.create(
            ht_no='22IT001',
            student_name='Mobile Student',
            email='mobile@example.com',
        )
        start_response = self.client.get(
            reverse('dashboard:google_login'),
            {'role': 'student', 'mobile': '1', 'continue': '1'},
        )
        state = parse_qs(urlparse(start_response['Location']).query)['state'][0]

        self.client.cookies.clear()
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {'access_token': 'access-token'},
        )
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {'email': student.email, 'email_verified': True},
        )

        callback_response = self.client.get(
            reverse('dashboard:google_callback'),
            {'code': 'auth-code', 'state': state},
        )

        self.assertEqual(callback_response.status_code, 302)
        self.assertTrue(callback_response['Location'].startswith('engineeringcollegeprojects://auth?token='))

        token = parse_qs(urlparse(callback_response['Location']).query)['token'][0]
        complete_response = self.client.get(
            reverse('dashboard:google_mobile_complete'),
            {'token': token},
        )

        self.assertEqual(complete_response.status_code, 302)
        self.assertEqual(complete_response['Location'], reverse('dashboard:add_student'))
        self.assertTrue(self.client.session['student_logged_in'])
        self.assertEqual(self.client.session['student_id'], student.id)
        self.assertEqual(self.client.session['student_display_name'], student.student_name)

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID='test-client-id',
        GOOGLE_OAUTH_CLIENT_SECRET='test-client-secret',
        SECURE_SSL_REDIRECT=False,
    )
    @patch('dashboard.views.requests.get')
    @patch('dashboard.views.requests.post')
    def test_google_faculty_login_uses_matching_faculty_name(self, mock_post, mock_get):
        faculty = Faculty.objects.create(
            staff_name='Consistent Faculty Name',
            employee_code='GMAILFAC001',
            email='faculty@example.com',
        )
        start_response = self.client.get(
            reverse('dashboard:google_login'),
            {'role': 'admin', 'continue': '1'},
        )
        state = parse_qs(urlparse(start_response['Location']).query)['state'][0]

        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {'access_token': 'access-token'},
        )
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                'email': faculty.email,
                'email_verified': True,
                'name': 'Different Gmail Name',
                'given_name': 'Different',
                'family_name': 'Gmail Name',
            },
        )

        callback_response = self.client.get(
            reverse('dashboard:google_callback'),
            {'code': 'auth-code', 'state': state},
        )

        self.assertEqual(callback_response.status_code, 302)
        self.assertEqual(callback_response['Location'], reverse('dashboard:add_faculty'))
        user = get_user_model().objects.get(email=faculty.email)
        self.assertEqual(user.get_full_name(), faculty.staff_name)
        self.assertTrue(user.is_staff)

    def test_pdf_generation_uses_dedicated_assets_boundary(self):
        self.assertEqual(STUDENT_PDF_TEMPLATE, 'dashboard/student_pdf.html')
        self.assertEqual(FACULTY_PDF_TEMPLATE, 'dashboard/faculty_pdf.html')

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_students_data_route_renders_directory_actions(self):
        user = get_user_model().objects.create_user(
            username='student-list-admin',
            password='testpass123',
            is_staff=True,
        )
        self.client.force_login(user)
        Student.objects.create(
            ht_no='22ITVIEW001',
            student_name='Directory Student',
            year=2,
            sem=1,
        )

        response = self.client.get(reverse('dashboard:students_data'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hall Ticket Number')
        self.assertContains(response, 'Directory Student')
        self.assertContains(response, reverse('dashboard:student_detail', args=[Student.objects.get(ht_no='22ITVIEW001').id]))
        self.assertContains(response, reverse('dashboard:edit_student', args=[Student.objects.get(ht_no='22ITVIEW001').id]))
        self.assertContains(response, reverse('dashboard:generate_student_pdf', args=[Student.objects.get(ht_no='22ITVIEW001').id]))
        self.assertContains(response, reverse('dashboard:delete_student', args=[Student.objects.get(ht_no='22ITVIEW001').id]))

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_add_student_redirects_to_students_directory(self):
        response = self.client.post(reverse('dashboard:add_student'), {
            'ht_no': '22ITSUBMIT001',
            'student_name': 'Submitted Student',
            'father_name': 'Parent One',
            'mother_name': 'Parent Two',
            'gender': 'Other',
            'nationality': 'Indian',
            'email': 'submitted@example.com',
            'year': '3',
            'sem': '2',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard:students_data'))

        list_response = self.client.get(response['Location'])
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Submitted Student')
        self.assertContains(list_response, '22ITSUBMIT001')

    def test_resolve_faculty_photo_for_pdf_uses_file_field(self):
        faculty = Faculty.objects.create(
            staff_name='Photo Faculty',
            employee_code='PHOTO9001',
            department='IT',
            designation='Assistant Professor',
            photo=SimpleUploadedFile(
                'photo.jpg',
                make_test_image_bytes(),
                content_type='image/jpeg',
            ),
        )

        data_uri, local_path, temp_paths, source = dashboard_views.resolve_faculty_photo_for_pdf(faculty)

        self.assertTrue(data_uri.startswith('data:image/jpeg;base64,'))
        self.assertTrue(Path(local_path).exists())
        self.assertEqual(temp_paths, [])
        self.assertEqual(source, 'photo_field_path')

    def test_resolve_faculty_photo_for_pdf_falls_back_to_media_file_by_employee_code(self):
        faculty = Faculty.objects.create(
            staff_name='Fallback Faculty',
            employee_code='PHOTO9002',
            department='IT',
            designation='Assistant Professor',
        )

        with tempfile.TemporaryDirectory() as temp_media_root:
            photo_dir = Path(temp_media_root) / 'faculty_photos'
            photo_dir.mkdir(parents=True, exist_ok=True)
            fallback_path = photo_dir / 'PHOTO9002.jpg'
            fallback_path.write_bytes(make_test_image_bytes())

            with override_settings(MEDIA_ROOT=temp_media_root):
                data_uri, local_path, temp_paths, source = dashboard_views.resolve_faculty_photo_for_pdf(faculty)

        self.assertTrue(data_uri.startswith('data:image/jpeg;base64,'))
        self.assertEqual(Path(local_path), fallback_path)
        self.assertEqual(temp_paths, [])
        self.assertEqual(source, 'media_employee_code_fallback')

    def test_reportlab_faculty_fallback_embeds_photo_when_available(self):
        faculty = Faculty.objects.create(
            staff_name='Fallback PDF Faculty',
            employee_code='PHOTO9003',
            department='IT',
            designation='Assistant Professor',
            photo=SimpleUploadedFile(
                'fallback-photo.jpg',
                make_test_image_bytes(),
                content_type='image/jpeg',
            ),
        )

        pdf_bytes = dashboard_views._build_reportlab_faculty_pdf(faculty)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        resources = reader.pages[0]['/Resources']

        self.assertIn('/XObject', resources)

    def test_faculty_dashboard_shows_gallery_and_resolved_faculty_photo(self):
        user = get_user_model().objects.create_user(
            username='faculty-dashboard-user',
            email='faculty-dashboard-user@example.com',
            password='secret123',
        )
        self.client.force_login(user)

        faculty = Faculty.objects.create(
            staff_name='Dashboard Faculty',
            employee_code='PHOTO9004',
            department='IT',
            designation='Assistant Professor',
        )

        with tempfile.TemporaryDirectory() as temp_media_root:
            photo_dir = Path(temp_media_root) / 'faculty_photos'
            photo_dir.mkdir(parents=True, exist_ok=True)
            (photo_dir / 'PHOTO9004.jpg').write_bytes(make_test_image_bytes())

            with override_settings(MEDIA_ROOT=temp_media_root):
                response = self.client.get(
                    reverse('dashboard:faculty') + f'?id={faculty.id}',
                    secure=True,
                )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gallery')
        self.assertContains(response, 'data:image/jpeg;base64,')

    def test_gallery_page_shows_gallery_content(self):
        user = get_user_model().objects.create_user(
            username='gallery-user',
            email='gallery-user@example.com',
            password='secret123',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard:gallery'), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gallery')
        self.assertContains(response, 'CONNECT HACKATHON 2026')
        self.assertContains(response, 'ITECH-2K26')

    @patch('dashboard.views.is_cloudinary_configured', return_value=True)
    @patch('dashboard.views.requests.get')
    @patch('dashboard.views.try_cloudinary_private_download')
    @patch('dashboard.views.cloudinary.api.resource')
    def test_download_remote_asset_retries_cloudinary_raw_public_id_with_extension(
        self,
        mock_cloudinary_resource,
        mock_private_download,
        mock_requests_get,
        _mock_cloudinary_enabled,
    ):
        cloudinary_url = (
            'https://res.cloudinary.com/demo/raw/upload/v1778072713/'
            'faculty_documents/7001/research_proofs/research_proof_7001_1.pdf'
        )
        private_response = Mock(
            status_code=200,
            headers={'content-type': 'application/pdf'},
            content=make_test_pdf_bytes('Research Proof'),
        )

        mock_cloudinary_resource.side_effect = Exception('not found')
        mock_requests_get.return_value = Mock(status_code=401, headers={}, content=b'')

        def fake_private_download(public_id, headers=None):
            if public_id.endswith('.pdf'):
                return private_response
            return None

        mock_private_download.side_effect = fake_private_download

        downloaded_path, is_pdf = dashboard_views.download_remote_asset(cloudinary_url)

        try:
            self.assertTrue(is_pdf)
            self.assertIsNotNone(downloaded_path)
            self.assertTrue(Path(downloaded_path).exists())
            self.assertEqual(Path(downloaded_path).suffix.lower(), '.pdf')
        finally:
            if downloaded_path and Path(downloaded_path).exists():
                Path(downloaded_path).unlink()

        mock_private_download.assert_any_call(
            'faculty_documents/7001/research_proofs/research_proof_7001_1.pdf'
        )

    @patch('dashboard.views.pdfkit', new=None)
    @patch('dashboard.views.is_cloudinary_configured', return_value=True)
    @patch('dashboard.views.cloudinary.uploader.upload')
    @patch('dashboard.views.download_remote_asset')
    @patch('dashboard.views.requests.get')
    def test_generate_student_pdf_merges_certificate_url_into_cloudinary_pdf(
        self,
        mock_requests_get,
        mock_download_remote_asset,
        mock_upload,
        _mock_cloudinary_enabled,
    ):
        mock_requests_get.return_value.status_code = 403
        mock_requests_get.return_value.headers = {}
        mock_requests_get.return_value.content = b''

        def fake_download_remote_asset(url, default_suffix='.pdf'):
            self.assertEqual(url, 'https://example.com/certificate.pdf')
            temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_pdf.write(make_test_pdf_bytes('Student Certificate'))
            temp_pdf.close()
            return temp_pdf.name, True

        uploaded_page_counts = []

        def fake_upload(file_path, *args, **kwargs):
            uploaded_page_counts.append(len(PdfReader(file_path).pages))
            return {
                'secure_url': 'https://example.com/student_merged.pdf',
                'public_id': kwargs['public_id'],
                'resource_type': kwargs.get('resource_type', 'raw'),
            }

        mock_download_remote_asset.side_effect = fake_download_remote_asset
        mock_upload.side_effect = fake_upload

        student = Student.objects.create(
            ht_no='23C11A9999',
            student_name='Student Merge Test',
            cert_achieve_url='https://example.com/certificate.pdf',
        )

        pdf_url = dashboard_views.generate_student_pdf(student)

        self.assertEqual(pdf_url, 'https://example.com/student_merged.pdf')
        self.assertEqual(len(uploaded_page_counts), 1)
        self.assertGreaterEqual(uploaded_page_counts[0], 2)
        mock_download_remote_asset.assert_called_once_with(
            'https://example.com/certificate.pdf',
            default_suffix='.jpg',
        )

        student.refresh_from_db()
        self.assertEqual(student.pdf_url, 'https://example.com/student_merged.pdf')
        self.assertTrue(student.pdf_generated)

    @patch('dashboard.views.generate_student_profile_pdf', return_value='https://example.com/student.pdf')
    @patch('dashboard.views.is_cloudinary_configured', return_value=False)
    def test_add_student_persists_additional_certificate_uploads(
        self,
        _mock_cloudinary_enabled,
        _mock_generate_student_pdf,
    ):
        with tempfile.TemporaryDirectory() as temp_media_root:
            response = None
            with override_settings(MEDIA_ROOT=temp_media_root):
                response = self.client.post(
                    reverse('dashboard:add_student'),
                    data={
                        'ht_no': '23C11A5555',
                        'student_name': 'Additional Certificate Student',
                        'admission_type': 'EAMCET',
                        'year': '2',
                        'sem': '1',
                        'additional_cert_type_1': 'achievement',
                        'additional_cert_title_1': 'Hackathon Winner',
                        'additional_cert_file_1': SimpleUploadedFile(
                            'achievement.pdf',
                            make_test_pdf_bytes('Achievement'),
                            content_type='application/pdf',
                        ),
                    },
                    secure=True,
                )

            self.assertIn(response.status_code, {301, 302})

        student = Student.objects.get(ht_no='23C11A5555')
        self.assertTrue(bool(student.cert_achieve))
        self.assertFalse(student.cert_achieve_url)

    @patch('dashboard.views.generate_student_profile_pdf', return_value='https://example.com/student-with-assets.pdf')
    @patch('dashboard.views.is_cloudinary_configured', return_value=False)
    def test_add_student_passes_uploaded_photo_and_certificate_overrides_to_pdf_generation(
        self,
        _mock_cloudinary_enabled,
        mock_generate_student_pdf,
    ):
        with tempfile.TemporaryDirectory() as temp_media_root:
            with override_settings(MEDIA_ROOT=temp_media_root):
                response = self.client.post(
                    reverse('dashboard:add_student'),
                    data={
                        'ht_no': '23C11A5556',
                        'student_name': 'PDF Asset Student',
                        'admission_type': 'EAMCET',
                        'year': '2',
                        'sem': '1',
                        'photo': SimpleUploadedFile(
                            'student-photo.jpg',
                            make_test_image_bytes(),
                            content_type='image/jpeg',
                        ),
                        'cert_achieve': SimpleUploadedFile(
                            'achievement.pdf',
                            make_test_pdf_bytes('Achievement'),
                            content_type='application/pdf',
                        ),
                    },
                    secure=True,
                )

        self.assertIn(response.status_code, {301, 302})
        self.assertTrue(mock_generate_student_pdf.called)
        _, kwargs = mock_generate_student_pdf.call_args
        self.assertTrue(kwargs['photo_override_path'])
        self.assertEqual(len(kwargs['certificate_override_assets']), 1)
        self.assertEqual(kwargs['certificate_override_assets'][0]['field_name'], 'cert_achieve')
        self.assertTrue(kwargs['certificate_override_assets'][0]['is_pdf'])

    def test_student_photo_redirect_normalizes_scheme_less_urls(self):
        student = Student.objects.create(
            ht_no='23C11A7777',
            student_name='URL Normalization Student',
            photo_url='res.cloudinary.com/demo/image/upload/v1/student/sample.jpg',
        )

        response = self.client.get(
            reverse('dashboard:student_photo_redirect', args=[student.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            'https://res.cloudinary.com/demo/image/upload/v1/student/sample.jpg',
        )

    def test_student_photo_redirect_falls_back_to_latest_cloudinary_upload(self):
        student = Student.objects.create(
            ht_no='23C11A7778',
            student_name='History Photo Student',
        )
        CloudinaryUpload.objects.create(
            student=student,
            upload_type='photo',
            cloudinary_url='https://example.com/student-history-photo.jpg',
            public_id='student-history-photo',
            resource_type='image',
        )

        response = self.client.get(
            reverse('dashboard:student_photo_redirect', args=[student.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://example.com/student-history-photo.jpg')

    def test_student_photo_redirect_prefers_local_photo_over_stale_photo_url(self):
        with tempfile.TemporaryDirectory() as temp_media_root:
            with override_settings(MEDIA_ROOT=temp_media_root, MEDIA_URL='/media/'):
                student = Student.objects.create(
                    ht_no='23C11A7778L',
                    student_name='Local Photo Student',
                    photo_url='https://example.com/stale-photo.jpg',
                    photo=SimpleUploadedFile(
                        'local-student-photo.jpg',
                        make_test_image_bytes(),
                        content_type='image/jpeg',
                    ),
                )

                response = self.client.get(
                    reverse('dashboard:student_photo_redirect', args=[student.id]),
                    secure=True,
                )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/media/student_photos/local-student-photo', response['Location'])

    @patch('dashboard.views.download_remote_asset')
    def test_resolve_student_photo_for_pdf_falls_back_to_latest_cloudinary_upload(self, mock_download_remote_asset):
        student = Student.objects.create(
            ht_no='23C11A7779',
            student_name='PDF History Photo Student',
        )
        CloudinaryUpload.objects.create(
            student=student,
            upload_type='photo',
            cloudinary_url='https://example.com/student-pdf-history-photo.jpg',
            public_id='student-pdf-history-photo',
            resource_type='image',
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_photo:
            temp_photo.write(make_test_image_bytes())
            temp_photo_path = temp_photo.name

        mock_download_remote_asset.return_value = (temp_photo_path, False)

        try:
            photo_uri, local_path, temp_paths, source = dashboard_views.resolve_student_photo_for_pdf(student)
        finally:
            if Path(temp_photo_path).exists():
                Path(temp_photo_path).unlink()

        self.assertTrue(photo_uri.startswith('data:image/') or photo_uri.startswith('file:///'))
        self.assertEqual(local_path, temp_photo_path)
        self.assertEqual(temp_paths, [temp_photo_path])
        self.assertEqual(source, 'cloudinary_upload_history')

    @patch('dashboard.views.download_remote_asset')
    def test_view_student_pdf_streams_cloudinary_pdf_through_app_route(self, mock_download_remote_asset):
        admin_user = get_user_model().objects.create_user(
            username='pdf-admin',
            email='pdf-admin@example.com',
            password='secret123',
        )
        self.client.force_login(admin_user)

        student = Student.objects.create(
            ht_no='23C11A7780',
            student_name='PDF Stream Student',
            pdf_url='https://example.com/student.pdf',
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(make_test_pdf_bytes('Student PDF'))
            temp_pdf_path = temp_pdf.name

        mock_download_remote_asset.return_value = (temp_pdf_path, True)

        response = self.client.get(
            reverse('dashboard:view_student_pdf', args=[student.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline;', response['Content-Disposition'])

    @patch('dashboard.views.generate_student_profile_pdf_bytes', return_value=make_test_pdf_bytes('Regenerated Student PDF'))
    @patch('dashboard.views.download_remote_asset', return_value=(None, False))
    def test_view_student_pdf_regenerates_when_saved_pdf_url_is_stale(
        self,
        _mock_download_remote_asset,
        mock_generate_student_pdf,
    ):
        admin_user = get_user_model().objects.create_user(
            username='pdf-regenerate-admin',
            email='pdf-regenerate-admin@example.com',
            password='secret123',
        )
        self.client.force_login(admin_user)

        student = Student.objects.create(
            ht_no='23C11A7780R',
            student_name='Stale Student PDF',
            pdf_url='https://example.com/stale-student.pdf',
        )

        response = self.client.get(
            reverse('dashboard:view_student_pdf', args=[student.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        mock_generate_student_pdf.assert_called_once_with(student)

    @patch('dashboard.views.download_remote_asset', return_value=(None, False))
    @patch('dashboard.views.is_cloudinary_configured', return_value=False)
    def test_generate_student_pdf_uses_saved_file_fields_when_url_fields_are_stale(
        self,
        _mock_cloudinary_enabled,
        _mock_download_remote_asset,
    ):
        student = Student.objects.create(
            ht_no='23C11A7790',
            student_name='Durable Asset Student',
            photo=SimpleUploadedFile(
                'durable-photo.jpg',
                make_test_image_bytes(),
                content_type='image/jpeg',
            ),
            photo_url='https://example.com/stale-photo.jpg',
            cert_achieve=SimpleUploadedFile(
                'durable-achievement.pdf',
                make_test_pdf_bytes('Durable Achievement'),
                content_type='application/pdf',
            ),
            cert_achieve_url='https://example.com/stale-achievement.pdf',
        )

        pdf_bytes = dashboard_views.generate_student_pdf(student, return_bytes=True)
        student.refresh_from_db()

        reader = PdfReader(io.BytesIO(pdf_bytes))
        combined_text = '\n'.join((page.extract_text() or '') for page in reader.pages[:2])

        self.assertGreaterEqual(len(reader.pages), 3)
        self.assertNotIn('NO PHOTO', combined_text)
        self.assertTrue(bool(student.pdf_file))

    @patch('dashboard.views.generate_student_profile_pdf_bytes', return_value=make_test_pdf_bytes('Generated Student PDF'))
    def test_demo_student_session_can_generate_student_pdf(self, _mock_generate_student_pdf):
        student = Student.objects.create(
            ht_no='23C11A7781',
            student_name='Demo Session Student',
        )

        session = self.client.session
        session['student_logged_in'] = True
        session['student_username'] = 'anrkitstudent'
        session.save()

        response = self.client.get(
            reverse('dashboard:generate_student_pdf', args=[student.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_students_data_filters_to_logged_in_student_record(self):
        own_student = Student.objects.create(
            ht_no='23C11A7782',
            student_name='Own Student',
        )
        Student.objects.create(
            ht_no='23C11A7783',
            student_name='Other Student',
        )

        session = self.client.session
        session['student_logged_in'] = True
        session['student_username'] = own_student.ht_no
        session['student_ht_no'] = own_student.ht_no
        session['student_id'] = own_student.id
        session.save()

        response = self.client.get(reverse('dashboard:students'), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, own_student.ht_no)
        self.assertNotContains(response, '23C11A7783')

    def test_student_dashboard_uses_student_photo_redirect_for_profile_box(self):
        student = Student.objects.create(
            ht_no='23C11A7784',
            student_name='Dashboard Photo Student',
            photo_url='https://example.com/student-photo.jpg',
        )

        session = self.client.session
        session['student_logged_in'] = True
        session['student_username'] = student.ht_no
        session['student_ht_no'] = student.ht_no
        session['student_id'] = student.id
        session.save()

        response = self.client.get(reverse('dashboard:student_dashboard_view'), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('dashboard:student_photo_redirect', args=[student.id]),
        )

    def test_students_data_uses_student_photo_redirect_even_without_photo_fields(self):
        admin_user = get_user_model().objects.create_user(
            username='students-list-admin',
            email='students-list-admin@example.com',
            password='secret123',
        )
        self.client.force_login(admin_user)

        student = Student.objects.create(
            ht_no='23C11A7784H',
            student_name='History Only Photo Student',
        )
        CloudinaryUpload.objects.create(
            student=student,
            upload_type='photo',
            cloudinary_url='https://example.com/student-history-only-photo.jpg',
            public_id='student-history-only-photo',
            resource_type='image',
        )

        response = self.client.get(reverse('dashboard:students'), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('dashboard:student_photo_redirect', args=[student.id]),
        )

    @patch('dashboard.views.generate_student_profile_pdf', return_value='https://example.com/student.pdf')
    @patch('dashboard.views.is_cloudinary_configured', return_value=True)
    @patch('dashboard.views.cloudinary.uploader.upload')
    def test_add_student_cloudinary_assets_display_on_detail_page(
        self,
        mock_upload,
        _mock_cloudinary_enabled,
        _mock_generate_student_pdf,
    ):
        admin_user = get_user_model().objects.create_user(
            username='student-admin',
            email='student-admin@example.com',
            password='secret123',
        )
        self.client.force_login(admin_user)

        def fake_upload(uploaded_file, *args, **kwargs):
            folder = kwargs['folder']
            public_id = kwargs['public_id']
            resource_type = kwargs.get('resource_type', 'auto')
            return {
                'secure_url': f'https://example.com/{folder}/{public_id}',
                'public_id': public_id,
                'resource_type': resource_type,
            }

        mock_upload.side_effect = fake_upload

        response = self.client.post(
            reverse('dashboard:add_student'),
            data={
                'ht_no': '23C11A6001',
                'student_name': 'Cloudinary Student',
                'admission_type': 'EAMCET',
                'year': '2',
                'sem': '1',
                'photo': SimpleUploadedFile(
                    'student-photo.jpg',
                    make_test_image_bytes(),
                    content_type='image/jpeg',
                ),
                'cert_achieve': SimpleUploadedFile(
                    'achievement.pdf',
                    make_test_pdf_bytes('Achievement'),
                    content_type='application/pdf',
                ),
            },
            secure=True,
        )

        self.assertIn(response.status_code, {301, 302})

        student = Student.objects.get(ht_no='23C11A6001')
        self.assertTrue(student.photo_url.startswith('https://example.com/student_documents/photos/'))
        self.assertTrue(student.cert_achieve_url.startswith('https://example.com/student_documents/achievement/'))
        self.assertTrue(bool(student.photo))
        self.assertTrue(bool(student.cert_achieve))
        self.assertTrue(
            CloudinaryUpload.objects.filter(student=student, upload_type='photo').exists()
        )
        self.assertTrue(
            CloudinaryUpload.objects.filter(student=student, upload_type='cert_achieve').exists()
        )

        photo_response = self.client.get(
            reverse('dashboard:student_photo_redirect', args=[student.id]),
            secure=True,
        )
        self.assertEqual(photo_response.status_code, 302)
        self.assertEqual(photo_response['Location'], student.photo_url)

        detail_response = self.client.get(
            reverse('dashboard:student_detail', args=[student.id]),
            secure=True,
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertNotContains(detail_response, 'No Photo')
        self.assertNotContains(detail_response, 'No documents uploaded.')
        self.assertContains(detail_response, 'View Document')

    @patch('dashboard.views.is_cloudinary_configured', return_value=True)
    @patch('dashboard.views.cloudinary.uploader.upload')
    def test_merge_student_certificates_uploads_pdf_and_redirects(
        self,
        mock_upload,
        _mock_cloudinary_enabled,
    ):
        admin_user = get_user_model().objects.create_user(
            username='merge-admin',
            email='merge-admin@example.com',
            password='secret123',
        )
        self.client.force_login(admin_user)

        student = Student.objects.create(
            ht_no='23C11A6002',
            student_name='Merge Student',
            photo=SimpleUploadedFile(
                'student-photo.jpg',
                make_test_image_bytes(),
                content_type='image/jpeg',
            ),
            cert_achieve=SimpleUploadedFile(
                'achievement.pdf',
                make_test_pdf_bytes('Achievement'),
                content_type='application/pdf',
            ),
        )

        mock_upload.return_value = {
            'secure_url': 'https://example.com/merged-student.pdf',
            'public_id': 'merged_student_23C11A6002',
            'resource_type': 'raw',
        }

        response = self.client.get(
            reverse('dashboard:merge_student_certificates', args=[student.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard:student_detail', args=[student.id]))
        self.assertTrue(mock_upload.called)
        self.assertTrue(
            CloudinaryUpload.objects.filter(
                student=student,
                upload_type='merged_student_certificates',
                cloudinary_url='https://example.com/merged-student.pdf',
            ).exists()
        )

    @patch('dashboard.views.is_cloudinary_configured', return_value=True)
    @patch('dashboard.views.cloudinary.uploader.upload')
    @patch('dashboard.views.download_remote_asset')
    def test_merge_student_certificates_uses_photo_upload_history_when_photo_fields_are_empty(
        self,
        mock_download_remote_asset,
        mock_upload,
        _mock_cloudinary_enabled,
    ):
        admin_user = get_user_model().objects.create_user(
            username='merge-history-admin',
            email='merge-history-admin@example.com',
            password='secret123',
        )
        self.client.force_login(admin_user)

        student = Student.objects.create(
            ht_no='23C11A6003',
            student_name='Merge History Student',
        )
        CloudinaryUpload.objects.create(
            student=student,
            upload_type='photo',
            cloudinary_url='https://example.com/history-photo.jpg',
            public_id='history-photo',
            resource_type='image',
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_photo:
            temp_photo.write(make_test_image_bytes())
            temp_photo_path = temp_photo.name

        mock_download_remote_asset.return_value = (temp_photo_path, False)
        mock_upload.return_value = {
            'secure_url': 'https://example.com/merged-history-student.pdf',
            'public_id': 'merged_student_23C11A6003',
            'resource_type': 'raw',
        }

        try:
            response = self.client.get(
                reverse('dashboard:merge_student_certificates', args=[student.id]),
                secure=True,
            )
        finally:
            if Path(temp_photo_path).exists():
                Path(temp_photo_path).unlink()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard:student_detail', args=[student.id]))
        self.assertTrue(mock_upload.called)

    @patch('dashboard.views.pdfkit', new=None)
    @patch('dashboard.views.is_cloudinary_configured', return_value=True)
    @patch('dashboard.views.cloudinary.uploader.upload')
    @patch('dashboard.views.requests.get')
    def test_generate_student_pdf_uses_uploaded_overrides_when_remote_assets_fail(
        self,
        mock_requests_get,
        mock_upload,
        _mock_cloudinary_enabled,
    ):
        mock_requests_get.return_value.status_code = 403
        mock_requests_get.return_value.headers = {}
        mock_requests_get.return_value.content = b''

        uploaded_page_counts = []

        def fake_upload(file_path, *args, **kwargs):
            uploaded_page_counts.append(len(PdfReader(file_path).pages))
            return {
                'secure_url': 'https://example.com/student_override_merged.pdf',
                'public_id': kwargs['public_id'],
                'resource_type': kwargs.get('resource_type', 'raw'),
            }

        mock_upload.side_effect = fake_upload

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as photo_tmp:
            photo_tmp.write(make_test_image_bytes())
            photo_path = photo_tmp.name
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as cert_tmp:
            cert_tmp.write(make_test_pdf_bytes('Override Certificate'))
            cert_path = cert_tmp.name

        student = Student.objects.create(
            ht_no='23C11A7001',
            student_name='Override Merge Student',
            photo_url='https://example.com/photo.jpg',
            cert_achieve_url='https://example.com/certificate.pdf',
        )

        try:
            pdf_url = dashboard_views.generate_student_pdf(
                student,
                photo_override_path=photo_path,
                certificate_override_assets=[
                    {
                        'field_name': 'cert_achieve',
                        'path': cert_path,
                        'is_pdf': True,
                    }
                ],
            )
        finally:
            for temp_path in (photo_path, cert_path):
                if Path(temp_path).exists():
                    Path(temp_path).unlink()

        self.assertEqual(pdf_url, 'https://example.com/student_override_merged.pdf')
        self.assertEqual(len(uploaded_page_counts), 1)
        self.assertGreater(uploaded_page_counts[0], 2)

    @patch('dashboard.views.generate_student_profile_pdf', return_value='https://example.com/student-edited.pdf')
    @patch('dashboard.views.is_cloudinary_configured', return_value=False)
    def test_edit_student_regenerates_pdf_after_uploaded_changes(
        self,
        _mock_cloudinary_enabled,
        mock_generate_student_pdf,
    ):
        student = Student.objects.create(
            ht_no='23C11A8001',
            student_name='Edit Student',
        )
        user = get_user_model().objects.create_user(
            username='edit-student-admin',
            email='edit-student-admin@example.com',
            password='secret123',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('dashboard:edit_student', args=[student.id]),
            data={
                'ht_no': student.ht_no,
                'student_name': student.student_name,
                'nationality': 'Indian',
                'photo': SimpleUploadedFile(
                    'edit-photo.jpg',
                    make_test_image_bytes(),
                    content_type='image/jpeg',
                ),
                'cert_achieve': SimpleUploadedFile(
                    'edit-achievement.pdf',
                    make_test_pdf_bytes('Edit Achievement'),
                    content_type='application/pdf',
                ),
            },
            secure=True,
        )

        self.assertIn(response.status_code, {301, 302})
        self.assertTrue(mock_generate_student_pdf.called)
        _, kwargs = mock_generate_student_pdf.call_args
        self.assertTrue(kwargs['photo_override_path'])
        self.assertEqual(len(kwargs['certificate_override_assets']), 1)

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
                'jntuh_id': 'JNTUH-T9001',
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

    def test_merge_certificates_with_pdf_bytes_merges_faculty_related_assets(self):
        with tempfile.TemporaryDirectory() as temp_media_root:
            with override_settings(MEDIA_ROOT=temp_media_root):
                faculty = Faculty.objects.create(
                    staff_name='Merged Faculty',
                    employee_code='F9002',
                    department='IT',
                    designation='Assistant Professor',
                    photo=SimpleUploadedFile(
                        'faculty-photo.jpg',
                        make_test_image_bytes(),
                        content_type='image/jpeg',
                    ),
                    other_documents=SimpleUploadedFile(
                        'other-doc.pdf',
                        make_test_pdf_bytes('Other Document'),
                        content_type='application/pdf',
                    ),
                )
                Certificate.objects.create(
                    faculty=faculty,
                    certificate_type='NPTEL',
                    certificate_file=SimpleUploadedFile(
                        'nptel.pdf',
                        make_test_pdf_bytes('Certificate Record'),
                        content_type='application/pdf',
                    ),
                )
                ResearchPublication.objects.create(
                    faculty=faculty,
                    research_type='journal',
                    title='Merged Research Publication',
                    publication_year=2024,
                    proof_document=SimpleUploadedFile(
                        'research-proof.pdf',
                        make_test_pdf_bytes('Research Proof'),
                        content_type='application/pdf',
                    ),
                )
                FDP.objects.create(
                    faculty=faculty,
                    fdp_type='fdp',
                    title='Merged FDP',
                    from_date=date(2024, 6, 1),
                    to_date=date(2024, 6, 2),
                    certificate=SimpleUploadedFile(
                        'fdp-proof.pdf',
                        make_test_pdf_bytes('FDP Proof'),
                        content_type='application/pdf',
                    ),
                )

                merged_pdf = dashboard_views.merge_certificates_with_pdf_bytes(
                    make_test_pdf_bytes('Faculty Profile'),
                    faculty,
                )

        self.assertIsNotNone(merged_pdf)
        self.assertGreaterEqual(len(PdfReader(io.BytesIO(merged_pdf)).pages), 5)

    @patch('dashboard.views.download_remote_asset')
    def test_merge_certificates_with_pdf_bytes_uses_faculty_upload_history_for_fdp_and_research(self, mock_download_remote_asset):
        def fake_download(url, default_suffix='.pdf'):
            label = 'Generic Upload'
            if 'fdp-history' in url:
                label = 'FDP Upload History'
            elif 'research-history' in url:
                label = 'Research Upload History'
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(make_test_pdf_bytes(label))
                return temp_pdf.name, True

        mock_download_remote_asset.side_effect = fake_download

        faculty = Faculty.objects.create(
            staff_name='History Merge Faculty',
            employee_code='F9002H',
            department='IT',
            designation='Assistant Professor',
        )
        FDP.objects.create(
            faculty=faculty,
            fdp_type='fdp',
            title='History FDP',
            from_date=date(2024, 7, 1),
            to_date=date(2024, 7, 2),
        )
        ResearchPublication.objects.create(
            faculty=faculty,
            research_type='journal',
            title='History Research',
            publication_year=2024,
        )
        CloudinaryUpload.objects.create(
            faculty=faculty,
            upload_type='fdp_certificate',
            cloudinary_url='https://example.com/fdp-history.pdf',
            public_id='fdp-history',
            resource_type='raw',
        )
        CloudinaryUpload.objects.create(
            faculty=faculty,
            upload_type='research_proof',
            cloudinary_url='https://example.com/research-history.pdf',
            public_id='research-history',
            resource_type='raw',
        )

        merged_pdf = dashboard_views.merge_certificates_with_pdf_bytes(
            make_test_pdf_bytes('Faculty Profile'),
            faculty,
        )

        self.assertIsNotNone(merged_pdf)
        self.assertGreaterEqual(len(PdfReader(io.BytesIO(merged_pdf)).pages), 3)

    @patch('dashboard.views.download_remote_asset')
    def test_merge_certificates_with_pdf_bytes_deduplicates_shared_research_and_fdp_uploads(self, mock_download_remote_asset):
        def fake_download(url, default_suffix='.pdf'):
            label = 'Generic Upload'
            if 'shared-fdp' in url:
                label = 'FDP Shared Upload'
            elif 'shared-research' in url:
                label = 'Research Shared Upload'
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(make_test_pdf_bytes(label))
                return temp_pdf.name, True

        mock_download_remote_asset.side_effect = fake_download

        faculty = Faculty.objects.create(
            staff_name='Shared Upload Faculty',
            employee_code='F9002D',
            department='IT',
            designation='Assistant Professor',
            fdp_certificate_url='https://example.com/shared-fdp.pdf',
            research_proof_url='https://example.com/shared-research.pdf',
        )
        FDP.objects.create(
            faculty=faculty,
            fdp_type='fdp',
            title='Shared FDP',
            from_date=date(2024, 8, 1),
            to_date=date(2024, 8, 2),
            certificate_url='https://example.com/shared-fdp.pdf',
        )
        ResearchPublication.objects.create(
            faculty=faculty,
            research_type='journal',
            title='Shared Research',
            publication_year=2024,
            proof_document_url='https://example.com/shared-research.pdf',
        )

        merged_pdf = dashboard_views.merge_certificates_with_pdf_bytes(
            make_test_pdf_bytes('Faculty Profile'),
            faculty,
        )

        self.assertIsNotNone(merged_pdf)
        reader = PdfReader(io.BytesIO(merged_pdf))
        self.assertEqual(len(reader.pages), 3)

        combined_text = '\n'.join((page.extract_text() or '') for page in reader.pages)
        self.assertEqual(combined_text.count('Research Shared Upload'), 1)
        self.assertEqual(combined_text.count('FDP Shared Upload'), 1)

    @patch('dashboard.views.build_faculty_profile_pdf_bytes', return_value=make_test_pdf_bytes('Generated Faculty PDF'))
    @patch('dashboard.views.is_cloudinary_configured', return_value=False)
    def test_generate_faculty_pdf_route_persists_pdf_document(
        self,
        _mock_cloudinary_enabled,
        _mock_generate_faculty_pdf_bytes,
    ):
        user = get_user_model().objects.create_user(
            username='faculty-generator',
            email='faculty-generator@example.com',
            password='secret123',
        )
        self.client.force_login(user)

        faculty = Faculty.objects.create(
            staff_name='Faculty Generator',
            employee_code='F9003',
            department='IT',
            designation='Assistant Professor',
        )

        response = self.client.get(
            reverse('dashboard:generate_faculty_pdf', args=[faculty.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])

        faculty.refresh_from_db()
        self.assertTrue(bool(faculty.pdf_document))

    @patch('dashboard.views.build_faculty_profile_pdf_bytes', return_value=make_test_pdf_bytes('Fresh Faculty PDF'))
    @patch('dashboard.views.is_cloudinary_configured', return_value=False)
    def test_faculty_pdf_view_regenerates_and_persists_pdf_document(
        self,
        _mock_cloudinary_enabled,
        mock_generate_faculty_pdf_bytes,
    ):
        user = get_user_model().objects.create_user(
            username='faculty-pdf-refresh',
            email='faculty-pdf-refresh@example.com',
            password='secret123',
        )
        self.client.force_login(user)

        faculty = Faculty.objects.create(
            staff_name='Faculty Refresh',
            employee_code='F9004',
            department='IT',
            designation='Assistant Professor',
        )

        response = self.client.get(
            reverse('dashboard:faculty_pdf', args=[faculty.id]),
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline;', response['Content-Disposition'])
        mock_generate_faculty_pdf_bytes.assert_called_once_with(faculty)

        faculty.refresh_from_db()
        self.assertTrue(bool(faculty.pdf_document))

    @patch('dashboard.views.build_faculty_profile_pdf_bytes', side_effect=RuntimeError('fresh generation failed'))
    @patch('dashboard.views.download_remote_asset', side_effect=RuntimeError('stale cloudinary asset'))
    def test_faculty_pdf_view_and_download_fall_back_to_saved_pdf_document(
        self,
        _mock_download_remote_asset,
        _mock_generate_faculty_pdf_bytes,
    ):
        user = get_user_model().objects.create_user(
            username='faculty-pdf-viewer',
            email='faculty-pdf-viewer@example.com',
            password='secret123',
        )
        self.client.force_login(user)

        faculty = Faculty.objects.create(
            staff_name='Saved Faculty PDF',
            employee_code='F9005',
            department='IT',
            designation='Assistant Professor',
            cloudinary_pdf_url='https://example.com/faculty-stale.pdf',
        )
        faculty.pdf_document.save(
            'faculty_saved.pdf',
            ContentFile(make_test_pdf_bytes('Saved Faculty PDF')),
            save=True,
        )

        view_response = self.client.get(
            reverse('dashboard:faculty_pdf', args=[faculty.id]),
            secure=True,
        )
        download_response = self.client.get(
            reverse('dashboard:download_faculty_pdf', args=[faculty.id]),
            secure=True,
        )

        self.assertEqual(view_response.status_code, 200)
        self.assertEqual(view_response['Content-Type'], 'application/pdf')
        self.assertIn('inline;', view_response['Content-Disposition'])

        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', download_response['Content-Disposition'])


@override_settings(SECURE_SSL_REDIRECT=False)
class PhonePeProjectDownloadTests(TestCase):
    def setUp(self):
        session = self.client.session
        session['payment_test'] = True
        session.save()
        self.payment = ProjectDownloadPayment.objects.create(
            merchant_order_id='ECPRJ-TEST-ORDER',
            session_key=session.session_key,
            amount_paise=dashboard_views.PROJECT_DOWNLOAD_PRICE_PAISE,
            status='PENDING',
        )

    @patch('dashboard.views._phonepe_access_token', return_value='test-token')
    @patch('dashboard.views.requests.get')
    def test_completed_status_without_exact_order_and_amount_stays_locked(
        self,
        mock_get,
        _mock_token,
    ):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {'state': 'COMPLETED'}
        mock_get.return_value = response

        paid = dashboard_views._phonepe_verify_payment(self.payment)

        self.assertFalse(paid)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'PENDING')
        self.assertIsNone(self.payment.verified_at)

    @patch('dashboard.views._phonepe_access_token', return_value='test-token')
    @patch('dashboard.views.requests.get')
    def test_exact_completed_order_and_amount_unlocks_payment(self, mock_get, _mock_token):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'merchantOrderId': self.payment.merchant_order_id,
            'state': 'COMPLETED',
            'amount': self.payment.amount_paise,
        }
        mock_get.return_value = response

        paid = dashboard_views._phonepe_verify_payment(self.payment)

        self.assertTrue(paid)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'COMPLETED')
        self.assertIsNotNone(self.payment.verified_at)

    @patch('dashboard.views._phonepe_verify_payment')
    def test_callback_rejects_invalid_authorization(self, mock_verify):
        with patch.dict(os.environ, {
            'PHONEPE_CALLBACK_USERNAME': 'callback-user',
            'PHONEPE_CALLBACK_PASSWORD': 'callback-password',
        }):
            response = self.client.post(
                reverse('dashboard:phonepe_payment_callback'),
                data=json.dumps({'payload': {'merchantOrderId': self.payment.merchant_order_id}}),
                content_type='application/json',
                HTTP_AUTHORIZATION='forged',
            )

        self.assertEqual(response.status_code, 401)
        mock_verify.assert_not_called()

    @patch('dashboard.views._phonepe_verify_payment', return_value=True)
    def test_authenticated_callback_rechecks_phonepe_status(self, mock_verify):
        username = 'callback-user'
        password = 'callback-password'
        authorization = hashlib.sha256(f'{username}:{password}'.encode('utf-8')).hexdigest()
        with patch.dict(os.environ, {
            'PHONEPE_CALLBACK_USERNAME': username,
            'PHONEPE_CALLBACK_PASSWORD': password,
        }):
            response = self.client.post(
                reverse('dashboard:phonepe_payment_callback'),
                data=json.dumps({'payload': {'merchantOrderId': self.payment.merchant_order_id}}),
                content_type='application/json',
                HTTP_AUTHORIZATION=authorization,
            )

        self.assertEqual(response.status_code, 204)
        mock_verify.assert_called_once()
        self.assertEqual(mock_verify.call_args.args[0].pk, self.payment.pk)

    @patch('dashboard.views._phonepe_verify_payment', return_value=False)
    def test_unverified_payment_cannot_download_zip(self, _mock_verify):
        response = self.client.get(
            reverse('dashboard:download_engineeringcollege_project'),
            {'order': self.payment.merchant_order_id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:project_download_payment'), response['Location'])
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.download_count, 0)

    @patch('dashboard.views._iter_engineeringcollege_source_files', return_value=[])
    @patch('dashboard.views._phonepe_verify_payment', return_value=True)
    def test_verified_payment_downloads_zip_and_counts_once(self, _mock_verify, _mock_files):
        response = self.client.get(
            reverse('dashboard:download_engineeringcollege_project'),
            {'order': self.payment.merchant_order_id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.download_count, 1)

    def test_payment_url_qr_is_embedded_png(self):
        qr_data_uri = dashboard_views._payment_url_qr_data_uri(
            'https://mercury.phonepe.com/transact/checkout-test'
        )

        self.assertTrue(qr_data_uri.startswith('data:image/png;base64,'))
        self.assertGreater(len(qr_data_uri), 100)

    def test_non_phonepe_url_is_never_rendered_as_payment_qr(self):
        self.assertEqual(
            dashboard_views._payment_url_qr_data_uri('https://example.com/fake-payment'),
            '',
        )

    @patch('dashboard.views._phonepe_create_payment')
    def test_show_qr_action_creates_order_and_returns_to_payment_page(self, mock_create):
        mock_create.return_value = 'https://mercury.phonepe.com/transact/checkout-test'
        with patch.dict(os.environ, {
            'PHONEPE_CLIENT_ID': 'test-client',
            'PHONEPE_CLIENT_SECRET': 'test-secret',
        }):
            response = self.client.post(
                reverse('dashboard:initiate_project_download_payment'),
                {'checkout_mode': 'qr'},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard:project_download_payment'), response['Location'])
        self.assertIn('order=', response['Location'])

    @patch('dashboard.views._phonepe_verify_payment', return_value=False)
    def test_pending_payment_page_displays_hosted_checkout_qr(self, _mock_verify):
        self.payment.payment_url = 'https://mercury.phonepe.com/transact/checkout-test'
        self.payment.save(update_fields=['payment_url', 'updated_at'])

        response = self.client.get(
            reverse('dashboard:project_download_payment'),
            {'order': self.payment.merchant_order_id},
        )

        self.assertContains(response, 'data:image/png;base64,')
        self.assertContains(response, 'Open PhonePe Checkout')
