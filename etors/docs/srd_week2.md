# Week 2 - Software Requirements Document (SRD)

## IV. E-TICKETING - ONLINE RESERVATION SYSTEM SRD

## 1. Introduction

### 1.1 Purpose

The purpose of this document is to record the software requirements of ETORS (E-Ticketing Online Reservation System), a web application that demonstrates the railway ticket reservation process. It describes what the system must do, the users who interact with it, the constraints placed on its operation, and the quality requirements used during development and testing.

ETORS automates train enquiry, berth-availability calculation, passenger booking, fare calculation, dummy payment, PNR generation, reservation retrieval, cancellation, journey insurance, and optional destination transport through BOOKMYCAB. This SRD reflects the behavior of the implemented ETORS application rather than a generic bus or railway ticketing system.

### 1.2 Scope

ETORS is a responsive web application within the Engineering College project. It is intended for academic demonstration and is hosted at `https://engineeringcollege.onrender.com/etors/`.

The application enables a passenger to:

- Search active trains using different source and destination stations and a journey date within the 120-day booking window.
- View train number, name, operating-days description, departure and arrival times, duration, and calculated berth availability.
- Log in with a verified Gmail account before making a reservation.
- Select General, Sleeper, AC 3 Economy, AC 3 Tier, AC 2 Tier, or AC First Class.
- Add between one and five passengers and record age, gender, and optional berth preference.
- Include an optional BOOKMYCAB transfer from the destination station to a specified drop address.
- Complete a dummy train payment using UPI, card, or net banking.
- Receive a unique 10-digit PNR, passenger seat details, and a demonstration train-insurance policy.
- Retrieve a booking using the PNR and registered mobile number and cancel a confirmed reservation.
- Use the ETORS Assistant for supported questions about the service.

When BOOKMYCAB is selected, the system also demonstrates vehicle-capacity validation, map-assisted destination entry, driver and vehicle assignment, cab arrival scheduling, pickup OTP verification, company-relayed call logging, cab insurance, and a separate dummy UPI payment after pickup.

Administrators use Django administration facilities to maintain stations, trains, fares, capacity, bookings, passengers, cab bookings, and call records.

### 1.3 Acronyms

| Acronym | Meaning |
|---|---|
| ETORS | E-Ticketing Online Reservation System |
| ORS | Online Reservation System |
| SRD | Software Requirements Document |
| GUI | Graphical User Interface |
| DBMS | Database Management System |
| PNR | Passenger Name Record |
| OTP | One-Time Password |
| UPI | Unified Payments Interface |
| OAuth | Open Authorization |
| ORM | Object-Relational Mapping |
| CSRF | Cross-Site Request Forgery |
| HTTPS | Hypertext Transfer Protocol Secure |

### 1.4 References

- IEEE 830-1998 guidance for Software Requirements Specifications.
- Django framework documentation.
- PostgreSQL documentation.
- Google OAuth documentation for Gmail authentication.
- Google Maps URLs and Places/Maps integration documentation.
- Render cloud deployment documentation.
- ETORS models, forms, views, services, templates, and automated tests in the Engineering College project.

### 1.5 Overview

The remaining sections describe the product perspective, product functions, user characteristics, constraints, assumptions, dependencies, functional requirements, non-functional requirements, interface specifications, hardware/software requirements, and indexed terms.

ETORS uses a browser-based client/server design. Django receives browser requests, validates input, applies reservation rules, and stores relational records for stations, trains, bookings, passengers, cabs, and call logs. The deployed application uses sample railway and transport data and does not connect to live Indian Railways, IRCTC, banking, insurance, telephone, or vehicle-dispatch systems.

## 2. Project Description

### 2.1 Product Perspective

Before computerization, passengers depend on counters or enquiry staff for schedules, fares, availability, booking, and cancellation. This causes queues and paperwork, while repeated manual entry and calculation can produce inconsistent passenger, fare, seat, and cancellation records. Onward transport from the destination station must also be arranged independently.

