from django.test import TestCase, override_settings
from django.urls import reverse


class CarPriceGoogleSignInTests(TestCase):
    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_maruti_prices_redirects_to_google_sign_in_without_verified_session(self):
        response = self.client.get(reverse("maruti-prices"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("dashboard:google_login"), response["Location"])
        self.assertIn("continue=1", response["Location"])

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_maruti_prices_accepts_verified_google_oauth_session(self):
        session = self.client.session
        session["google_oauth_email"] = "student@college.edu"
        session["car_price_gmail_verified"] = True
        session.save()

        response = self.client.get(reverse("maruti-prices"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "K-RADIUS Prediction")
