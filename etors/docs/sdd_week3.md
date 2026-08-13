# Week 3 - Software Design Document (SDD)

## 1. System Architecture

**Figure 3.1: Layered System Architecture of ETORS**

![ETORS layered system architecture](/static/etors/images/etors_system_architecture.svg)

Figure 3.1 shows the architecture of the E-Ticketing Online Reservation System (ETORS). Passengers, cab drivers, and administrators access responsive web interfaces over HTTPS. Requests pass through authentication and session controls to Django routing, views, forms, and business services. The application uses Django models and the ORM to persist railway reservation and cab-dispatch data in PostgreSQL. Google OAuth supports passenger identity verification, while Render provides cloud hosting and automated deployment.

### 1.1 Architecture Overview

ETORS follows a layered, modular Django architecture with six logical layers:

1. Users Layer
2. Presentation Layer
3. Authentication and Security Layer
4. Application and Business-Service Layer
5. Data Layer
6. Integration and Deployment Layer

Each layer has a defined responsibility. User-interface changes can be made without changing fare calculations; payment or cab rules can be updated in service functions without rewriting templates; and database access remains centralized through Django models and the ORM. This separation improves security, testability, maintainability, and future extensibility.

### 1.2 Architectural Style

The application uses Django's Model-Template-View pattern:

- **Model:** Represents stations, trains, bookings, passengers, cab bookings, and call logs.
- **Template:** Produces responsive HTML for search, booking, payment, PNR, cab, and documentation pages.
- **View:** Coordinates HTTP requests, forms, sessions, services, database transactions, and responses.
- **Service:** Encapsulates reusable availability, fare, insurance, seat, cab-scheduling, and payment-reconciliation rules.

### 1.3 Request and Data Flow

1. The browser sends an HTTPS request to an ETORS URL.
2. Django routing selects the appropriate view.
3. Authentication, ownership, CSRF, and session rules are applied.
4. Django forms validate route, date, passenger, contact, PNR, and cab inputs.
5. Views call business services for availability, fare, seat, insurance, and cab calculations.
6. Models read or write relational data through Django's ORM.
7. A template returns a responsive result, confirmation, or validation message.

## 2. Users Layer

### 2.1 Passenger

Passengers are the primary ETORS users. They can:

- Search active trains by source, destination, and journey date.
- View schedules, running days, fares, and calculated availability.
- Authenticate with a verified Gmail account before booking.
- Select travel class, berth preference, and optional train insurance.
- Enter contact details and details for one or more passengers.
- Complete a dummy UPI, card, or net-banking payment.
- Receive a unique 10-digit PNR and allocated seat numbers.
- Retrieve a booking using the PNR and registered mobile number.
- View booking, passenger, insurance, and cab information.
- Cancel a confirmed reservation.
- Request an optional BOOKMYCAB destination transfer.
- Ask supported questions through the ETORS chatbot.

**Responsibilities**

- Provide accurate journey, contact, and passenger information.
- Keep the PNR and pickup OTP confidential.
- Verify booking details before confirming the demonstration payment.
- Use the system only for its stated academic purpose.

### 2.2 Cab Driver

The cab driver is a limited demonstration role. The driver can:

- Open a private UUID-based dispatch link.
- View the pickup station, train arrival, destination, and vehicle assignment.
- Verify the passenger using a time-limited pickup OTP.
- Initiate and complete a company-relayed call session.
- Direct the passenger to the dummy UPI payment workflow after verification.

**Responsibilities**

- Use only the assigned private dispatch link.
- Confirm the correct OTP before marking pickup verification.
- Respect call-recording consent and passenger privacy.

### 2.3 Administrator

Administrators supervise master and operational data through Django administration facilities. They can:

- Add and update stations.
- Add, update, activate, or deactivate trains.
- Maintain schedules, running days, capacity, and fares.
- Inspect booking, passenger, cab, payment-status, and call-log records.
- Correct demonstration data when authorized.
- Monitor deployed application behaviour and database health.