ETORS centralizes the demonstrated workflow. The passenger searches for a route and date, selects an available train, authenticates through Gmail, supplies passenger details, chooses a class, optionally adds BOOKMYCAB, and completes a dummy train payment. ETORS then creates the booking and passenger records in a database transaction, issues a 10-digit PNR, assigns a sequential seat to each passenger who requires a berth, and displays the confirmation.

The computerized system provides the following benefits:

- Train, schedule, availability, fare, passenger, booking, and cancellation information can be stored and retrieved centrally.
- Server-side calculation reduces repetitive fare and availability work.
- Confirmed bookings reduce availability, while cancelled bookings release their occupied berths.
- PNR and registered-mobile verification prevents a PNR alone from revealing passenger information.
- BOOKMYCAB connects destination-station pickup with the train journey while retaining a separate post-pickup cab payment.
- Responsive screens support desktop and mobile browsers.

### 2.2 Product Functions

The product supports three user groups.

**Passenger functions**

- Search trains by source, destination, and date.
- View schedule information and current calculated availability.
- Authenticate using the parent application's verified Gmail flow.
- Compare six travel classes and their calculated fares.
- Book one to five passengers and provide berth preferences.
- Complete dummy train payment by UPI, card, or net banking.
- Receive a PNR, automatic seat allocation, and included demonstration train insurance.
- Verify PNR status using the registered mobile number.
- View reservation, passenger, fare, insurance, and cab information.
- Cancel a confirmed reservation.
- Ask supported questions through the ETORS Assistant.

**BOOKMYCAB passenger and driver functions**

- Select Bike, Auto, Mini, Sedan, SUV, Tempo Traveller, or Bus according to passenger capacity.
- Record a destination address and optional map coordinates.
- Require consent for company-relayed recorded calls.
- Generate a cab reference, private dispatch token, six-digit pickup OTP, driver, vehicle, insurance policy, and schedule.
- Schedule the demonstration vehicle to reach the destination station 20 minutes before train arrival.
- Allow the driver to verify the pickup OTP through the private dispatch page.
- Allow the passenger to pay the cab fare plus cab-insurance premium separately through dummy UPI after pickup verification.
- Log demonstration call sessions and reconcile an expired unpaid cab amount as a driver-salary deduction.

**Administrator functions**

- Create and maintain station and train master data.
- Maintain train status, times, duration, running-days description, capacity, sleeper fare, and AC fare.
- Inspect and administer bookings, passengers, cab records, payment states, and call logs.

### 2.3 User Characteristics

**Passenger:** A passenger should be able to read the English interface and use a general-purpose web browser. Gmail access is required to book, and the registered Indian mobile number is required for PNR verification. No reservation-system training is expected.

**Administrator:** An administrator should understand ETORS master data and reservation rules and be authorized to use Django administration facilities.

**Cab driver (demonstration role):** A driver follows a private dispatch link, views the assigned trip, verifies the pickup OTP, and may start or end a simulated company-relayed call. Basic smartphone browser skills are sufficient.

### 2.4 General Constraints

- The application requires internet access and a modern browser.
- Source and destination must be different.
- Journey dates must be from the current date through the next 120 days.
- Only active trains whose stored source and destination match the search are returned.
- The `running_days` value is descriptive in the current implementation; it is displayed but is not used to reject a selected date.
- Booking requires an authenticated user whose session is marked as a verified ETORS Gmail login.
- A booking contains a maximum of five passengers.
- Passengers aged above five require a berth; passengers aged one to five are recorded as `NO BERTH` and are not charged the train fare or per-berth insurance premium.
- Availability is checked when the booking form is opened, when it is submitted, and again before confirmation.
- Contact mobile numbers must be valid 10-digit Indian mobile numbers beginning with 6–9.
- PNR values contain exactly 10 digits.
- PNR verification is limited after five unsuccessful attempts in the same session.
- A selected BOOKMYCAB vehicle must hold the entire passenger group.
- Cab booking requires a drop address and call-recording consent.
- Train and cab payments, policies, calls, dispatches, and deductions are simulations only.

