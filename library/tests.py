import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from student.models import Department, Student

from .models import Author, Book, Fine, Issue, LibraryStat
from .utilities import calcFine, getmybooks


class LibraryWeek6Tests(TestCase):
    """Small, student-friendly unit and integration suite documented in Week 6."""

    def setUp(self):
        self.department = Department.objects.create(name="CSE(AI&ML)")
        self.user = User.objects.create_user(
            username="23CSE001",
            password="Test@12345",
        )
        self.student = Student.objects.create(
            first_name="Test",
            last_name="Student",
            department=self.department,
            student_id=self.user,
        )
        self.admin = User.objects.create_superuser(
            username="librarian",
            email="librarian@example.com",
            password="Admin@12345",
        )
        self.author = Author.objects.create(
            name="Robert C. Martin",
            description="Software author",
        )
        self.book = Book.objects.create(
            name="Clean Code",
            author=self.author,
            image="books/clean-code.png",
            category="TEXT",
        )

    def test_valid_student_login(self):
        response = self.client.post(
            "/aeclibrary/student/login/",
            {"username": "23CSE001", "password": "Test@12345"},
        )
        self.assertRedirects(response, "/aeclibrary/")
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(self.user.pk))

    def test_invalid_student_login(self):
        response = self.client.post(
            "/aeclibrary/student/login/",
            {"username": "23CSE001", "password": "wrong-password"},
        )
        self.assertRedirects(response, "/aeclibrary/student/signup/")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_home_redirects_anonymous_user(self):
        response = self.client.get("/aeclibrary/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/aeclibrary/student/signup/"))

    def test_search_finds_book(self):
        self.client.force_login(self.user)
        response = self.client.get(
            "/aeclibrary/search/",
            {"search-query": "clean"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Code")

    def test_student_can_request_book_once(self):
        self.client.force_login(self.user)
        self.client.get(f"/aeclibrary/request-book-issue/{self.book.pk}/")
        self.client.get(f"/aeclibrary/request-book-issue/{self.book.pk}/")
        self.assertEqual(
            Issue.objects.filter(student=self.student, book=self.book).count(),
            1,
        )

    def test_admin_can_approve_issue(self):
        issue = Issue.objects.create(student=self.student, book=self.book)
        self.client.force_login(self.admin)
        response = self.client.get(f"/aeclibrary/issuebook/{issue.pk}/")
        self.assertRedirects(response, "/aeclibrary/all-issues/")
        issue.refresh_from_db()
        self.assertTrue(issue.issued)
        self.assertIsNotNone(issue.issued_at)
        self.assertGreater(issue.return_date, timezone.now())

    def test_return_before_due_date_creates_no_fine(self):
        issue = Issue.objects.create(
            student=self.student,
            book=self.book,
            issued=True,
            issued_at=timezone.now(),
            return_date=timezone.now() + datetime.timedelta(days=5),
        )
        self.client.force_login(self.admin)
        self.client.get(f"/aeclibrary/returnbook/{issue.pk}/")
        issue.refresh_from_db()
        self.assertTrue(issue.returned)
        self.assertFalse(Fine.objects.filter(issue=issue).exists())

    def test_author_and_book_string_values(self):
        self.assertEqual(str(self.author), "Robert C. Martin")
        self.assertEqual(str(self.book), "Clean Code")

    def test_overdue_issue_calculates_fine(self):
        issue = Issue.objects.create(
            student=self.student,
            book=self.book,
            issued=True,
            issued_at=timezone.now() - datetime.timedelta(days=10),
            return_date=timezone.now() - datetime.timedelta(days=3),
        )
        calcFine(issue)
        fine = Fine.objects.get(issue=issue)
        self.assertEqual(fine.amount, 30)

    def test_getmybooks_separates_requested_book(self):
        Issue.objects.create(student=self.student, book=self.book, issued=False)
        requested, issued = getmybooks(self.user)
        self.assertIn(self.book, requested)
        self.assertNotIn(self.book, issued)

    def test_issue_signal_updates_library_stat(self):
        Issue.objects.create(
            student=self.student,
            book=self.book,
            issued=True,
            return_date=timezone.now() + datetime.timedelta(days=5),
        )
        stat = LibraryStat.objects.get(pk=1)
        self.assertEqual(stat.borrowed_books, 1)

    def test_documentation_contains_week6(self):
        response = self.client.get("/aeclibrary/documentation/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Week 4 and Week 5")
        self.assertContains(response, "Week 6 - Unit Testing and Integration Testing")