**Responsibilities**

- Maintain accurate train and station information.
- Protect administrative credentials and passenger data.
- Review system errors, backups, migrations, and deployment status.

## 3. Presentation Layer

The presentation layer uses Django templates, HTML5, CSS3, and JavaScript. A shared ETORS base template provides consistent branding, navigation, messages, responsive layout, and accessibility behaviour.

### 3.1 Main Interfaces

- **Home and Search:** Source, destination, date, train results, availability, and fares.
- **Booking:** Contact, class, passenger, berth, insurance, and optional cab fields.
- **Train Payment:** Fare summary and dummy payment-method selection.
- **Payment Success:** PNR, seats, policy references, and cab-dispatch confirmation.
- **PNR Verification:** Ten-digit PNR and registered-mobile verification.
- **PNR Details:** Journey, passengers, status, fares, insurance, cab, and cancellation.
- **Cab Dispatch:** Driver assignment, pickup schedule, OTP verification, and call action.
- **Cab Payment:** Post-pickup dummy UPI payment and payment status.
- **Cab Call Session:** Company-relayed demonstration call and recording metadata.
- **Documentation:** Week-based problem, requirements, and design documents.
- **Chatbot:** Contextual answers to supported ETORS questions.

### 3.2 Interface Design Principles

- Responsive cards and grids for desktop and mobile screens.
- Clear labels, validation errors, success messages, and status badges.
- Keyboard-accessible links, controls, and forms.
- Minimal disclosure of passenger and cab information.
- Explicit labels identifying payment and transport operations as demonstrations.

## 4. Authentication and Security Layer

The authentication and security layer protects reservation creation, booking retrieval, cab dispatch, and state-changing actions.

### 4.1 Gmail Authentication

Booking requires an authenticated application user and an ETORS session flag established by the parent Google Gmail login flow. Unauthenticated users are redirected to the Google login route and returned to their intended booking page after successful verification.

### 4.2 Booking Authorization

A booking detail page is available only when:

- The authenticated user owns the booking, or
- The visitor has verified the exact PNR with its registered mobile number during the current session.

This prevents disclosure based on PNR knowledge alone.

### 4.3 Cab Security

- Cab dispatch pages use non-guessable UUID tokens.
- Pickup OTPs are stored using Django password hashing rather than plain text.
- OTP attempts and expiration times limit repeated verification.
- Cab payment is allowed only after successful pickup verification.
- Company-relayed call records require passenger consent.

### 4.4 Web Security Controls

- Django CSRF protection for POST requests.
- Server-side form validation for all critical inputs.
- Secure session-based workflow state.
- ORM queries instead of manually concatenated SQL.
- HTTPS communication on Render.
- Environment variables for deployment secrets and service credentials.
- Escaped user-supplied template values.

## 5. Application Layer

The application layer contains routing, request coordination, validation, business rules, and response generation.

### 5.1 URL Routing

`etors/urls.py` maps URLs to views for:

- Home and train search
- Documentation and chatbot
- Booking and payment
- PNR verification, detail, and cancellation
- Cab dispatch, payment, and call sessions
- ETORS logout

### 5.2 Views

Views coordinate forms, authentication, sessions, services, transactions, and templates. They do not duplicate reusable fare or scheduling algorithms that belong in the service layer.

### 5.3 Forms and Validation

- `SearchForm` validates route and journey date.
- `BookingForm` validates passenger count, contact data, travel class, cab capacity, destination, map coordinates, and call consent.
- `PNRForm` validates the ten-digit PNR and registered mobile number.

### 5.4 Business Services

`etors/services.py` provides:

- Train availability calculation
- Class-based fare calculation
- Fare-option generation
- Train-insurance policy generation
- Seat-number allocation
- Cab fare and schedule calculation
- Cab, driver, vehicle, OTP, and policy creation
- Cab amount-due calculation
- Expired cab-payment reconciliation

### 5.5 Transaction Management

