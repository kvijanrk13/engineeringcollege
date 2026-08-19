# Week 1 - Problem Statement

## II. E-TICKETING - ONLINE RESERVATION SYSTEM (ETORS)

### Problem Statement

Railway passengers need a simple way to find trains, check current berth availability, compare travel classes and fares, and reserve tickets without visiting a booking counter. A counter-based process is time-consuming and makes it difficult to obtain up-to-date information, particularly during busy travel periods. Passengers also need a secure way to retrieve or cancel a booking and, after reaching the destination station, arrange suitable onward transport.

ETORS addresses this problem through an academic web application that demonstrates the complete railway reservation workflow. It combines train search, passenger booking, dummy payment, PNR-based journey management, optional train-to-destination transport through BOOKMYCAB, and an ETORS help chatbot in one responsive interface.

### Existing System

In a traditional reservation process, a passenger visits a railway counter or enquiry office to ask about routes, schedules, fares, and available seats. Separate counters or manually maintained records can cause queues, repeated data entry, delayed availability updates, calculation errors, and difficulty retrieving an earlier reservation. A passenger cannot conveniently compare all travel options, reserve from home, or securely manage the journey using a mobile browser.

Onward travel is also normally arranged separately after the train ticket is booked. This gives the passenger no single workflow for scheduling a vehicle at the destination station, recording the pickup, and tracking its payment status.

### Proposed System

ETORS (E-Ticketing Online Reservation System) is a web-based railway reservation demonstration. Its working flow is as follows:

1. **Search trains:** The passenger selects different source and destination stations and a journey date from today through the next 120 days. ETORS lists active trains for the route with departure time, arrival time, duration, and live berth availability.
2. **Authenticate for booking:** Train search and PNR verification are public, but booking requires login with a verified Gmail account.
3. **Enter journey details:** The passenger chooses General, Sleeper, AC 3 Economy, AC 3 Tier, AC 2 Tier, or AC First Class and enters contact details for the reservation. Up to five passengers can be included in one booking, with gender and optional berth preference recorded for each passenger.
4. **Validate berth capacity:** Passengers above five years of age require a berth. ETORS checks the required number of berths against current availability before proceeding and checks it again when payment is submitted.
5. **Add BOOKMYCAB when required:** The passenger may select a Bike, Auto, Mini, Sedan, SUV, Tempo Traveller, or Bus for pickup at the destination station. The vehicle must have enough capacity for the passenger group. A drop address and consent for company-relayed recorded calls are required.
6. **Complete dummy train payment:** ETORS displays the class-based train fare and demonstration train-insurance premium. The passenger selects dummy UPI, card, or net banking; no real money is transferred.
7. **Confirm the reservation:** After successful validation, ETORS creates the booking, generates a unique 10-digit PNR, assigns sequential seat numbers to passengers who require berths, and shows the confirmed journey details.
8. **Manage the booking securely:** A passenger retrieves a reservation using both the 10-digit PNR and the registered mobile number. Verified users can view the passenger list, fare, insurance, and cab details, or cancel a confirmed reservation. Cancellation releases its occupied berths back into availability and also cancels any linked cab booking.
9. **Complete the BOOKMYCAB workflow:** ETORS assigns a demonstration driver and vehicle and schedules arrival at the destination station 20 minutes before the train. The driver verifies the passenger using a six-digit pickup OTP. After pickup, the passenger completes a separate dummy UPI cab payment consisting of the cab fare and cab-insurance premium. If the payment deadline expires, the demonstration records the amount as a driver-salary deduction.
10. **Obtain help:** The built-in ETORS Assistant answers common questions about searching, booking, PNR status, cancellation, BOOKMYCAB, and support services.

### The proposed system has the following advantages

1. Passengers can search routes and reserve railway tickets online without waiting at a booking counter.
2. Schedules, journey duration, class-based fares, and current berth availability are presented in one workflow.
3. A 120-day date limit, route validation, passenger validation, and repeated availability checks reduce invalid or over-capacity bookings.
4. Verified Gmail authentication protects ticket creation, while PNR plus registered-mobile verification protects passenger information.
5. One reservation can contain up to five passengers, with appropriate handling for children aged five or below who do not require a berth.
6. Dummy UPI, card, and net-banking methods safely demonstrate train payment without processing real money.
7. Every confirmed booking receives a unique 10-digit PNR, automatic seat assignment, and a demonstration train-insurance policy.
8. Cancellation updates the booking immediately and makes released berths available for later reservations.
9. BOOKMYCAB integrates destination-station pickup, vehicle-capacity validation, driver assignment, OTP verification, cab insurance, and separate dummy UPI payment.
10. The responsive website and ETORS Assistant make the demonstration accessible from desktop and mobile browsers.

> **Academic demonstration:** ETORS uses sample trains, drivers, insurance policies, and payment flows. It does not transfer real money and is not affiliated with IRCTC or Indian Railways.
