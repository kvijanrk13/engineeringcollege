# Week 1 - Problem Statement

## 1. PROBLEM STATEMENTS

### II. E-TICKETING – ONLINE RESERVATION SYSTEM

An Online Reservation System ORS is a project that manages ticket booking electronically according to user needs. For any public transporting system (Bus, Train or Airlines) the key element is passenger. Passengers travel around using these systems as part of their day-to-day work. The main problem in these systems is lack of sufficient vehicles as well as seats specifically during peak hours and seasons. The passengers always find it difficult to get tickets and empty seats during these time periods. So they usually opt for private transportation facilities which effects government revenue. So there is a need for system which helps passengers to reserve/book tickets in advance so that they do comfortable journey.

**Existing System:**

Currently most transportation systems do not have a particular developed system for enhancing the online booking of tickets. This implies that there is lack of any kind of interaction between the transport company and the customers. In most of time, anyone wishing to do ticket booking has to visit the premises of the company to make the necessary inquiries or has to contact the manager in the company by phone call in order to inquire about the tickets and seats. The main challenge associated with the current system is that passengers have to contact booking counter which is consumption of time and burden which would be avoided by having an automated system.

**Proposed System:**

E-Ticketing / Online Reservation System ORS is a web system that manages all the reservation related functions like booking reservation/ticket, checking reservation status, payment for confirmed reservation, cancellation and refund. With the help of ORS people can book their tickets online through internet, sitting in their home by a single click of mouse.

The proposed system has the following advantages:
1. Customer can buy his ticket through the online system and no need to queue up to buy tickets at the counter.
2. Customer can check the time of departure and arrival through the system.
3. Using their credit/debit cards or other payment modes passengers can easily get their tickets.
4. The number of staff at the counter can be reduced.

---

## 2. System Overview for ETORS

The ETORS (E-Ticketing Online Reservation System) is a web-based application designed to demonstrate an efficient online railway ticket reservation platform. It provides:

- **Student Portal**: Students can search trains by source, destination and date, view live seat availability, book tickets with a verified Gmail account, track booking status with PNR, and arrange destination cab services.
- **Admin Portal**: Administrators can manage train inventory, monitor bookings, view passenger details, generate reports, and maintain demonstration data.
- **Payment Integration**: Dummy payment gateway for demonstrating secure transaction flow.
- **Authentication**: Google OAuth 2.0 for secure student login.
- **Cab Integration**: BOOKMYCAB integration for station transfer services.

---

## 3. Key Objectives

1. **Train Search & Discovery**
   - Search trains by source, destination, and journey date
   - View train details (name, departure time, arrival time, duration)
   - Real-time availability checking for seats

2. **Booking Management**
   - User registration and Gmail-based authentication
   - Ticket booking with passenger details
   - Unique PNR generation for successful bookings
   - Dummy payment processing

3. **PNR & Status Tracking**
   - Secure PNR verification using mobile number
   - Booking status inquiry
   - Booking cancellation and refund handling

4. **Cab Integration**
   - BOOKMYCAB integration for destination transfers
   - Vehicle selection and fare calculation
   - Cab booking confirmation

5. **Reporting**
   - Booking statistics
   - Passenger demographics
   - Revenue and fare reports

---

## 4. Functional Requirements

1. The system should allow users to search for trains between selected stations.
2. The system should display train details such as name, departure time, arrival time, and duration.
3. The system should allow a user to book a ticket after logging in with a verified Gmail account.
4. The system should generate a unique PNR for successful booking.
5. The system should allow users to verify PNR status securely using PNR and mobile number.
6. The system should support dummy payment and reservation confirmation.
7. The system should allow integration with BOOKMYCAB for destination transfers.
8. The system should handle booking cancellations and refund calculations.

---

## 5. Non-Functional Requirements

- The interface should be simple and easy to use
- The system should provide clear feedback for errors and success messages
- The application should be responsive and accessible on desktop and mobile screens
- The system should be secure with proper authentication and data protection
- The system should handle multiple concurrent users efficiently

---

## 6. Technology Stack

- **Backend**: Django 3.1+ (Python)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: PostgreSQL (Neon)
- **Payments**: Dummy gateway (for demonstration)
- **Deployment**: Render Cloud Platform
- **Authentication**: Google OAuth 2.0
- **Cab Integration**: BOOKMYCAB API

---

## 7. Project Scope

ETORS is an academic project that demonstrates how an online railway reservation system operates. It includes train search, booking, PNR generation, dummy payment processing, PNR verification, and cab booking integration. The system is intended as a classroom demonstration and not a real railway reservation system. All data is demonstration data maintained for educational purposes.