The payment workflow creates a booking, passengers, seat assignments, insurance, and optional cab record inside a database transaction. Availability is checked again before creation. If any required operation fails, the transaction is rolled back so that incomplete reservation data is not retained.

## 6. Modules Layer

### 6.1 Train Search Module

**Functions**

- Validate source, destination, and date.
- Query active trains serving the selected route.
- Display schedule and running information.
- Calculate remaining seats for the selected date.
- Present supported class fares and booking actions.

### 6.2 Reservation Module

**Functions**

- Enforce verified Gmail authentication.
- Capture contact and passenger details.
- Validate travel class and berth preferences.
- Prevent reservations that exceed availability.
- Store pending booking data securely in the session.

### 6.3 Payment and Confirmation Module

**Functions**

- Calculate ticket and insurance totals.
- Display dummy UPI, card, and net-banking methods.
- Recheck availability within a transaction.
- Generate booking, passenger, PNR, seat, and policy records.
- Display confirmation without transferring real money.

### 6.4 PNR Management Module

**Functions**

- Validate PNR format.
- Match the registered mobile number.
- Authorize booking-detail access in the session.
- Display reservation and passenger status.
- Cancel confirmed train and linked cab bookings.
- Release cancelled passenger seats from availability calculations.

### 6.5 BOOKMYCAB Module

**Functions**

- Select a vehicle suitable for passenger count.
- Capture drop address and optional coordinates.
- Calculate cab fare and insurance.
- Schedule pickup relative to train arrival.
- Assign demonstration driver and vehicle data.
- Generate cab reference, private dispatch token, and pickup OTP.
- Verify pickup and process dummy UPI payment.
- Reconcile expired payment through the academic driver-deduction rule.

### 6.6 Cab Communication Module

**Functions**

- Capture recording consent during cab selection.
- Generate company call and recording references.
- Record call start and completion timestamps.
- Avoid exposing direct personal calling as the primary workflow.

### 6.7 Help and Documentation Module

**Functions**

- Display Week 1, Week 2, and Week 3 documents.
- Render controlled Markdown as HTML.
- Answer supported ETORS questions.
- Reject empty or unrelated chatbot requests with clear feedback.

### 6.8 Administration Module

**Functions**

- Maintain stations and trains.
- Configure capacity, fares, schedules, and active status.
- Inspect reservation, passenger, cab, and call records.
- Support controlled correction and demonstration-data maintenance.

## 7. Data Layer

The data layer uses Django models and the ORM with a relational production database. PostgreSQL supplies persistent storage on Render.

### 7.1 Entity Relationship Summary

```text
Station (source) 1 ─── * Train * ─── 1 Station (destination)
                           │
                           │ 1
                           │
                           * Booking * ─── 0..1 User
                               │
                  ┌────────────┴────────────┐
                  │ 1                       │ 1
                  │                         │
                  * Passenger               0..1 CabBooking
                                                  │
                                                  │ 1
                                                  │
                                                  * CabCallLog
```

`PROTECT` is used where deleting referenced station or train data would damage operational history. Passenger and cab records use cascading relationships where their parent booking is the owning record. A booking may have zero or one cab booking, while a cab booking may have multiple call logs.

### 7.2 Data Integrity

- Station codes and train numbers are unique.
- PNRs and cab references are generated uniquely.
- Cab dispatch tokens use unique UUID values.
- Fares use fixed-precision decimal fields.
- Positive-value validators protect capacity, fare, and passenger-age values.
- Model choices constrain booking, class, cab, and payment status values.
- Foreign keys preserve entity relationships.
- Database transactions prevent partial booking creation.

## 8. Integration and Deployment Layer

### 8.1 Google Authentication

The parent application supplies Google OAuth-based Gmail authentication. ETORS consumes the authenticated user and session marker instead of managing a separate passenger password database.

### 8.2 PostgreSQL

PostgreSQL stores application and ETORS relational data in production. Django migrations version and apply schema changes.

### 8.3 Render Cloud

Render provides:

