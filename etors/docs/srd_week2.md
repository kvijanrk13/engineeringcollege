# ETORS Week 2 - Software Requirements Document (SRD)

## 1. Introduction

### 1.1 Purpose

This Software Requirements Document specifies the behavior and constraints of the **E-Ticketing Online Reservation System (ETORS)**. ETORS is an academic Django application that demonstrates searching for trains, reserving seats, generating a PNR, simulating payment and arranging a destination cab.

### 1.2 Scope

ETORS provides a responsive web interface for passengers to:

- Search active trains by source, destination and journey date.
- Compare schedules, travel classes, fares and current seat availability.
- Sign in using a verified Gmail account before booking.
- Enter details for one or more passengers and choose berth preferences.
- complete a dummy payment and receive a confirmed seat and 10-digit PNR.
- Verify a booking using both PNR and registered mobile number.
- Cancel an eligible reservation.
- Add BOOKMYCAB, choose a suitable vehicle and pay its simulated fare.

The system is a classroom demonstration. It does not connect to IRCTC, Indian Railways, a real payment gateway or a real cab fleet.

### 1.3 Definitions and Abbreviations

| Term | Meaning |
|---|---|
| ETORS | E-Ticketing Online Reservation System |
| PNR | Passenger Name Record |
| SRD | Software Requirements Document |
| SDD | Software Design Document |
| OTP | One-Time Password |
| OAuth | Open Authorization |
| CRUD | Create, Read, Update and Delete |

## 2. Product Description

### 2.1 Product Perspective

Traditional counter-based reservation requires passengers to visit a station, wait in a queue and depend on staff for schedules and availability. ETORS models a centralized online alternative. A browser communicates with Django views and services, while PostgreSQL stores stations, trains, bookings, passengers, cab bookings and call logs. Render hosts the application over HTTPS.

### 2.2 User Classes

| User | Capabilities |
|---|---|
| Visitor | Search trains, view availability, read documentation, ask the ETORS assistant and start PNR verification. |
| Authenticated passenger | Perform visitor actions and create a booking after verified Gmail login. |
| Booking holder | View or cancel a booking after PNR/mobile verification; access associated cab details. |
| Administrator | Maintain demonstration data through Django administration and monitor stored records. |

### 2.3 Assumptions and Dependencies

- Users have a modern browser and internet connection.
- Google OAuth is available for passenger identity verification.
- PostgreSQL and the Render web service are operational.
- Train data and fares are demonstration data maintained by the project.
- Payment, insurance, driver allocation and telephone recording are simulations only.

## 3. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall list source and destination stations and reject an identical source and destination. |
| FR-02 | The system shall accept journey dates from today through the configured 120-day booking window. |
| FR-03 | The system shall display matching active trains with schedule, duration and available seats. |
| FR-04 | The system shall calculate availability from train capacity minus confirmed passengers for that journey date. |
| FR-05 | The system shall require verified Gmail authentication before a passenger can book. |
| FR-06 | The system shall validate contact details and details for every supplied passenger. |
| FR-07 | The system shall support General, Sleeper, 1A, 2A, 3A and 3E travel classes and calculate the corresponding fare. |
| FR-08 | The system shall show a dummy payment summary before confirmation. |
| FR-09 | On successful payment, the system shall create a unique 10-digit PNR and allocate seats transactionally. |
| FR-10 | The system shall require the registered mobile number with the PNR before revealing booking information. |
| FR-11 | The system shall allow an authorized user to cancel a confirmed booking and restore availability. |
| FR-12 | The system shall optionally create a BOOKMYCAB reservation for the destination station. |
| FR-13 | The system shall validate cab capacity, destination address, map coordinates and call-recording consent. |
| FR-14 | The system shall calculate cab arrival relative to train arrival and issue a protected pickup OTP. |
| FR-15 | The ETORS assistant shall answer supported questions and reject empty or oversized requests. |

## 4. Non-Functional Requirements

### 4.1 Security

- Booking creation shall require an authenticated Gmail session.
- PNR details shall require matching registered mobile verification.
- State-changing form submissions shall use CSRF protection and POST where appropriate.
- Pickup OTP values shall be stored as hashes rather than plain text.
- Production traffic shall use HTTPS.

### 4.2 Usability and Accessibility

- Pages shall be responsive on desktop and mobile screens.
- Forms shall provide labels, validation messages and clear success/error feedback.
- Booking and payment steps shall use consistent navigation and terminology.

### 4.3 Reliability and Performance

- Seat allocation and booking confirmation shall use database transactions to avoid partial records.
- Availability shall never be displayed below zero.
- Normal search and PNR requests should complete within three seconds under demonstration load.
- Database relationships shall protect referenced station and train data from accidental deletion.

### 4.4 Maintainability and Portability

- The application shall separate models, forms, views, services, URLs and templates.
- The system shall run in standard modern browsers without client installation.
- Database schema changes shall be managed through Django migrations.

## 5. Interface Requirements

### 5.1 User Interfaces

- ETORS home and train search
- Passenger and BOOKMYCAB booking form
- Dummy payment page
- Payment confirmation and PNR page
- Protected PNR details and cancellation
- Cab payment and driver dispatch pages
- Documentation and embedded help assistant

### 5.2 Software Interfaces

| Interface | Purpose |
|---|---|
| Django | URL routing, validation, sessions, ORM and HTML rendering |
| PostgreSQL | Persistent relational storage |
| Google OAuth | Verified passenger login |
| Render | Cloud deployment and HTTPS endpoint |

## 6. Acceptance Criteria

The release is acceptable when train search returns correct matches, overselling is prevented, unauthenticated booking redirects to Gmail login, successful dummy payment produces a protected PNR, cancellation changes booking status, optional cab booking respects passenger capacity, and the documentation page renders Weeks 1–3.
