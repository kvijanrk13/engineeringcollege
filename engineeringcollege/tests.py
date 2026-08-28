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
        self.assertContains(response, "/static/moocs/content_lock.js")
        self.assertContains(response, "/static/moocs/content_lock.css")

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
        self.assertContains(response, "2014 Paper I + new MCQs (100)")
        self.assertContains(response, "Paper II answer key + new MCQs (100)")
        self.assertContains(response, "New questions, no Set 1 repeats")
        self.assertContains(response, "Paper II PYQ + unique textbook questions")
        self.assertContains(response, "UGC-NET syllabus coverage")
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
        self.assertContains(response, "Question palette")
        self.assertContains(response, 'class="question-number-prefix"')
        self.assertNotContains(response, "Sl.No.")
        self.assertContains(response, "/static/moocs/moocs.js")
        self.assertContains(response, "/static/moocs/content_lock.js")
        self.assertContains(response, "/static/moocs/content_lock.css")
        self.assertContains(response, 'id="moocs-profile-email"')
        self.assertContains(response, "student@gmail.com")
        self.assertContains(response, "/static/moocs/moocs.js?v=34")
        self.assertContains(response, 'id="reset-exam"')
        self.assertContains(response, "Reset and start from Set 1")
        self.assertContains(response, "/static/moocs/textbook_questions.js")
        self.assertContains(response, "/static/moocs/paper2_answer_key.js")
        self.assertContains(response, "/static/moocs/paper1_2014.js")
        self.assertContains(response, "/static/moocs/d8704_paper_two.js")
        self.assertContains(response, "/static/moocs/pdf_archive_sets.js")
        self.assertContains(response, "/static/moocs/assessment_pattern.js")
        self.assertContains(response, "/static/moocs/feedback.css")

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