- Python web-service hosting
- HTTPS termination
- Environment-variable configuration
- Build and start commands
- Static-file serving support
- Deployment from the Git main branch
- Automatic dependency installation and Django migrations during build

### 8.4 Demonstration Integration Boundaries

Railway inventory, train payment, insurance, cab allocation, UPI, calls, and salary deductions are implemented as academic simulations. Service boundaries allow approved production APIs to replace these implementations later without redesigning the whole application.

## 9. Design Goals

- **Security:** Protect passenger, PNR, OTP, session, and cab-dispatch information.
- **Consistency:** Prevent partial bookings and release cancelled capacity correctly.
- **Usability:** Provide a short, understandable reservation workflow.
- **Modularity:** Separate templates, forms, views, services, and models.
- **Maintainability:** Centralize rules and document responsibilities.
- **Scalability:** Support additional stations, trains, bookings, and passengers.
- **Portability:** Operate in modern desktop and mobile browsers.
- **Testability:** Keep validation and service behaviour independently verifiable.
- **Extensibility:** Permit future real railway, payment, mapping, messaging, and cab integrations.

## 10. Advantages of the Proposed Architecture

- Clear layered separation of concerns
- Secure Gmail-gated booking
- Protected PNR/mobile booking retrieval
- Centralized fare, availability, seat, and cab rules
- Atomic booking and passenger creation
- Responsive desktop and mobile interface
- Relational data integrity through Django ORM
- Hashed OTPs and private cab dispatch tokens
- Cloud deployment with HTTPS and migrations
- Easier testing, maintenance, and future integration

## 11. Data Tables

### Table 1: Station

| S.No | Column | Type / Length | Constraint | Description |
|---|---|---|---|---|
| 1 | id | Big Integer | Primary Key | Internal station identifier |
| 2 | code | Varchar(8) | Unique | Railway station code |
| 3 | name | Varchar(120) | Required | Station name |
| 4 | city | Varchar(80) | Required | City served by the station |

### Table 2: Train

| S.No | Column | Type / Length | Constraint | Description |
|---|---|---|---|---|
| 1 | id | Big Integer | Primary Key | Internal train identifier |
| 2 | number | Varchar(6) | Unique | Train number |
| 3 | name | Varchar(120) | Required | Train name |
| 4 | source_id | Foreign Key | Protected | Departure station |
| 5 | destination_id | Foreign Key | Protected | Arrival station |
| 6 | departure_time | Time | Required | Scheduled departure |
| 7 | arrival_time | Time | Required | Scheduled arrival |
| 8 | duration | Varchar(30) | Required | Journey duration display |
| 9 | running_days | Varchar(20) | Default: Daily | Operating-day description |
| 10 | seat_capacity | Positive Integer | Default: 120 | Total demonstration capacity |
| 11 | sleeper_fare | Decimal(8,2) | Minimum 1 | Base sleeper fare |
| 12 | ac_fare | Decimal(8,2) | Minimum 1 | Base AC fare |
| 13 | active | Boolean | Default: True | Search and booking availability |

### Table 3: Booking

| S.No | Column | Type / Length | Constraint | Description |
|---|---|---|---|---|
| 1 | id | Big Integer | Primary Key | Internal booking identifier |
| 2 | pnr | Varchar(10) | Unique | Generated Passenger Name Record |
| 3 | user_id | Foreign Key | Optional, SET NULL | Authenticated booking owner |
| 4 | train_id | Foreign Key | Protected | Reserved train |
| 5 | journey_date | Date | Required | Date of travel |
| 6 | travel_class | Varchar(2) | Choice | General, Sleeper, or AC class |
| 7 | contact_name | Varchar(100) | Required | Booking contact |
| 8 | contact_email | Email | Required | Contact email |
| 9 | contact_phone | Varchar(15) | Required | Registered verification mobile |
| 10 | total_fare | Decimal(10,2) | Required | Calculated train amount |
| 11 | train_insurance_policy | Varchar(24) | Optional | Demonstration policy reference |
| 12 | train_insurance_premium | Decimal(8,2) | Default: 0 | Insurance premium |
| 13 | status | Varchar(12) | Choice | Confirmed or cancelled |
| 14 | booked_at | DateTime | Auto | Creation timestamp |
| 15 | cancelled_at | DateTime | Optional | Cancellation timestamp |

