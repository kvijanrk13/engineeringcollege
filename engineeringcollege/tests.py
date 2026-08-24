from django.test import SimpleTestCase


class MoocsPageTests(SimpleTestCase):
    def test_moocs_exam_console_renders(self):
        response = self.client.get("/MOOCS")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Computer Science Mock Examination")
        self.assertContains(response, "Question palette")
        self.assertContains(response, "/static/moocs/moocs.js")
        self.assertContains(response, "/static/moocs/textbook_questions.js")
        self.assertContains(response, "/static/moocs/feedback.css")
