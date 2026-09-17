import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from dashboard.models import MoocsPayment, MoocsVisitor


@override_settings(
    GOOGLE_OAUTH_CLIENT_ID="test-google-client-id",
    GOOGLE_OAUTH_CLIENT_SECRET="test-google-client-secret",
)
class MoocsPageTests(TestCase):
    def test_moocs_requires_gmail_before_loading_exam(self):
        response = self.client.get("/MOOCS")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Continue with Gmail")
        self.assertContains(response, "target=moocs")
        self.assertNotContains(response, "Question palette")
        self.assertNotContains(response, "/static/moocs/moocs.js")
        self.assertContains(response, "/static/moocs/content_lock.js")
        self.assertContains(response, "/static/moocs/content_lock.css")
        self.assertContains(response, "/static/moocs/moocs.css?v=22")

    def test_moocs_exam_console_renders(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_gmail_email"] = "student@gmail.com"
        session.save()
        response = self.client.get("/MOOCS")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set 1")
        self.assertContains(response, "Set 2")
        self.assertContains(response, "Set 11")
        self.assertContains(response, "Set 20")
        self.assertContains(response, "Set 21")
        self.assertContains(response, "Set 30")
        self.assertContains(response, "Set 41")
        self.assertContains(response, "Set 50")
        self.assertContains(response, "Set 50 — New unique computer-science MCQs (100)")
        self.assertContains(response, 'id="welcome" class="welcome card"')
        self.assertNotContains(response, 'id="welcome" class="welcome card" hidden')
        self.assertContains(response, "Two hundred mixed, syllabus-aligned papers")
        self.assertContains(response, "set <= 200")
        self.assertContains(response, "2014 Paper I + new MCQs (100)")
        self.assertContains(response, "Paper II answer key + new MCQs (100)")
        self.assertContains(response, "New unique computer-science MCQs")
        self.assertContains(response, "Syllabus Coverage")
        self.assertContains(response, "Unit 1: Discrete Structures")
        self.assertContains(response, "Unit 2: Architecture")
        self.assertContains(response, "Unit 3: Programming &amp; Graphics")
        self.assertContains(response, "Unit 4: DBMS &amp; Data Mining")
        self.assertContains(response, "Unit 5: System Software &amp; OS")
        self.assertContains(response, "Unit 6: Software Engineering")
        self.assertContains(response, "Unit 7: Data Structures &amp; Algorithms")
        self.assertContains(response, "Unit 8: TOC &amp; Compilers")
        self.assertContains(response, "Unit 9: Networks")
        self.assertContains(response, "Unit 10: Artificial Intelligence")
        self.assertContains(response, "Computer Science Mock Examination")
        self.assertNotContains(response, "Apply the governing definition carefully before selecting.")
        self.assertNotContains(response, "Analyze the conditions, rule out near-correct alternatives")
        self.assertContains(response, "Question palette")
        self.assertContains(response, 'class="question-number-prefix"')
        self.assertNotContains(response, "Sl.No.")
        self.assertContains(response, "/static/moocs/moocs.js")
        self.assertContains(response, "/static/moocs/content_lock.js")
        self.assertContains(response, "/static/moocs/content_lock.css")
        self.assertContains(response, 'id="moocs-profile-email"')
        self.assertContains(response, "student@gmail.com")
        self.assertContains(response, "/static/moocs/moocs.js?v=47")
        self.assertContains(response, "/static/moocs/extended_sets.js?v=7")
        self.assertContains(response, "/static/moocs/bloom_taxonomy.js?v=2")
        self.assertContains(response, 'id="moocs-signout"')
        self.assertContains(response, 'method="post"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "allowNavigation = true")
        self.assertContains(response, 'id="download-explanations"')
        self.assertContains(response, "Download explanations PDF")
        self.assertContains(response, 'id="reset-exam"')
        self.assertContains(response, "Reset and start from Set 1")
        self.assertContains(response, "/static/moocs/textbook_questions.js")
        self.assertContains(response, "/static/moocs/paper2_answer_key.js")
        self.assertContains(response, "/static/moocs/paper1_2014.js")
        self.assertContains(response, "/static/moocs/d8704_paper_two.js")
        self.assertContains(response, "/static/moocs/pdf_archive_sets.js")
        self.assertContains(response, "/static/moocs/assessment_pattern.js")
        self.assertContains(response, "/static/moocs/gate_archive_sets.js")
        self.assertContains(response, "/static/moocs/feedback.css")

    def test_verified_moocs_session_is_counted_as_a_unique_visitor(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_gmail_email"] = "Student@Gmail.com"
        session.save()

        self.client.get("/MOOCS")
        self.client.get("/MOOCS")

        self.assertEqual(MoocsVisitor.objects.filter(email="student@gmail.com").count(), 1)

    def test_moocs_logout_closes_exam_session(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_gmail_email"] = "student@gmail.com"
        session.save()

        response = self.client.get("/MOOCS/logout/")

        self.assertRedirects(response, "/MOOCS", fetch_redirect_response=False)
        self.assertNotIn("moocs_gmail_verified", self.client.session)

    def test_verified_moocs_session_can_open_other_site_pages(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session.save()

        response = self.client.get("/")

        self.assertNotEqual(response.headers.get("Location"), "/MOOCS")


class MoocsPaymentTests(TestCase):
    def setUp(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_gmail_email"] = "student@gmail.com"
        session.save()

    @override_settings(RAZORPAY_KEY_ID="test_key", RAZORPAY_KEY_SECRET="test_secret")
    @patch("engineeringcollege.moocs_views._create_moocs_order")
    def test_set_3_payment_page_opens_razorpay(self, create_order):
        create_order.return_value = ({"id": "order_test_123"}, 20000)

        response = self.client.get("/MOOCS/payment/?set=3")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unlock Sets 3–200")
        self.assertContains(response, "Open Razorpay payment")
        self.assertContains(response, "order_test_123")

    @override_settings(RAZORPAY_KEY_ID="", RAZORPAY_KEY_SECRET="")
    def test_payment_page_reports_missing_razorpay_configuration(self):
        response = self.client.get("/MOOCS/payment/?set=3")

        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "Razorpay is not configured", status_code=503)

    @override_settings(RAZORPAY_KEY_ID="test_key", RAZORPAY_KEY_SECRET="test_secret")
    @patch("engineeringcollege.moocs_views._get_razorpay_client")
    def test_set_3_order_uses_two_hundred_rupees(self, get_client):
        get_client.return_value.order.create.return_value = {"id": "order_test_123"}

        response = self.client.post(
            "/MOOCS/payment/create-order/",
            data=json.dumps({"set_number": 3, "email": "student@gmail.com"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["amount"], 20000)
        self.assertEqual(payload["set_number"], 3)
        payment = MoocsPayment.objects.get(email="student@gmail.com", set_number=3)
        self.assertEqual(payment.amount, 200.00)
        self.assertEqual(payment.razorpay_order_id, "order_test_123")

    @patch("engineeringcollege.moocs_views._get_razorpay_client")
    def test_set_3_verification_marks_premium_sets_paid(self, get_client):
        get_client.return_value.utility.verify_payment_signature.return_value = None
        get_client.return_value.payment.fetch.return_value = {
            "order_id": "order_test_123",
            "status": "captured",
        }
        MoocsPayment.objects.create(
            email="student@gmail.com",
            set_number=3,
            amount=200.00,
            razorpay_order_id="order_test_123",
            status="pending",
        )

        response = self.client.post(
            "/MOOCS/payment/verify/",
            data=json.dumps({
                "set_number": 3,
                "email": "student@gmail.com",
                "razorpay_payment_id": "pay_test_123",
                "razorpay_order_id": "order_test_123",
                "razorpay_signature": "signature_test",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payment = MoocsPayment.objects.get(email="student@gmail.com", set_number=3)
        self.assertEqual(payment.status, "completed")
        self.assertEqual(payment.razorpay_payment_id, "pay_test_123")