### Table 4: Passenger

| S.No | Column | Type / Length | Constraint | Description |
|---|---|---|---|---|
| 1 | id | Big Integer | Primary Key | Internal passenger identifier |
| 2 | booking_id | Foreign Key | Cascade | Parent booking |
| 3 | name | Varchar(100) | Required | Passenger name |
| 4 | age | Positive Small Integer | Minimum 1 | Passenger age |
| 5 | gender | Varchar(1) | Choice | Male, female, or other |
| 6 | berth_preference | Varchar(30) | Optional | Requested berth type |
| 7 | seat_number | Varchar(12) | Required | Allocated demonstration seat |

### Table 5: Cab Booking

| S.No | Column | Type / Length | Constraint | Description |
|---|---|---|---|---|
| 1 | id | Big Integer | Primary Key | Internal cab-booking identifier |
| 2 | booking_id | One-to-One Key | Cascade, Unique | Associated train booking |
| 3 | reference | Varchar(12) | Unique | Generated cab reference |
| 4 | dispatch_token | UUID | Unique | Private driver-dispatch token |
| 5 | pickup_otp_hash | Varchar(128) | Required | Hashed pickup OTP |
| 6 | pickup_otp_expires_at | DateTime | Required | OTP expiry |
| 7 | pickup_verified_at | DateTime | Optional | Successful verification time |
| 8 | payment_deadline | DateTime | Required | Cab payment deadline |
| 9 | payment_status | Varchar(20) | Choice | Pending, paid, deducted, or cancelled |
| 10 | payment_method | Varchar(8) | Optional | Dummy payment method |
| 11 | paid_at | DateTime | Optional | Payment completion time |
| 12 | driver_salary_deduction | Decimal(8,2) | Default: 0 | Academic overdue-payment result |
| 13 | cab_type | Varchar(8) | Choice | Selected vehicle type |
| 14 | pickup_station_id | Foreign Key | Protected | Destination station pickup |
| 15 | drop_address | Varchar(240) | Required | Passenger destination |
| 16 | drop_latitude | Decimal(9,6) | Optional | Map latitude |
| 17 | drop_longitude | Decimal(9,6) | Optional | Map longitude |
| 18 | train_arrival_at | DateTime | Required | Expected train arrival |
| 19 | cab_arrival_at | DateTime | Required | Scheduled cab arrival |
| 20 | fare | Decimal(8,2) | Required | Cab fare |
| 21 | cab_insurance_policy | Varchar(24) | Optional | Cab policy reference |
| 22 | cab_insurance_premium | Decimal(8,2) | Default: 0 | Cab insurance premium |
| 23 | driver_name | Varchar(100) | Required | Assigned demonstration driver |
| 24 | driver_phone | Varchar(15) | Required | Driver contact number |
| 25 | vehicle_number | Varchar(20) | Required | Assigned vehicle registration |
| 26 | status | Varchar(12) | Choice | Scheduled, arrived, completed, cancelled |
| 27 | created_at | DateTime | Auto | Creation timestamp |

### Table 6: Cab Call Log

| S.No | Column | Type / Length | Constraint | Description |
|---|---|---|---|---|
| 1 | id | Big Integer | Primary Key | Internal call identifier |
| 2 | cab_booking_id | Foreign Key | Cascade | Parent cab booking |
| 3 | reference | Varchar(18) | Unique | Generated call reference |
| 4 | company_number | Varchar(20) | Default | Company relay number |
| 5 | recording_reference | Varchar(24) | Unique | Demonstration recording reference |
| 6 | status | Varchar(12) | Choice | Active or completed |
| 7 | started_at | DateTime | Auto | Call start timestamp |
| 8 | ended_at | DateTime | Optional | Call completion timestamp |

