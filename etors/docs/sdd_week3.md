# ETORS Week 3 - Software Design Document (SDD)

## 1. System Architecture

ETORS uses a layered Django web architecture:

1. **Presentation layer** — responsive Django templates for search, booking, payment, PNR and cab workflows.
2. **Routing and controller layer** — `etors/urls.py` maps requests to views; views coordinate validation, sessions and responses.
3. **Business service layer** — `etors/services.py` calculates availability, fares, insurance, seats, cab schedules and payment reconciliation.
4. **Domain and persistence layer** — Django models represent railway and cab records and use PostgreSQL through the ORM.
5. **Integration and deployment layer** — Google OAuth provides login and Render hosts the production service over HTTPS.

This separation keeps presentation code independent from core fare and allocation rules and makes each layer easier to test.

## 2. Major Modules

| Module | Main responsibility |
|---|---|
| Train Search | Validate route/date and display matching active trains with calculated availability. |
| Authentication | Establish a verified Gmail-backed ETORS session before booking. |
| Reservation | Capture contact/passenger data, class and berth preferences; prevent capacity violations. |
| Payment | Present and process a safe dummy payment before confirmation. |
| PNR Management | Generate a unique PNR, authorize access using mobile verification and support cancellation. |
| BOOKMYCAB | Validate vehicle capacity and destination, schedule pickup, allocate a dummy driver and manage cab payment. |
| Help and Documentation | Serve Weeks 1–3 and answer common questions through the ETORS assistant. |

## 3. Data Design

### 3.1 Core Entities

| Entity | Important fields | Relationships |
|---|---|---|
| Station | code, name, city | Source/destination for trains; pickup point for cabs. |
| Train | number, name, schedule, capacity, sleeper fare, AC fare, active | References source and destination stations; has many bookings. |
| Booking | PNR, journey date, class, fare, contact data, status, insurance | References a train and authenticated user; has passengers and optionally one cab. |
| Passenger | name, age, gender, berth preference, allocated seat | Belongs to one booking. |
| CabBooking | reference, cab type, pickup/drop, schedule, fare, driver, OTP hash, payment status | One-to-one with a train booking; references pickup station. |
| CabCallLog | call reference, timestamps and dummy recording metadata | Belongs to a cab booking. |

### 3.2 Relationship Summary

```text
Station 1 ─── * Train * ─── 1 Station
                    │
                    │ 1
                    │
                    * Booking 1 ─── * Passenger
                        │
                        │ 0..1
                        │
                        1 CabBooking 1 ─── * CabCallLog
```

Foreign-key protection preserves stations and trains referenced by operational records. Unique PNR, cab reference and dispatch tokens provide stable identifiers for protected workflows.

## 4. Component Design

### 4.1 Search Flow

1. `SearchForm` validates source, destination and date.
2. The home view queries active trains for the selected route.
3. `train_availability()` counts confirmed passengers for each train/date.
4. The home template presents schedule, fare context and a booking action.

### 4.2 Booking and Payment Flow

1. The booking view verifies the ETORS Gmail session.
2. `BookingForm` validates contact, passenger, class, berth and optional cab details.
3. Valid data is stored temporarily in the session for the payment step.
4. The payment view rechecks availability within a database transaction.
5. A booking, its passengers, insurance reference and optional cab booking are created.
6. A seat number and unique 10-digit PNR are returned on the confirmation page.

### 4.3 Protected PNR Flow

1. The user submits a 10-digit PNR and registered mobile number.
2. The application compares both values before authorizing the PNR in the session.
3. Only authenticated ownership or an authorized session may open the detail page.
4. Cancellation updates the status from `CONFIRMED` to `CANCELLED`; availability calculations then release those seats.

### 4.4 BOOKMYCAB Flow

1. The passenger selects a vehicle compatible with group size and supplies the destination.
2. `create_cab_booking()` schedules pickup before train arrival and assigns demonstration driver data.
3. A six-digit pickup OTP is generated; only its secure hash is stored.
4. The cab payment and dispatch views use non-guessable reference/UUID routes.
5. `reconcile_cab_payment()` models overdue payment as a driver deduction for the academic scenario.

## 5. Validation and Security Design

- Django forms centralize date, phone, passenger, vehicle-capacity and coordinate validation.
- CSRF tokens protect POST forms.
- Gmail authentication gates booking creation.
- PNR plus registered mobile protects passenger details from PNR-only disclosure.
- Database transactions keep booking, passenger and cab creation consistent.
- Hashed pickup OTPs and random dispatch tokens reduce exposure of cab credentials.
- Templates escape ordinary user data; only project-controlled Markdown documentation is rendered as HTML.

## 6. User Interface Design

The interface uses a shared ETORS base template with persistent search, documentation, BOOKMYCAB, PNR and login navigation. Cards, clear status badges and responsive grids support both desktop and mobile use. The documentation page follows the AECLibrary reference by placing each lab week in a distinct, readable card.

## 7. Deployment Design

The Django application is version-controlled with Git and deployed from the main branch to Render. PostgreSQL provides persistent production data. Environment variables hold deployment credentials and OAuth configuration. Django migrations version schema changes, while production checks validate configuration before release.

## 8. Design Goals

- Prevent overselling and partial reservations.
- Protect passenger and pickup information.
- Keep fares and scheduling rules centralized.
- Provide a short, understandable booking journey.
- Support extension to additional routes, trains, passenger rules and real integrations.

## 9. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Concurrent users reserve the final seat | Recheck availability inside the transactional payment workflow. |
| PNR enumeration exposes personal data | Require the matching registered mobile and session authorization. |
| Incorrect cab capacity | Validate passenger count against the selected vehicle capacity. |
| Train crosses midnight | Add one day when calculated arrival is earlier than departure. |
| Third-party login or hosting outage | Display clear errors and retain modular integration boundaries. |
| Demo services mistaken for real services | Label payment, insurance, support and railway data as academic simulations. |

## 10. Conclusion

The ETORS design combines Django's layered structure with explicit service functions and relational models. It supports a complete academic reservation workflow while emphasizing transactional consistency, privacy, responsive interaction and maintainable components.
