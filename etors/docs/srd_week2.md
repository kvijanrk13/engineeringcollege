# Week 2 - Software Requirements Document (SRD)

## IV. E-TICKETING – ONLINE RESERVATION SYSTEM

## 1. Introduction

### 1.1 Problem Statement

An E-Ticketing Online Reservation System (ETORS) manages railway ticket enquiries and reservations electronically. In a manual reservation process, passengers must visit a booking counter or contact an operator to learn about trains, schedules, fares, and seat availability. This consumes time, creates queues, increases paperwork, and makes reservation records harder to maintain accurately.

The system must provide a single web-based platform through which passengers can search for trains, check availability, enter passenger information, select a travel class, complete a demonstration payment, and obtain a unique Passenger Name Record (PNR). It must also allow passengers to retrieve and cancel a booking securely using the PNR and registered mobile number.

**Existing System:**

The existing process depends heavily on booking counters, telephone enquiries, registers, and manual calculations. Passengers may need to wait in a queue to check schedules or reserve a seat. Maintaining passenger, payment, cancellation, and seat-allocation records manually can produce duplicate entries, calculation errors, delayed updates, and difficulty retrieving historical information.

**Proposed System:**

The proposed ETORS is a cloud-hosted web application for railway reservation demonstrations. It provides route and date-based train search, live calculated seat availability, authenticated booking, passenger and berth details, fare calculation, dummy digital payment, automatic PNR and seat generation, secure PNR enquiry, cancellation, train insurance, and optional BOOKMYCAB destination transfer services.

The proposed system has the following advantages:

1. Passengers can search and reserve tickets without visiting a booking counter.
2. Train schedules, travel classes, fares, and available seats are displayed together.
3. Booking and passenger records are stored centrally and can be retrieved quickly.
4. PNR and seat numbers are generated automatically after successful payment.
5. PNR details are protected by verification with the registered mobile number.
6. Optional destination cab booking is available within the reservation flow.
7. Paperwork and repetitive manual calculations are reduced.

### 1.2 Purpose

The purpose of this document is to specify the software requirements for ETORS. The application automates the principal activities involved in a demonstration railway reservation workflow: train discovery, availability checking, passenger registration, fare calculation, payment simulation, ticket confirmation, PNR enquiry, cancellation, and optional cab transfer booking.

This document defines the functional and non-functional requirements, user roles, constraints, assumptions, dependencies, interfaces, and operating environment that guide the development, testing, deployment, and maintenance of ETORS.

### 1.3 Scope

ETORS is a responsive, cloud-based web application developed using Python and the Django framework.

**For Passengers:**

- Search active trains by departure station, arrival station, and journey date
- View train number, train name, schedule, duration, running days, fares, and availability
- Sign in through a verified Gmail account before booking
- Select General, Sleeper, or supported AC travel classes
- Enter contact and passenger details
- Specify gender and berth preference for each passenger
- Add train insurance to the reservation
- Select an optional BOOKMYCAB vehicle and destination address
- Complete payment through a dummy UPI, card, or net-banking flow
- Receive a unique 10-digit PNR and allocated seat numbers
- Retrieve a reservation using the PNR and registered mobile number
- View train, passenger, insurance, fare, and cab details
- Cancel a confirmed reservation
- Use the ETORS help chatbot for supported enquiries

**For Cab Passengers and Drivers:**

- Schedule a cab according to the train's destination and arrival time
- Select a vehicle according to passenger capacity
- Generate a private cab reference and dispatch link
- Verify passenger pickup using a time-limited OTP
- Complete dummy cab payment through UPI after pickup verification
- Record company-relayed driver/passenger call sessions with consent
- Apply the configured demonstration salary-deduction rule when payment expires

**For Administrators:**

- Manage stations and active train services
- Maintain schedules, running days, capacity, and class fares
- View and administer booking, passenger, cab, and call records
- Activate or deactivate train services
- Monitor reservation data through Django administration facilities

### 1.4 Definitions, Acronyms and Abbreviations