## 12. Risk Management Document

### 12.1 Project Name

E-Ticketing Online Reservation System (ETORS)

### 12.2 Document Control

| Item | Value |
|---|---|
| Document ID | ETORS-RMMM-01 |
| Document Owner | ETORS Development Team |
| Version | 1.0 |
| Review Cycle | Twice per month and before release |

### 12.3 Risk Management Methodology

1. **Identify:** Record technical, operational, security, privacy, and schedule risks.
2. **Assess:** Estimate likelihood and impact.
3. **Respond:** Avoid, reduce, transfer, or accept each risk.
4. **Monitor:** Review indicators, assigned actions, and residual exposure.

### 12.4 Stakeholders

- Project Manager
- Development and Test Team
- College Authorities
- System Administrator
- Passengers and Student Evaluators
- Demonstration Cab Operators
- Hosting and Authentication Providers

### 12.5 Risk Register

| Risk ID | Risk Description | Likelihood | Impact | Priority |
|---|---|---|---|---|
| ET-R01 | Concurrent users attempt to reserve the final available seat | Possible | High | High |
| ET-R02 | PNR guessing exposes passenger information | Possible | Critical | Critical |
| ET-R03 | Incorrect fare or class calculation confirms the wrong amount | Unlikely | High | High |
| ET-R04 | Google authentication is unavailable | Possible | Medium | Medium |
| ET-R05 | Render or database service is unavailable | Possible | High | High |
| ET-R06 | Cab OTP or private dispatch information is disclosed | Unlikely | Critical | High |
| ET-R07 | Incorrect train-arrival rollover schedules a cab on the wrong date | Possible | High | High |
| ET-R08 | Users mistake dummy payment or transport data for a real service | Possible | High | High |
| ET-R09 | A migration or release causes incompatible schema/application state | Unlikely | Critical | High |
| ET-R10 | Passenger data is retained or displayed beyond authorized use | Unlikely | Critical | High |

### 12.6 Risk Assessment Matrix

| Impact / Likelihood | Rare (1) | Unlikely (2) | Possible (3) | Likely (4) |
|---|---:|---:|---:|---:|
| Low (1) | 1 | 2 | 3 | 4 |
| Medium (2) | 2 | 4 | 6 | 8 |
| High (3) | 3 | 6 | 9 | 12 |
| Critical (4) | 4 | 8 | 12 | 16 |

Scores 1–3 are low, 4–6 are medium, 8–9 are high, and 12–16 are critical.

### 12.7 Risk Response Plan

| Risk ID | Owner | Mitigating Action | Contingent Action | Status |
|---|---|---|---|---|
| ET-R01 | Backend Developer | Recheck availability inside the transaction before record creation | Reject the payment confirmation and ask the passenger to select another train | Monitored |
| ET-R02 | Security Owner | Require PNR plus registered mobile or authenticated ownership | Invalidate verified sessions and review access logs | Controlled |
| ET-R03 | Backend Developer | Centralize fare rules and test every class | Disable affected class until corrected | Monitored |
| ET-R04 | System Administrator | Preserve modular authentication redirect and clear error feedback | Temporarily suspend new bookings while retaining public search | Accepted |
| ET-R05 | DevOps Owner | Use managed hosting, health checks, and database backups | Restore service/database from the latest valid release or backup | Monitored |
| ET-R06 | Security Owner | Hash OTPs, expire attempts, and use UUID dispatch tokens | Cancel/reissue the cab assignment and token | Controlled |
| ET-R07 | Backend Developer | Handle arrival times earlier than departure as next-day arrival | Correct schedule and notify affected demonstration users | Controlled |
| ET-R08 | Product Owner | Label railway, payment, insurance, calls, and cabs as demonstrations | Suspend the misleading workflow until labels are corrected | Controlled |
| ET-R09 | DevOps Owner | Run migrations and checks during deployment; version migrations in Git | Roll forward with a corrective migration or restore the prior service release | Monitored |
| ET-R10 | Data Controller | Apply ownership checks and minimum disclosure | Remove unauthorized access and investigate the exposure | Controlled |

