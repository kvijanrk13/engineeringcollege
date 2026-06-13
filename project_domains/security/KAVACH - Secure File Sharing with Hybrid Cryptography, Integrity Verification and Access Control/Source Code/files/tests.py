from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import PlainTextFile


class PlainTextFileSharingTests(TestCase):
    def test_profile_upload_requires_receiver_gmail_and_shares_file(self):
        sender = User.objects.create_user(
            username="sender",
            email="sender@gmail.com",
            password="pass12345",
        )
        self.client.force_login(sender)

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "receiver_email": "receiver@gmail.com",
                "uploaded_file": SimpleUploadedFile(
                    "note.txt",
                    b"hello receiver",
                    content_type="text/plain",
                ),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        shared_file = PlainTextFile.objects.get()
        self.assertEqual(shared_file.owner, sender)
        self.assertEqual(shared_file.receiver_email, "receiver@gmail.com")
        self.assertContains(response, "Text file encrypted and shared with receiver@gmail.com.")

    def test_receiver_profile_lists_and_decrypts_shared_file(self):
        sender = User.objects.create_user(
            username="sender",
            email="sender@gmail.com",
            password="pass12345",
        )
        receiver = User.objects.create_user(
            username="receiver",
            email="receiver@gmail.com",
            password="pass12345",
        )
        self.client.force_login(sender)
        upload_response = self.client.post(
            reverse("accounts:profile"),
            {
                "receiver_email": "receiver@gmail.com",
                "uploaded_file": SimpleUploadedFile(
                    "note.txt",
                    b"hello receiver",
                    content_type="text/plain",
                ),
            },
        )
        self.assertEqual(upload_response.status_code, 302)
        shared_file = PlainTextFile.objects.get()

        self.client.force_login(receiver)
        profile_response = self.client.get(reverse("accounts:profile"))
        self.assertContains(profile_response, "Files Received For You")
        self.assertContains(profile_response, "note.txt")
        self.assertContains(profile_response, "hello receiver")
        self.assertContains(profile_response, reverse("files:download", args=[shared_file.id]))

        self.client.logout()
        self.assertTrue(self.client.login(username="receiver", password="pass12345"))
        later_profile_response = self.client.get(reverse("accounts:profile"))
        self.assertContains(later_profile_response, "Files Received For You")
        self.assertContains(later_profile_response, "note.txt")
        self.assertContains(later_profile_response, "hello receiver")

        download_response = self.client.get(reverse("files:download", args=[shared_file.id]))
        self.assertEqual(download_response.status_code, 200)
        self.assertEqual(download_response.content, b"hello receiver")

    def test_non_receiver_cannot_download_shared_file(self):
        sender = User.objects.create_user(
            username="sender",
            email="sender@gmail.com",
            password="pass12345",
        )
        other = User.objects.create_user(
            username="other",
            email="other@gmail.com",
            password="pass12345",
        )
        self.client.force_login(sender)
        self.client.post(
            reverse("accounts:profile"),
            {
                "receiver_email": "receiver@gmail.com",
                "uploaded_file": SimpleUploadedFile(
                    "note.txt",
                    b"hello receiver",
                    content_type="text/plain",
                ),
            },
        )
        shared_file = PlainTextFile.objects.get()

        self.client.force_login(other)
        response = self.client.get(reverse("files:download", args=[shared_file.id]))

        self.assertEqual(response.status_code, 404)