| Abbreviation | Meaning |
|---|---|
| ETORS | E-Ticketing Online Reservation System |
| ORS | Online Reservation System |
| PNR | Passenger Name Record |
| GUI | Graphical User Interface |
| DBMS | Database Management System |
| OTP | One-Time Password |
| UPI | Unified Payments Interface |
| OAuth | Open Authorization |
| HTTPS | Hypertext Transfer Protocol Secure |
| ORM | Object-Relational Mapping |
| RBAC | Role-Based Access Control |

### 1.5 References

- IEEE 830 Software Requirements Specification guidance
- Roger S. Pressman – *Software Engineering: A Practitioner's Approach*
- Ian Sommerville – *Software Engineering*
- Django official documentation
- PostgreSQL documentation
- Google OAuth documentation
- Render cloud documentation
- RBI guidance for regulated digital payment modes (production consideration)

### 1.6 Overview

ETORS follows a client-server architecture. Passengers interact with responsive web pages, while Django processes requests and stores stations, trains, bookings, passengers, cab bookings, and call records in a relational database. Authentication is integrated with the college application's Google sign-in flow. The deployed academic system uses demonstration train, payment, insurance, cab, driver, and communication data; it is not connected to a live railway inventory or banking network.

## 2. Project Description

### 2.1 Product Perspective

ETORS is a dedicated module within the Engineering College web application. It replaces a paper-based demonstration of reservation activities with a centralized workflow accessible through a standard browser.

The passenger begins by selecting source and destination stations and a valid journey date. ETORS lists matching active trains and calculates availability from capacity and confirmed passenger records. An authenticated passenger selects a train and class, enters passenger information, and optionally requests insurance and a destination cab. After the dummy payment succeeds, the application creates the booking and passenger records atomically, generates the PNR and seat assignments, and displays the confirmation.

The proposed system provides these benefits:

- Faster route, schedule, and fare enquiries
- Consistent capacity and availability calculations
- Centralized booking and passenger information
- Automatic fare, insurance, PNR, seat, and cab calculations
- Secure booking retrieval using two identifying values
- Immediate booking cancellation and linked cab cancellation
- Responsive access from desktop and mobile browsers
- Reduced paperwork and administrative effort

### 2.2 Product Functions

The major product functions are:

**Passenger Functions**

- Gmail authentication and logout
- Station and journey-date selection
- Train search and result display
- Seat-availability calculation
- Travel-class and fare selection
- Multi-passenger data entry
- Berth-preference capture
- Train-insurance selection
- Dummy payment processing
- PNR and seat-number generation
- PNR/mobile verification
- Booking-detail display
- Reservation cancellation
- ETORS chatbot assistance

**BOOKMYCAB Functions**

- Vehicle selection based on passenger capacity
- Destination-address and optional map-coordinate capture
- Fare and cab-insurance calculation
- Driver, vehicle, reference, and schedule generation
- Time-limited pickup OTP verification
- Dummy UPI payment after pickup
- Payment-deadline reconciliation
- Company-relayed call logging with recording consent

**Administrative Functions**

- Station management
- Train and schedule management
- Capacity and fare management
- Booking and passenger record management
- Cab-dispatch and call-record monitoring

### 2.3 User Characteristics

**Administrator**

The administrator maintains station and train master data and can inspect reservation records. The administrator should understand the reservation workflow, Django administration interface, and basic data-management procedures.

**Passenger**

The passenger searches for trains, completes reservations, checks PNR status, books optional cab transport, and cancels eligible bookings. A passenger requires basic English comprehension, web-browsing ability, a valid Gmail identity for booking, and access to the registered mobile number used for PNR verification.

**Cab Driver (Demonstration Role)**

The driver uses the private dispatch link to view assignment details, verify the passenger's pickup OTP, and initiate a company-relayed call. Only basic smartphone and web-browser skills are required.

### 2.4 General Constraints

- Internet connectivity and a supported web browser are required.
- Source and destination stations must be different.
- The journey date cannot be earlier than the current date.
- Only active trains matching the selected route may be booked.
- Booking requires an authenticated session marked as a verified ETORS Gmail login.
- Passenger count and seat allocation cannot exceed calculated availability.
- Contact and passenger values must pass server-side validation.
- The PNR must contain exactly 10 digits.
- Booking details require both the PNR and matching registered mobile number unless the authenticated owner is accessing them.
- Payment, insurance, cab, driver, and call facilities are academic simulations.
- Cab vehicle capacity must accommodate all passengers in the train booking.
- Pickup OTPs and cab payment deadlines expire after configured time limits.

