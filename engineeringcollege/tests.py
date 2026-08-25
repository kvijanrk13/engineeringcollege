from django.test import TestCase, override_settings


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

    def test_moocs_exam_console_renders(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_gmail_email"] = "student@gmail.com"
        session.save()
        response = self.client.get("/MOOCS")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set 1")
        self.assertContains(response, "Data Structures")
        self.assertContains(response, "Data Mining")
        self.assertContains(response, "Discrete Mathematics")
        self.assertContains(response, "Data Communications and Networking")
        self.assertContains(response, "Java Programming")
        self.assertContains(response, "Database Management Systems")
        self.assertContains(response, "Computer Science Mock Examination")
        self.assertContains(response, "Question palette")
        self.assertContains(response, "/static/moocs/moocs.js")
        self.assertContains(response, "/static/moocs/textbook_questions.js")
        self.assertContains(response, "/static/moocs/feedback.css")

    def test_moocs_logout_closes_exam_session(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_gmail_email"] = "student@gmail.com"
        session.save()

        response = self.client.get("/MOOCS/logout/")

        self.assertRedirects(response, "/MOOCS", fetch_redirect_response=False)
        self.assertNotIn("moocs_gmail_verified", self.client.session)
