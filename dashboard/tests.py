from django.test import TestCase
from django.urls import reverse

class DashboardTests(TestCase):
    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IT DEPARTMENT')