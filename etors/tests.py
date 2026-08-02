from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Booking, Passenger, Station, Train
from .services import train_availability


class EtorsTests(TestCase):
    def setUp(self):
        source = Station.objects.create(code="TST", name="Test Source", city="Source")
        destination = Station.objects.create(code="TEN", name="Test End", city="End")
        self.train = Train.objects.create(
            number="99999",
            name="Test Express",
            source=source,
            destination=destination,
            departure_time=time(8),
            arrival_time=time(12),
            duration="4h",
            seat_capacity=2,
            sleeper_fare=Decimal("250"),
            ac_fare=Decimal("700"),
        )
        self.journey_date = date.today() + timedelta(days=2)

    def test_home_and_train_search(self):
        response = self.client.get(
            reverse("etors:home"),
            {
                "source": self.train.source_id,
                "destination": self.train.destination_id,
                "journey_date": self.journey_date.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Express")
        self.assertContains(response, "Login with Gmail")
        self.assertContains(response, "target=etors")
        self.assertContains(response, "ETORS Assistant")
        self.assertContains(response, reverse("etors:chatbot"))

    def test_demo_stations_routes_and_calendar_are_available(self):
        khammam = Station.objects.get(code="KMM")
        vijayawada = Station.objects.get(code="BZA")
        secunderabad = Station.objects.get(code="SC")
        requested_routes = {
            (khammam.pk, vijayawada.pk),
            (vijayawada.pk, khammam.pk),
            (vijayawada.pk, secunderabad.pk),
            (secunderabad.pk, vijayawada.pk),
            (khammam.pk, secunderabad.pk),
            (secunderabad.pk, khammam.pk),
        }
        demo_routes = set(
            Train.objects.filter(number__in=[f"0900{i}" for i in range(1, 7)])
            .values_list("source_id", "destination_id")
        )
        self.assertEqual(demo_routes, requested_routes)

        response = self.client.get(reverse("etors:home"))
        self.assertContains(response, "Khammam (KMM)")
        self.assertContains(response, 'type="date"')
        self.assertContains(response, f'min="{date.today().isoformat()}"')
        self.assertContains(
            response,
            f'max="{(date.today() + timedelta(days=120)).isoformat()}"',
        )

    def test_chatbot_answers_current_features(self):
        response = self.client.post(
            reverse("etors:chatbot"),
            {"question": "What features and services are available?"},
        )
        self.assertEqual(response.status_code, 200)
        answer = response.json()["answer"]
        self.assertIn("Route and journey-date search", answer)
        self.assertIn("PNR generation, lookup, and cancellation", answer)

    def test_chatbot_answers_booking_and_rejects_invalid_questions(self):
        response = self.client.post(
            reverse("etors:chatbot"),
            {"question": "How can I book a ticket?"},
        )
        self.assertContains(response, "10-digit PNR")

        response = self.client.post(reverse("etors:chatbot"), {"question": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Enter a question about ETORS.")

    def test_authenticated_navigation_and_logout(self):
        user = User.objects.create_user(
            username="gmail-user",
            email="traveller@gmail.com",
            first_name="Traveller",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("etors:home"))
        self.assertContains(response, "Hi, Traveller")
        self.assertContains(response, "Logout")
        self.assertNotContains(response, "College Home")

        response = self.client.get(reverse("etors:logout"))
        self.assertRedirects(response, reverse("etors:home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_booking_generates_pnr_and_passenger(self):
        response = self.client.post(
            reverse(
                "etors:book",
                args=[self.train.pk, self.journey_date.isoformat()],
            ),
            {
                "travel_class": "SL",
                "contact_name": "Asha Kumar",
                "contact_email": "asha@example.com",
                "contact_phone": "9876543210",
                "passenger_name": "Asha Kumar",
                "passenger_age": 24,
                "passenger_gender": "F",
                "berth_preference": "Lower",
            },
        )
        booking = Booking.objects.get()
        self.assertRedirects(response, reverse("etors:pnr_detail", args=[booking.pnr]))
        self.assertEqual(len(booking.pnr), 10)
        self.assertEqual(booking.passengers.count(), 1)
        self.assertEqual(train_availability(self.train, self.journey_date), 1)

    def test_cancellation_releases_availability(self):
        booking = Booking.objects.create(
            train=self.train,
            journey_date=self.journey_date,
            travel_class="SL",
            contact_name="Ravi",
            contact_email="ravi@example.com",
            contact_phone="9876543210",
            total_fare=Decimal("250"),
        )
        Passenger.objects.create(
            booking=booking,
            name="Ravi",
            age=30,
            gender="M",
            seat_number="S001",
        )
        self.assertEqual(train_availability(self.train, self.journey_date), 1)
        response = self.client.post(reverse("etors:cancel_booking", args=[booking.pnr]))
        booking.refresh_from_db()
        self.assertRedirects(response, reverse("etors:pnr_detail", args=[booking.pnr]))
        self.assertEqual(booking.status, "CANCELLED")
        self.assertEqual(train_availability(self.train, self.journey_date), 2)

    def test_invalid_pnr_returns_404(self):
        response = self.client.get(reverse("etors:pnr_detail", args=["0000000000"]))
        self.assertEqual(response.status_code, 404)