### 2.5 Assumptions and Dependencies

**Assumptions**

- Administrators enter accurate station, train, schedule, fare, and capacity data.
- Passengers supply correct names, ages, email addresses, mobile numbers, and destination details.
- Each active train record represents a direct source-to-destination service.
- Submission of a permitted dummy payment method represents payment success for the demonstration.
- The hosting platform and external authentication service are available when required.

**Dependencies**

- Python and Django.
- Django ORM and a relational database; PostgreSQL is used by the deployed environment.
- Google authentication supplied by the parent Engineering College application.
- Django sessions, CSRF protection, password hashing, and transaction management.
- HTML5, CSS3, and JavaScript in a standards-compliant browser.
- Render hosting and HTTPS termination.
- Google Maps links; embedded Places/Maps behavior additionally depends on a configured API key.

## 3. Specific Requirements

### 3.1 Functional Requirements

#### 3.1.1 Train Search

1. The system shall display all stored stations in the source and destination controls.
2. The system shall reject identical source and destination selections.
3. The system shall reject past dates and dates more than 120 days ahead.
4. The system shall return active trains matching the selected source and destination.
5. The system shall display the train number, name, running-days description, departure time, arrival time, duration, and available berth count.
6. The system shall calculate availability as train capacity minus passengers attached to confirmed bookings for that train and journey date.

#### 3.1.2 Authentication and Booking

7. The system shall allow public train search but shall require verified Gmail authentication before booking.
8. The system shall allow General, Sleeper, AC 3 Economy, AC 3 Tier, AC 2 Tier, and AC First Class selection.
9. The system shall derive each class fare from the train's stored sleeper or AC base fare and the configured class multiplier.
10. The system shall capture the first passenger as the booking contact name together with contact email and mobile number.
11. The system shall accept one required passenger and up to four additional passengers.
12. The system shall validate every supplied passenger's name, age from 1 to 120, and gender, with berth preference optional.
13. The system shall count only passengers above five years old when checking berth availability and calculating train fare.
14. The system shall include a demonstration train-insurance premium of Rs. 0.45 for every passenger who requires a berth.
15. The system shall recheck capacity inside the confirmation transaction to reduce overbooking risk.

#### 3.1.3 Train Payment and Confirmation

16. The system shall offer dummy UPI, card, and net-banking methods for train payment.
17. The system shall clearly state that the payment is a demonstration and no real money is transferred.
18. The train amount payable shall contain the class-based train fare plus the included train-insurance premium; it shall not charge the cab amount at this stage.
19. After valid payment submission, the system shall create the booking and passenger records atomically.
20. The system shall generate a unique numeric 10-digit PNR.
21. The system shall allocate sequential seat identifiers to passengers above five and `NO BERTH` to passengers aged one to five.
22. The system shall generate a demonstration train-insurance policy reference.
23. The system shall show booking, PNR, passenger, seat, insurance, and optional cab confirmation details.

#### 3.1.4 PNR Enquiry and Cancellation

24. The system shall require a valid PNR and matching registered mobile number before authorizing public access to a reservation.
25. The system shall also allow staff, the authenticated booking owner, or a session previously authorized for that PNR to view it.
26. The system shall limit unsuccessful PNR/mobile verification attempts to five per browser session.
27. The system shall display booking status, train, route, date, class, passengers, contact details, fare, insurance, and linked cab information.
28. The system shall permit an authorized user to cancel a confirmed booking using a CSRF-protected POST request.
29. Cancellation shall record the cancellation time, stop the booking from consuming availability, cancel a linked cab, and cancel a still-pending cab payment.

#### 3.1.5 BOOKMYCAB

