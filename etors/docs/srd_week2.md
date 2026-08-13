# ETORS Week 2 - Software Requirements Document (SRD)

## IV. E-TICKETING – ONLINE RESERVATION SYSTEM SRD

## 1. Introduction

### 1.1 Purpose

The purpose of this document is to record the requirements of an application that will automate the process of ticket reservation/booking. This document reflects the features expecting from the software and constraint imposed on the development of the system.

### 1.2 Scope

The system ORS is web based application.

The passengers will gain access to the available buses/trains per certain route and available seats by logging in through the customer's portal.

The staff will access the system by logging in via the staff portal where they can display the transport schedule and reserve seats and sell tickets.

### 1.3 Acronyms

- **ORS** – Online Reservation System
- **GUI** – Graphical User Interface
- **DBMS** - Database Management System

### 1.4 References

IEEE/ANSI 830-1998 SRD Standard

### 1.5 Overview

The rest of the document deals with all the main features of this software. It not only describes various functions but also gives details about how these functions are related to each other.

## 2. Project Description

### 2.1 Product Perspective

Before the automation, the system suffered from the following drawbacks:

- Since the number of passengers have drastically increased therefore maintaining and retrieving detailed record of passenger is extremely difficult.
- The existing system is highly manual involving a lot of paper work and calculation and therefore may be erroneous. This has led to inconsistency and inaccuracy in the maintenance of data.

Hence the railways reservation system is proposed with the following benefits:

- The computerization of the reservation system will reduce a lot of paperwork and hence the load on the airline administrative staff.
- The passenger, reservation, cancellation list can easily be retrieved and any required addition, deletion or updating can be performed.

### 2.2 Product Functions

There are two different users who will be using this product:

- Booking agents.
- Passengers.

The features that are available to the Booking Agent and Passenger are:

- Searching for train that are available between the "Departure location" and "Arrival location"
- Booking and Cancelling tickets
- Maintaining details of all the passengers supposed to travel
- Payment facility using various modes like credit/debit card

### 2.3 User Characteristics

- Users of the system should be comfortable with English language.
- User should be comfortable using general purpose applications on the computer system.

### 2.4 General Constraints

- The system must be user friendly

### 2.5 Assumptions and Dependencies

- Booking Agents will be having a valid user name and password to access the software
- The software needs booking agent to have complete knowledge of reservation system.
- Software is dependent on access to internet.

## 3. Specific Requirements

### 3.1 Functional Requirements

A functional requirement is a statement of how a system must behave. It defines what the system should do in order to meet the user's needs or expectations.

The following are some functional criteria for Ticketing System:

1. User registration and login
2. Train search and booking
3. Payment gateway integration
4. Seat selection and reservation
5. Email and SMS confirmations
6. Cancellation and refund options
7. Fare and schedule updates
8. Train tracking and live status updates
9. Feedback and ratings system
10. Accessibility for people with disabilities

### 3.2 Non-Functional Requirements

Non-functional requirements explain the limitations and constraints of the system to be designed. They define how the system should work internally (e.g., performance, security, etc.).

The non-functional requirements of Ticketing System:

#### 3.2.1 Product Requirements:

**Usability:**
- The booking agents shall be able to work with all the features of ticketing system with 1-2 days of training and the system shall assist the users by displaying help instructions.

**Performance:**
- The home page shall support 500 passenger requests per hour must with 5 seconds or less response time in a desktop/mobile browser over a 1Mbps connection.

**Reliability:**
- The system must perform without failure in 99.5 percent of uses during normal hours and 95 percent in peak seasons.

**Portability:**
- A system running on Windows 10 device must be able to run on Windows 11 device without any change in its behavior and performance.

**Scalability:**
- The system must be scalable enough to support 25000 visits at the same time while maintaining optimal performance.

**Availability:**
- The system must be available to passengers 98percent of the time every hour during business hours of the day.

**Maintainability:**
- The mean time to restore the system (MTTRS) following a system failure must not be greater than 10 minutes.

#### 3.2.2 Organizational Requirements:

**Delivery:**
- The developed system should be delivered as incremental versions to the client and the first version within 6-8 weeks of project initiation.

**Implementation:**
- The system shall implement with web technologies like HTML/JSP/PHP

**Standards:**
- The date/time format must be as follows: DD-MM-YYYY and HH:MM:SS on 0-24hr clock
- The payments must do under RBI controlled modes.

#### 3.2.3 External Requirements:

**Security:**
- The system user's data shall be encrypted in database and the travel history should be disclosed only for legal purposes.

**Interoperability:**
- The system shall operate under the control of localtransportation authority systems.

#### 3.3.4 Interface Specification

Various GUI elements like forms, images and standard buttons will be included in the User Interface.

## 4. Appendices

## 5. Index
