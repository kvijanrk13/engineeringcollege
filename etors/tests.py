from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, CabBooking, CabCallLog, Passenger, Station, Train
from .services import cab_fare_for, fare_for, train_availability


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

    def login_etors_passenger(self):
        user = User.objects.create_user(
            username=f"gmail-passenger-{User.objects.count()}",
            email=f"passenger{User.objects.count()}@gmail.com",
        )
        self.client.force_login(user)
        session = self.client.session
        session["etors_gmail_login"] = True
        session.save()
        return user

    def test_ticket_booking_requires_verified_gmail_login(self):
        book_url = reverse("etors:book", args=[self.train.pk, self.journey_date.isoformat()])
        response = self.client.get(book_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("dashboard:google_login"), response.url)
        self.assertIn("target=etors", response.url)
        self.assertFalse(Booking.objects.exists())

        ordinary_user = User.objects.create_user(username="ordinary", email="ordinary@example.com")
        self.client.force_login(ordinary_user)
        response = self.client.get(book_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("dashboard:google_login"), response.url)

        session = self.client.session
        session["etors_gmail_login"] = True
        session.save()
        self.assertEqual(self.client.get(book_url).status_code, 200)

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
        self.assertContains(response, "From search to seat in four simple steps")
        self.assertContains(response, "indian-railways-hero.jpg")

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
        self.assertIn("Verified Gmail login required", answer)
        self.assertIn("General, Sleeper, 1A, 2A, 3A, and 3E", answer)
        self.assertIn("Privacy-protected cab dispatch", answer)
        self.assertIn("1800-000-3877", answer)

    def test_chatbot_answers_every_recent_etors_feature(self):
        cases = {
            "Can children travel and who receives a berth?": ("five", "older than 5"),
            "Which travel classes and fares are available?": ("General", "3E"),
            "Why is Gmail login required for booking?": ("verified Gmail", "cannot book"),
            "How is PNR status protected?": ("registered mobile", "PNR alone"),
            "Explain passenger privacy from the cab driver and pickup OTP": ("no passenger identity", "pickup OTP"),
            "What train and cab insurance is provided?": ("₹0.45", "₹10"),
            "Which dummy payment methods can I use?": ("UPI", "net banking"),
            "How does BOOKMYCAB reach the station?": ("20 minutes", "Mini"),
            "Give both customer care helpline numbers": ("1800-000-3877", "1800-000-2222"),
        }
        for question, expected_parts in cases.items():
            with self.subTest(question=question):
                answer = self.client.post(
                    reverse("etors:chatbot"), {"question": question}
                ).json()["answer"]
                for expected in expected_parts:
                    self.assertIn(expected, answer)

    def test_chatbot_answers_booking_and_rejects_invalid_questions(self):
        response = self.client.post(
            reverse("etors:chatbot"),
            {"question": "How can I book a ticket?"},
        )
        self.assertContains(response, "10-digit PNR")

        response = self.client.post(reverse("etors:chatbot"), {"question": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Enter a question about ETORS.")

    def test_documentation_button_links_to_week1_week2_and_week3(self):
        response = self.client.get(reverse("etors:home"))
        self.assertContains(response, "DOCUMENTATION")
        self.assertContains(response, reverse("etors:documentation"))

        docs_response = self.client.get(reverse("etors:documentation"))
        self.assertEqual(docs_response.status_code, 200)
        self.assertContains(docs_response, "Week 1")
        self.assertContains(docs_response, "Week 2")
        self.assertContains(docs_response, "Week 3")
        self.assertContains(docs_response, "ETORS")
        self.assertContains(docs_response, "Problem Statement")
        self.assertContains(docs_response, "Software Requirements Document")
        self.assertContains(docs_response, "Software Design Document")
        self.assertContains(docs_response, "Functional Requirements")
        self.assertContains(docs_response, "System Architecture")
        self.assertContains(docs_response, 'href="#week-2"')
        self.assertContains(docs_response, 'href="#week-3"')

    def test_week1_includes_the_supplied_srd_content(self):
        response = self.client.get(reverse("etors:documentation"))
        content = response.content.decode()
        week1 = content.split('id="week-1"', 1)[1].split('id="week-2"', 1)[0]

        self.assertIn("E-TICKETING", week1)
        self.assertIn("Software Requirements Document", week1)
        self.assertIn("User registration and login", week1)
        self.assertIn("Accessibility for people with disabilities", week1)
        self.assertIn("Organizational Requirements", week1)
        self.assertIn("External Requirements", week1)
        self.assertIn("Interface Specification", week1)

    def test_week2_srd_describes_the_implemented_etors_workflow(self):
        response = self.client.get(reverse("etors:documentation"))
        content = response.content.decode()
        week2 = content.split('id="week-2"', 1)[1].split('id="week-3"', 1)[0]

        self.assertIn("verified Gmail", week2)
        self.assertIn("10-digit PNR", week2)
        self.assertIn("registered mobile number", week2)
        self.assertIn("BOOKMYCAB", week2)
        self.assertIn("pickup OTP", week2)
        self.assertIn("Academic Demonstration Notice", week2)
        self.assertNotIn("HTML/JSP/PHP", week2)

    def test_authenticated_navigation_and_logout(self):
        response = self.client.get(reverse("etors:home"))
        self.assertContains(response, "1800-000-3877")
        self.assertContains(response, "1800-000-2222")
        answer = self.client.post(
            reverse("etors:chatbot"),
            {"question": "What are the customer care helpline numbers?"},
        ).json()["answer"]
        self.assertIn("1800-000-3877", answer)
        self.assertIn("1800-000-2222", answer)

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
        self.login_etors_passenger()
        booking_data = {
            "travel_class": "SL",
            "contact_name": "Asha Kumar",
            "contact_email": "asha@example.com",
            "contact_phone": "9876543210",
            "passenger_name": "Asha Kumar",
            "passenger_age": 24,
            "passenger_gender": "F",
            "berth_preference": "Lower",
        }
        response = self.client.post(
            reverse(
                "etors:book",
                args=[self.train.pk, self.journey_date.isoformat()],
            ),
            booking_data,
        )
        self.assertRedirects(response, reverse("etors:payment"))
        self.assertFalse(Booking.objects.exists())

        response = self.client.get(reverse("etors:payment"))
        self.assertContains(response, "Dummy Payment")
        self.assertContains(response, "₹250.00")

        response = self.client.post(
            reverse("etors:payment"),
            {"payment_method": "UPI"},
        )
        booking = Booking.objects.get()
        self.assertContains(response, "PAYMENT SUCCESSFULL")
        self.assertContains(response, "S001")
        self.assertEqual(len(booking.pnr), 10)
        self.assertEqual(booking.passengers.count(), 1)
        self.assertEqual(booking.total_fare, Decimal("250.45"))
        self.assertEqual(booking.train_insurance_premium, Decimal("0.45"))
        self.assertTrue(booking.train_insurance_policy.startswith("TRNINS-"))
        self.assertEqual(train_availability(self.train, self.journey_date), 1)

    def test_payment_requires_pending_booking(self):
        self.login_etors_passenger()
        response = self.client.get(reverse("etors:payment"))
        self.assertRedirects(response, reverse("etors:home"))

    def test_all_travel_classes_have_dummy_fares(self):
        self.assertEqual(
            [code for code, _label in Booking.CLASS_CHOICES],
            ["GN", "SL", "1A", "2A", "3A", "3E"],
        )
        self.assertEqual(fare_for(self.train, "GN"), Decimal("150.00"))
        self.assertEqual(fare_for(self.train, "SL"), Decimal("250.00"))
        self.assertEqual(fare_for(self.train, "3E"), Decimal("630.00"))
        self.assertEqual(fare_for(self.train, "3A"), Decimal("700.00"))
        self.assertEqual(fare_for(self.train, "2A"), Decimal("980.00"))
        self.assertEqual(fare_for(self.train, "1A"), Decimal("1400.00"))

    def test_cab_vehicle_types_prices_and_capacity_validation(self):
        self.assertEqual(
            [code for code, _label in CabBooking.CAB_CHOICES],
            ["BIKE", "AUTO", "MINI", "SEDAN", "SUV", "TEMPO", "BUS"],
        )
        expected_fares = {
            "BIKE": "150.00", "AUTO": "250.00", "MINI": "350.00",
            "SEDAN": "500.00", "SUV": "750.00", "TEMPO": "1200.00", "BUS": "2500.00",
        }
        for vehicle, fare in expected_fares.items():
            self.assertEqual(cab_fare_for(vehicle), Decimal(fare))

        self.login_etors_passenger()
        response = self.client.post(
            reverse("etors:book", args=[self.train.pk, self.journey_date.isoformat()]),
            {
                "travel_class": "SL", "contact_email": "group@example.com",
                "contact_phone": "9876543210", "passenger_name": "Passenger One",
                "passenger_age": 30, "passenger_gender": "M",
                "passenger_2_name": "Passenger Two", "passenger_2_age": 28,
                "passenger_2_gender": "F", "book_cab": "on", "cab_type": "BIKE", "call_recording_consent": "on",
                "cab_drop_address": "Demo Address",
            },
        )
        self.assertContains(response, "This vehicle allows 1 passenger. Select a larger vehicle.")

    def test_multiple_passengers_and_child_berth_rule(self):
        self.login_etors_passenger()
        response = self.client.post(
            reverse("etors:book", args=[self.train.pk, (date.today() + timedelta(days=1)).isoformat()]),
            {
                "travel_class": "SL",
                "contact_name": "Dummy Family",
                "contact_email": "family@example.com",
                "contact_phone": "9876543210",
                "passenger_name": "Adult One",
                "passenger_age": 30,
                "passenger_gender": "M",
                "berth_preference": "Lower",
                "passenger_2_name": "Child Five",
                "passenger_2_age": 5,
                "passenger_2_gender": "F",
                "passenger_2_berth_preference": "Upper",
            },
        )
        self.assertRedirects(response, reverse("etors:payment"))
        response = self.client.post(reverse("etors:payment"), {"payment_method": "UPI"})
        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.get(contact_email="family@example.com")
        self.assertEqual(booking.contact_name, "Adult One")
        self.assertEqual(booking.passengers.count(), 2)
        self.assertEqual(booking.total_fare, Decimal("250.45"))
        self.assertEqual(booking.passengers.get(name="Child Five").seat_number, "NO BERTH")
        self.assertNotEqual(booking.passengers.get(name="Adult One").seat_number, "NO BERTH")

    def test_bookmycab_is_linked_scheduled_and_cancelled_with_train(self):
        self.login_etors_passenger()
        response = self.client.post(
            reverse(
                "etors:book",
                args=[self.train.pk, self.journey_date.isoformat()],
            ),
            {
                "travel_class": "3A",
                "contact_name": "Meera Rao",
                "contact_email": "meera@example.com",
                "contact_phone": "9876543210",
                "passenger_name": "Meera Rao",
                "passenger_age": 31,
                "passenger_gender": "F",
                "berth_preference": "Lower",
                "book_cab": "on",
                "call_recording_consent": "on",
                "cab_type": "SEDAN",
                "cab_drop_address": "MG Road, Destination City",
                "cab_drop_latitude": "16.506200",
                "cab_drop_longitude": "80.648000",
            },
        )
        self.assertRedirects(response, reverse("etors:payment"))

        payment = self.client.get(reverse("etors:payment"))
        self.assertContains(payment, "BOOKMYCAB")
        self.assertContains(payment, "Sedan")
        self.assertContains(payment, "500.00")
        self.assertContains(payment, "700.45")
        self.assertContains(payment, "Cab amount is not charged now")

        confirmation = self.client.post(
            reverse("etors:payment"),
            {"payment_method": "CARD"},
        )
        booking = Booking.objects.get(contact_email="meera@example.com")
        cab = CabBooking.objects.get(booking=booking)
        self.assertContains(confirmation, "BOOKMYCAB CONFIRMED")
        self.assertEqual(booking.total_fare, Decimal("700.45"))
        self.assertEqual(cab.fare, Decimal("500.00"))
        self.assertEqual(cab.cab_insurance_premium, Decimal("10.00"))
        self.assertTrue(cab.cab_insurance_policy.startswith("CABINS-"))
        self.assertEqual(cab.payment_status, "PENDING")
        self.assertEqual(cab.pickup_station, self.train.destination)
        self.assertEqual(cab.drop_address, "MG Road, Destination City")
        self.assertEqual(cab.drop_latitude, Decimal("16.506200"))
        self.assertEqual(cab.drop_longitude, Decimal("80.648000"))
        self.assertContains(confirmation, "View destination in Google Maps")
        self.assertEqual(
            cab.train_arrival_at - cab.cab_arrival_at,
            timedelta(minutes=20),
        )
        self.assertTrue(cab.driver_name)
        self.assertTrue(cab.vehicle_number)

        details = self.client.get(reverse("etors:pnr_detail", args=[booking.pnr]))
        self.assertContains(details, cab.reference)
        self.assertContains(details, "Cab reaches station")

        self.client.post(reverse("etors:cancel_booking", args=[booking.pnr]))
        cab.refresh_from_db()
        self.assertEqual(cab.status, "CANCELLED")

    def test_bookmycab_requires_vehicle_and_drop_address(self):
        self.login_etors_passenger()
        booking_page = self.client.get(reverse("etors:book", args=[self.train.pk, self.journey_date.isoformat()]))
        self.assertContains(booking_page, "Google Maps destination")
        self.assertContains(booking_page, "https://www.google.com/maps/search/?api=1")
        response = self.client.post(
            reverse(
                "etors:book",
                args=[self.train.pk, self.journey_date.isoformat()],
            ),
            {
                "travel_class": "SL",
                "contact_name": "Ravi",
                "contact_email": "ravi@example.com",
                "contact_phone": "9876543210",
                "passenger_name": "Ravi",
                "passenger_age": 30,
                "passenger_gender": "M",
                "berth_preference": "",
                "book_cab": "on",
                "call_recording_consent": "on",
                "cab_type": "",
                "cab_drop_address": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a BOOKMYCAB vehicle type")
        self.assertContains(response, "Enter the destination drop address")

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
        session = self.client.session
        session["etors_authorized_pnrs"] = [booking.pnr]
        session.save()
        self.assertEqual(train_availability(self.train, self.journey_date), 1)
        response = self.client.post(reverse("etors:cancel_booking", args=[booking.pnr]))
        booking.refresh_from_db()
        self.assertRedirects(response, reverse("etors:pnr_detail", args=[booking.pnr]))
        self.assertEqual(booking.status, "CANCELLED")
        self.assertEqual(train_availability(self.train, self.journey_date), 2)

    def test_invalid_pnr_returns_404(self):
        response = self.client.get(reverse("etors:pnr_detail", args=["0000000000"]))
        self.assertEqual(response.status_code, 404)

    def test_pnr_requires_matching_registered_mobile(self):
        booking = Booking.objects.create(
            train=self.train,
            journey_date=self.journey_date,
            travel_class="SL",
            contact_name="Private Passenger",
            contact_email="private@example.com",
            contact_phone="9876543210",
            total_fare=Decimal("250"),
        )
        direct = self.client.get(reverse("etors:pnr_detail", args=[booking.pnr]))
        self.assertRedirects(direct, reverse("etors:home"))
        wrong = self.client.get(
            reverse("etors:pnr_search"),
            {"pnr": booking.pnr, "contact_phone": "9876543211"},
        )
        self.assertRedirects(wrong, reverse("etors:home"))
        verified = self.client.get(
            reverse("etors:pnr_search"),
            {"pnr": booking.pnr, "contact_phone": "9876543210"},
        )
        self.assertRedirects(verified, reverse("etors:pnr_detail", args=[booking.pnr]))
        self.assertContains(self.client.get(reverse("etors:pnr_detail", args=[booking.pnr])), "Private Passenger")

    def test_driver_dispatch_hides_passenger_data_until_pickup_otp(self):
        booking = Booking.objects.create(
            train=self.train,
            journey_date=self.journey_date,
            travel_class="SL",
            contact_name="Hidden Passenger",
            contact_email="hidden@example.com",
            contact_phone="9876543210",
            total_fare=Decimal("250"),
        )
        cab = CabBooking.objects.create(
            booking=booking,
            cab_type="MINI",
            pickup_station=self.train.destination,
            drop_address="Secret Home Address",
            train_arrival_at=timezone.now() + timedelta(hours=2),
            cab_arrival_at=timezone.now() + timedelta(hours=1, minutes=40),
            fare=Decimal("350"),
            driver_name="Dummy Driver",
            driver_phone="9876501001",
            vehicle_number="TS 09 ET 2401",
            pickup_otp_hash=make_password("123456"),
            pickup_otp_expires_at=timezone.now() + timedelta(hours=3),
            payment_deadline=timezone.now() + timedelta(hours=3),
        )
        url = reverse("etors:cab_dispatch", args=[cab.dispatch_token])
        dispatch = self.client.get(url)
        self.assertContains(dispatch, self.train.number)
        self.assertContains(dispatch, "1800 100 200")
        self.assertNotContains(dispatch, booking.pnr)
        self.assertNotContains(dispatch, "Hidden Passenger")
        self.assertNotContains(dispatch, "9876543210")
        self.assertNotContains(dispatch, "Secret Home Address")
        call_start = self.client.post(reverse("etors:cab_call_start", args=[cab.dispatch_token]))
        self.assertEqual(call_start.status_code, 302)
        call = CabCallLog.objects.get(cab_booking=cab)
        self.assertTrue(call.recording_reference.startswith("REC-"))
        call_page = self.client.get(call_start.url)
        self.assertContains(call_page, "1800 100 200")
        self.assertContains(call_page, call.recording_reference)
        self.assertNotContains(call_page, "9876543210")
        self.client.post(call_start.url)
        call.refresh_from_db()
        self.assertEqual(call.status, "COMPLETED")
        self.assertIsNotNone(call.ended_at)
        rejected = self.client.post(url, {"pickup_otp": "000000"})
        self.assertNotContains(rejected, "Secret Home Address")
        verified = self.client.post(url, {"pickup_otp": "123456"})
        self.assertContains(verified, "Secret Home Address")
        cab.refresh_from_db()
        self.assertIsNotNone(cab.pickup_verified_at)

        session = self.client.session
        session["etors_authorized_pnrs"] = [booking.pnr]
        session.save()
        payment_url = reverse("etors:cab_payment", args=[cab.reference])
        cab_payment = self.client.post(payment_url, {"payment_method": "UPI"})
        self.assertRedirects(cab_payment, reverse("etors:pnr_detail", args=[booking.pnr]))
        cab.refresh_from_db()
        self.assertEqual(cab.payment_status, "PAID_UPI")
        self.assertEqual(cab.payment_method, "UPI")
        self.assertEqual(cab.driver_salary_deduction, Decimal("0"))

    def test_missed_cab_deadline_deducts_dummy_driver_salary(self):
        booking = Booking.objects.create(
            train=self.train, journey_date=self.journey_date, travel_class="SL",
            contact_name="Late Passenger", contact_email="late@example.com",
            contact_phone="9876543210", total_fare=Decimal("250.45"),
        )
        cab = CabBooking.objects.create(
            booking=booking, cab_type="AUTO", pickup_station=self.train.destination,
            drop_address="Hidden Address", train_arrival_at=timezone.now() - timedelta(hours=1),
            cab_arrival_at=timezone.now() - timedelta(hours=1, minutes=20), fare=Decimal("250"),
            cab_insurance_premium=Decimal("10"), driver_name="Late Driver",
            driver_phone="9876501002", vehicle_number="AP 16 AU 5182",
            pickup_otp_hash=make_password("654321"),
            pickup_otp_expires_at=timezone.now() - timedelta(minutes=1),
            payment_deadline=timezone.now() - timedelta(minutes=1),
        )
        response = self.client.get(reverse("etors:cab_dispatch", args=[cab.dispatch_token]))
        self.assertContains(response, "dummy deduction from the cab driver's salary")
        cab.refresh_from_db()
        self.assertEqual(cab.payment_status, "DRIVER_DEDUCTION")
        self.assertEqual(cab.driver_salary_deduction, Decimal("260.00"))

    def test_chatbot_explains_company_call_relay_and_recording(self):
        answer = self.client.post(
            reverse("etors:chatbot"),
            {"question": "How does the driver call the passenger and is the conversation recording tracked?"},
        ).json()["answer"]
        self.assertIn("1800 100 200", answer)
        self.assertIn("simulated recording references", answer)