### 12.8 Risk Monitoring Schedule

- Review open risks on the first and third Monday of each month.
- Review security, migration, and deployment risks before every production release.
- Record incidents and update likelihood, impact, owner, and response actions.

## 13. Configuration Management Document

### 13.1 Project Name

E-Ticketing Online Reservation System (ETORS)

### 13.2 Document Control

| Item | Value |
|---|---|
| Document Number | ETORS-CM-01 |
| Product | ETORS Django Module |
| Release State | Version controlled and cloud deployed |
| Document Author | Development Team |
| Product Owner | Project Manager / College Authority |

### 13.3 Configuration Items

| S.No | Configuration Item | Location / Identifier | Control Method |
|---|---|---|---|
| 1 | Requirements Document | `etors/docs/srd_week2.md` | Git revision |
| 2 | Design Document | `etors/docs/sdd_week3.md` | Git revision |
| 3 | Architecture Diagram | `etors/static/etors/images/etors_system_architecture.svg` | Git revision |
| 4 | URL Configuration | `etors/urls.py` | Code review and tests |
| 5 | Views | `etors/views.py` | Code review and tests |
| 6 | Forms | `etors/forms.py` | Validation tests |
| 7 | Business Services | `etors/services.py` | Unit and integration tests |
| 8 | Data Models | `etors/models.py` | Migration control |
| 9 | Templates | `etors/templates/etors/` | UI review and tests |
| 10 | Static Assets | `etors/static/etors/` | Git revision and deployment collection |
| 11 | Database Schema | Django migration files | Ordered migration history |
| 12 | Deployment Configuration | `render.yaml`, build/start scripts | Git and environment configuration |

### 13.4 Version and Change Control

1. Changes are made on a controlled Git working branch.
2. Modified files are reviewed with `git diff`.
3. Relevant Django tests, checks, and migration checks are executed.
4. Configuration and schema changes include migration files when required.
5. A descriptive commit records the approved change.
6. The main branch is pushed to the remote repository.
7. Render builds the revision, installs dependencies, applies migrations, and starts the service.
8. The deployed interface and critical workflows are verified.

### 13.5 Naming and Identification

- Source files use Python and Django naming conventions.
- Database migrations use Django-generated sequential identifiers.
- PNR, cab, call, policy, and dispatch identifiers follow separate formats.
- Releases are identified by Git commit hash and deployment timestamp.
- Secrets are identified by environment-variable name and are not stored in source files.

### 13.6 Backup and Recovery

- Source and documentation are retained in the remote Git repository.
- Database backups follow the capabilities and policy of the managed database service.
- Environment-variable values are managed outside source control.
- Recovery uses a verified Git revision plus the latest compatible database backup.
- Corrective schema changes use forward migrations whenever practical.

### 13.7 Configuration Audit

Before release, the team shall confirm:

- Only intended files are included in the commit.
- `git diff --check` reports no whitespace errors.
- Django reports no missing migrations.
- Migrations and system checks complete successfully.
- Automated ETORS tests pass.
- Static architecture assets load correctly.
- The live documentation and reservation routes return successful responses.
- Demonstration notices remain visible.

## 14. Conclusion

The ETORS design provides a secure, modular, scalable, and maintainable academic reservation architecture. Its layered organisation separates user interfaces, authentication, request handling, business services, relational data, and deployment responsibilities. Atomic booking creation, protected PNR retrieval, hashed pickup OTPs, explicit simulation boundaries, and version-controlled cloud deployment address the main consistency and security risks.

The architecture supports the current end-to-end workflow—train search, authenticated reservation, dummy payment, PNR confirmation, booking enquiry, cancellation, and optional BOOKMYCAB transfer—while preserving clear extension points for approved real-world railway, payment, insurance, mapping, messaging, and transportation integrations.