30. The system shall allow BOOKMYCAB to be added during train booking.
31. The system shall validate the selected vehicle capacity against the total number of passengers, including passengers who do not require train berths.
32. The system shall require a vehicle type, drop address, and consent for company-relayed recorded calls.
33. The system shall accept optional map latitude and longitude only within valid geographic ranges.
34. The system shall assign the train's destination station as the cab pickup station.
35. The system shall schedule cab arrival 20 minutes before the calculated train arrival, including an overnight arrival when appropriate.
36. The system shall generate a unique cab reference, unguessable dispatch token, demonstration driver, vehicle number, cab-insurance policy, and hashed pickup OTP.
37. The private dispatch page shall permit no more than five unsuccessful OTP attempts and shall reject expired OTPs.
38. The system shall require successful pickup verification before accepting dummy cab payment.
39. Cab payment shall be accepted only by dummy UPI and shall equal the cab fare plus the Rs. 10 cab-insurance premium.
40. When the payment deadline expires while payment is pending, the system shall record the amount as a demonstration driver-salary deduction.
41. The system shall create call and recording references when a company-relayed call starts and shall record its completion time when ended.

#### 3.1.6 Assistance and Administration

42. The ETORS Assistant shall accept a non-empty question of no more than 500 characters and return a contextual response for supported ETORS topics.
43. The system shall provide separate demonstration support numbers for train booking and BOOKMYCAB.
44. Authorized administrators shall be able to maintain stations, trains, fares, capacity, bookings, passengers, cab bookings, and call logs.

### 3.2 Non-Functional Requirements

Non-functional requirements describe how ETORS should operate rather than which reservation functions it performs.

#### 3.2.1 Product Requirements

**Usability**

- A passenger with ordinary browser experience should be able to search trains and complete the demonstration without formal training.
- Forms shall use visible labels, clear validation errors, explanatory notices, confirmation messages, and consistent navigation.
- The interface shall adapt to desktop and mobile viewport sizes.

**Performance**

- Normal train-search, PNR, and documentation requests should complete within five seconds under the expected academic demonstration load and a stable network connection.
- Fare and availability calculations shall finish before confirmation is stored.
- Views that display related train, station, passenger, or cab data should use efficient related-object queries.

**Reliability**

- Booking and passenger creation shall be transactional so that a failure does not leave a partial reservation.
- Unique database constraints shall protect PNR, cab reference, dispatch token, call reference, and recording reference values.
- Confirmed passengers shall reduce availability and cancelled passengers shall not.

**Portability**

- ETORS shall require no client installation and should work in current standards-compliant browsers on Windows, Linux, macOS, Android, and iOS.

**Scalability**

- The relational design shall permit growth in stations, trains, journey dates, bookings, passengers, and cab records.
- Capacity checks and booking creation shall remain server-controlled when concurrent users submit reservations.

**Availability**

- The deployed application should remain available continuously except during Render outages, cold starts, maintenance, or external-service interruptions.

**Maintainability**

- Models, forms, views, service rules, templates, documentation, and tests shall remain separated by responsibility.
- Fare multipliers, insurance premiums, cab fares, vehicle capacity, schedules, and payment reconciliation rules should be centralized where practical.

**Accessibility**

- Controls shall be keyboard operable and associated with readable labels.
- Text, status, and validation feedback shall not depend only on color.
- Responsive layouts shall remain understandable at narrow widths.

#### 3.2.2 Organizational Requirements

**Delivery:** Changes shall be delivered incrementally through Git commits and deployed from the configured repository branch.

**Implementation:** The backend shall use Python and Django; data access shall use Django ORM; pages shall use HTML5, CSS3, and JavaScript; deployment shall use a Render-compatible configuration.

**Standards:** Dates shown to users shall be unambiguous, time values shall use a 24-hour display where provided, stored date-times shall follow Django timezone handling, and state-changing forms shall use POST with CSRF protection.

**Testing:** Reservation rules and documentation expectations shall be covered by Django automated tests. Django system checks and migration consistency checks shall be run before deployment.

#### 3.2.3 External Requirements

**Security**