### 2.5 Assumptions and Dependencies

**Assumptions**

- Train, station, schedule, capacity, and fare data entered by administrators is accurate.
- Users provide correct passenger and contact information.
- Google authentication and the application's session service are available.
- The application is deployed on Render or a compatible hosting service.
- Demonstration payments are treated as successful only after valid form submission.

**Dependencies**

- Python and Django framework
- Relational database supported by Django, with PostgreSQL used in deployment
- Google OAuth authentication supplied by the parent application
- Render cloud hosting
- HTML5, CSS3, and JavaScript-capable browser
- Secure session, CSRF, and password-hashing facilities provided by Django

## 3. Specific Requirements

### 3.1 Functional Requirements

The system shall:

1. Allow a user to select a source, destination, and current or future journey date.
2. Reject a search when source and destination are identical.
3. Display active trains that serve the selected route and operate on the selected date.
4. Display train number, name, departure, arrival, duration, running days, fares, and available seats.
5. Calculate availability from train capacity minus passengers on confirmed bookings for that date.
6. Require verified Gmail authentication before opening the booking workflow.
7. Allow selection from the travel classes configured by ETORS.
8. Capture contact name, email address, and mobile number.
9. Capture each passenger's name, age, gender, and berth preference.
10. Validate that at least one passenger is included and that enough seats remain.
11. Calculate class fare for every passenger and add selected insurance premiums.
12. Offer dummy UPI, card, and net-banking methods for the train-ticket payment demonstration.
13. Create the booking and all passenger records as one database transaction after payment.
14. Generate a unique 10-digit PNR for every successful booking.
15. Allocate a seat number to every passenger.
16. Generate a train-insurance policy reference when insurance is selected.
17. Allow PNR enquiry only after matching the PNR with its registered mobile number or authenticated owner.
18. Display booking status, journey, passenger, fare, insurance, and linked cab information.
19. Allow an authorized user to cancel a confirmed booking.
20. Record the cancellation time and cancel a linked pending cab booking.
21. Allow an optional destination cab to be selected during train booking.
22. Validate the cab type against the number of passengers.
23. Store the drop address and optional geographic coordinates.
24. Generate a unique cab reference, dispatch token, pickup OTP, driver, and vehicle assignment.
25. Schedule cab arrival relative to the train's destination arrival.
26. Require pickup OTP verification before dummy cab UPI payment.
27. Expire the OTP and reconcile unpaid cab charges after the configured deadline.
28. Create and complete company-relayed cab call logs only after recording consent is supplied.
29. Provide contextual answers for supported ETORS help questions through the chatbot.
30. Permit administrators to maintain station, train, fare, capacity, and reservation data.

### 3.2 Non-Functional Requirements

#### 3.2.1 Product Requirements

**Usability**

- The interface shall use clear labels, validation messages, confirmation messages, and consistent navigation.
- A first-time passenger with basic web skills should be able to search and complete a demonstration booking without formal training.
- Pages shall adapt to desktop and mobile screen sizes.

**Performance**

- Normal search and PNR requests should return within three seconds under expected academic demonstration load.
- Availability and fare calculations shall be completed before a booking is confirmed.
- Database queries should use related-object loading where required to avoid unnecessary repeated requests.

**Reliability**

- Booking and passenger creation shall be atomic so that partial reservations are not stored.
- PNR, cab reference, dispatch token, and call reference values shall be unique.
- A cancelled booking shall no longer reduce available-seat totals.

**Portability**

- ETORS shall run through current standards-compliant browsers on Windows, Linux, macOS, Android, and iOS without platform-specific installation.

**Scalability**

- The database design shall support growth in stations, trains, journey dates, passengers, and bookings.
- Frequently used search and relationship fields shall use database-backed queries suitable for concurrent users.

**Availability**

