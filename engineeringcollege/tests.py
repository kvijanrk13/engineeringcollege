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
        self.assertContains(response, "Set 2")
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
        self.assertContains(response, "/static/moocs/moocs.js")
        self.assertContains(response, "/static/moocs/textbook_questions.js")
        self.assertContains(response, "/static/moocs/feedback.css")

    def test_moocs_logout_closes_exam_session(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_gmail_email"] = "student@gmail.com"
        session["moocs_exam_lock"] = True
        session.save()

        response = self.client.get("/MOOCS/logout/")

        self.assertRedirects(response, "/MOOCS", fetch_redirect_response=False)
        self.assertNotIn("moocs_gmail_verified", self.client.session)
        self.assertNotIn("moocs_exam_lock", self.client.session)

    def test_moocs_lock_redirects_other_site_pages(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_exam_lock"] = True
        session.save()

        response = self.client.get("/")

        self.assertRedirects(response, "/MOOCS", fetch_redirect_response=False)

    def test_moocs_lock_allows_exam_and_static_assets(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_exam_lock"] = True
        session.save()

        self.assertEqual(self.client.get("/MOOCS").status_code, 200)
        self.assertNotEqual(
            self.client.get("/static/moocs/moocs.js").status_code,
            302,
        )

    def test_moocs_lock_blocks_direct_static_page_navigation(self):
        session = self.client.session
        session["moocs_gmail_verified"] = True
        session["moocs_exam_lock"] = True
        session.save()

        response = self.client.get(
            "/static/moocs/moocs.js",
            HTTP_SEC_FETCH_DEST="document",
        )

        self.assertRedirects(response, "/MOOCS", fetch_redirect_response=False)