- Deployed browser traffic shall use HTTPS.
- Booking shall require verified Gmail authentication.
- State-changing requests shall use Django CSRF protection.
- PNR information shall require ownership, staff authority, or prior PNR/mobile verification.
- Cab OTPs shall be stored as password hashes, and dispatch URLs shall use UUID tokens.
- Server-side validation shall be applied even when client-side validation is present.

**Privacy**

- Passenger and travel data shall not be exposed from a PNR alone.
- Consent shall be collected before enabling the recorded-call demonstration.
- The company-relay workflow shall avoid showing the passenger's mobile number to the cab driver.

**Interoperability**

- ETORS shall integrate with the parent application's Google authentication and user sessions.
- It shall operate with the configured Django relational database and Render environment.
- Google Maps links shall use standard HTTPS URLs; optional embedded map features shall depend on the configured Google Maps API.
- A future production system would require approved railway inventory, payment, messaging, insurance, telephony, and dispatch APIs; these are outside the current scope.

### 3.3 Interface Specification

#### 3.3.1 User Interface

- ETORS navigation, train-search form, search results, BOOKMYCAB introduction, and PNR-verification form.
- Verified Gmail login redirect supplied by the parent application.
- Booking form with travel class, contact, passenger, insurance, cab, map, and consent sections.
- Dummy train-payment and confirmation screens.
- PNR detail and cancellation screen.
- Cab dispatch, pickup-OTP, cab-payment, and call-session screens.
- ETORS documentation and chatbot interfaces.
- Django administration interface.

#### 3.3.2 Hardware Interface

- Desktop or laptop computer, tablet, or smartphone.
- Keyboard, mouse, touch screen, or other browser-compatible input device.
- Internet-capable network interface.

No railway terminal, card reader, GPS unit, telephone switch, or vehicle hardware is controlled by this academic system.

#### 3.3.3 Software Interface

- Django application framework, ORM, authentication, sessions, forms, and administration.
- PostgreSQL in deployment and a compatible configured database in development/testing.
- Parent-application Google authentication.
- Render web-service environment.
- Optional Google Maps/Places browser integration.

#### 3.3.4 Communication Interface

- HTTPS between the browser and deployed server.
- Secure configured connection between Django and PostgreSQL.
- Session cookies for authentication and PNR authorization.
- CSRF tokens for protected POST requests.
- HTTP GET for read/search operations and POST for booking, payment, OTP, call, logout, and cancellation state changes.

## 4. Appendices

### 4.1 Hardware Requirements

- Development computer with a dual-core processor or better.
- At least 4 GB RAM and sufficient storage for the project and dependencies.
- Reliable internet access for authentication, hosted database, deployment, and live verification.

### 4.2 Software Requirements

- Python 3.10 or a project-compatible later version.
- Django and dependencies declared by the project.
- PostgreSQL or another configured Django-compatible relational database.
- Git version control.
- A modern browser and a code editor or IDE.

### 4.3 Academic Demonstration Notice

ETORS is an educational prototype. Its trains, seats, fares, payments, insurance policies, cab assignments, OTPs, calls, and salary deductions are demonstration data and processes. No real ticket, payment, insurance policy, recorded telephone call, or vehicle dispatch is created. ETORS is not affiliated with IRCTC or Indian Railways.

## 5. Index

- **A:** Accessibility, Administrator, Authentication, Availability
- **B:** Berth, Booking, BOOKMYCAB
- **C:** Cab, Cancellation, Capacity, CSRF
- **D:** Database, Django, Dispatch
- **F:** Fare, Functional Requirements
- **G:** Gmail Authentication, Google Maps, GUI
- **I:** Insurance, Interface, Interoperability
- **O:** OAuth, OTP
- **P:** Passenger, Payment, Performance, PNR, Privacy
- **R:** Reliability, Render, Reservation
- **S:** Scope, Search, Seat, Security, Station
- **T:** Train, Transaction, Travel Class
- **U:** UPI, Usability