- The deployed application should be accessible continuously except during hosting outages or scheduled maintenance.

**Maintainability**

- The system shall use separate Django models, forms, views, services, templates, and tests.
- Fare, capacity, insurance, cab, and payment rules shall be centralized so they can be changed without rewriting unrelated interfaces.

**Accessibility**

- Forms shall provide labels, keyboard-operable controls, readable contrast, and understandable error feedback.
- Responsive layouts shall remain usable at mobile viewport widths.

#### 3.2.2 Organizational Requirements

- The backend shall be developed with Python and Django.
- Data shall be managed through Django's ORM and a relational database.
- The interface shall use HTML5, CSS3, and JavaScript.
- Source code shall be maintained using Git version control.
- The deployed service shall use HTTPS through the cloud-hosting platform.
- Dates displayed to users shall be unambiguous, and stored date/time values shall follow Django's timezone-aware conventions.
- Demonstration payment screens shall clearly state that no real money is transferred.

#### 3.2.3 External Requirements

**Security**

- Booking creation shall require verified Gmail authentication.
- Django CSRF protection shall protect state-changing form submissions.
- PNR access shall require ownership or matching mobile-number verification.
- Cab pickup OTPs shall be stored as password hashes rather than plain text.
- Private cab dispatch links shall use unguessable UUID tokens.
- Server-side validation shall be applied even when browser validation is available.
- Sensitive production communication shall use HTTPS.

**Privacy**

- Passenger contact and travel information shall be shown only to authorized or verified users.
- Cab call recording consent shall be collected before a relayed call is created.
- Travel and communication records shall be used only for the stated academic and operational purposes.

**Interoperability**

- ETORS shall integrate with the parent application's Google authentication flow.
- The application shall operate with Django-supported relational databases and Render-compatible deployment services.
- A production version may replace demonstration payment, railway inventory, messaging, mapping, and cab data with approved external APIs.

### 3.3 Interface Specification

**User Interface**

- ETORS home and train-search page
- Train search-results cards
- Gmail authentication redirect
- Passenger and booking form
- Dummy train-payment page
- Payment-success and PNR confirmation page
- PNR/mobile verification form
- Booking-detail and cancellation page
- BOOKMYCAB dispatch and OTP page
- Dummy cab UPI payment page
- Cab call-session page
- Documentation and chatbot interfaces
- Django administration interface

**Hardware Interface**

- Desktop computer or laptop
- Tablet or smartphone
- Keyboard, mouse, or touch input
- Internet connection

**Software Interface**

- Django framework and ORM
- PostgreSQL or another configured relational database
- Google OAuth authentication from the parent system
- Render cloud platform
- Modern web browser

**Communication Interface**

- HTTPS for browser-to-server communication in deployment
- Secure database connectivity
- Session cookies for authenticated and verified workflows
- POST requests protected by CSRF tokens for state changes

## 4. Appendices

### Hardware Requirements

- Dual-core processor or better
- 4 GB RAM minimum for a development workstation
- 10 GB free disk space for development tools and project files
- Reliable internet connection

### Software Requirements

- Windows, Linux, or macOS development environment
- Python 3.10 or later
- Django-compatible relational database
- HTML5, CSS3, and JavaScript
- Git
- Visual Studio Code, PyCharm, or equivalent editor
- Modern standards-compliant browser

### Academic Demonstration Notice

ETORS is an educational prototype. Train schedules, availability, payments, insurance policies, cab assignments, OTPs, calls, and salary deductions are demonstration data and processes. The application must not be represented as a live railway, banking, insurance, or transportation service.

## 5. Index

- A: Accessibility, Administrator, Authentication, Availability
- B: Berth, Booking, BOOKMYCAB
- C: Cab, Cancellation, Capacity, CSRF
- D: Database, Django, Dispatch
- F: Fare, Functional Requirements
- G: Gmail Authentication, GUI
- I: Insurance, Interface, Interoperability
- O: OAuth, OTP
- P: Passenger, Payment, Performance, PNR, Privacy
- R: Reliability, Render, Reservation
- S: Scope, Search, Seat, Security, Station
- T: Train, Travel Class
- U: UPI, Usability
