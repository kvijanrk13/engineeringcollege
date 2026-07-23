2. SOFTWARE REQUIREMENTS DOCUMENT (SRD)

1. Introduction

1.1 Purpose

The purpose of this document is to specify the software requirements for the Anurag Engineering College Library Management System (AECLMS). The application is developed to automate library operations such as maintaining book records, member registration, book issue, return, renewal, fine calculation, and report generation. The system provides a secure, user-friendly, and web-based platform that minimizes manual work and improves the efficiency of library management.

This document defines all functional and non-functional requirements, system constraints, assumptions, interfaces, and operational characteristics that will guide the development, testing, deployment, and maintenance of the system.

1.2 Scope

The Engineering College Library Management System is a cloud-based web application developed using the Django framework.

The system provides the following facilities.

For Students

Login using Google Gmail Authentication

Search books by Title

Search books by Author

Search books by ISBN

Search books by Category

View Book Availability

Borrow Books

Return Books

Renew Books

View Borrowing History

View Fine Details

Update Profile

For Librarians

Secure Login

Add New Books

Update Book Details

Delete Books

Manage Student Records

Issue Books

Return Books

Renew Books

Calculate Fine Automatically

Search Books

Generate Reports

For Administrator

Manage Librarians

Manage Departments

Manage Book Categories

Manage Publishers

Dashboard Monitoring

User Management

Database Backup

System Configuration

1.3 Definitions, Acronyms and Abbreviations

1.4 References

IEEE 830 Software Requirements Specification Standard

Roger S. Pressman – Software Engineering

Ian Sommerville – Software Engineering

Django Official Documentation

PostgreSQL Documentation

Google OAuth Documentation

Bootstrap Documentation

1.5 Overview

The Engineering College Library Management System consists of three major users.

Student

Librarian

Administrator

The application follows a client-server architecture and provides secure authentication, centralized book management, automatic fine calculation, report generation, and cloud deployment.

2. Project Description

2.1 Product Perspective

The existing library management process is mostly manual, involving registers and paper-based records. Such a system requires considerable effort to search books, maintain issue and return records, calculate overdue fines, and prepare reports. These manual activities often result in delays, inaccurate records, and increased administrative workload.

The proposed Engineering College Library Management System overcomes these limitations by providing a centralized, web-based platform. It enables students, librarians, and administrators to access library services securely from anywhere using a web browser. The application stores all information in a PostgreSQL database, supports Gmail authentication, and provides automated book issue, return, renewal, fine calculation, and report generation.

The proposed system offers the following advantages:

Reduces paperwork and manual record maintenance.

Provides quick and accurate book search.

Automates issue, return, and renewal processes.

Calculates overdue fines automatically.

Improves data security through authenticated access.

Generates reports instantly.

Supports cloud-based access and centralized database management.

2.2 Product Functions

The system provides the following major functions.

Student

Secure Login

Search Books

View Book Details

Borrow Books

Return Books

Renew Books

View Fine Details

View Borrowing History

Librarian

Add Books

Update Books

Delete Books

Issue Books

Return Books

Renew Books

Manage Students

Fine Calculation

Generate Reports

Administrator

Manage Librarians

Manage Departments

Manage Categories

Manage Publishers

Manage Users

Monitor Dashboard

Backup Database

2.3 User Characteristics

Administrator

The Administrator has complete control over the application. The administrator manages users, departments, categories, publishers, librarians, and monitors the overall performance of the system through the administrative dashboard.

Librarian

The Librarian performs day-to-day library operations. The librarian maintains book records, issues and returns books, manages student accounts, calculates fines, and generates reports. The librarian should possess basic computer knowledge and be familiar with library procedures.

Student

Students are end users of the system. They use the application to search books, check availability, borrow, renew, and return books, and view their borrowing history and fine details. Students require only basic computer and web browsing skills.

2.4 General Constraints

Internet connectivity is mandatory.

Users must possess valid login credentials.

Students must authenticate using their institutional Gmail account.

PostgreSQL database server should remain operational.

Only authorized librarians can issue and return books.

Books cannot be issued when no copies are available.

The system should support access through standard web browsers.

2.5 Assumptions and Dependencies

Assumptions

The application will be deployed on the Render cloud platform.

Google OAuth services are available for authentication.

Users have reliable Internet access.

Book information entered by librarians is accurate.

Dependencies

Django Framework

PostgreSQL Database

Google OAuth Authentication

Cloudinary (Book Cover Images)

Render Cloud Hosting

3. Specific Requirements

3.1 Functional Requirements

The system shall provide the following functions:

Google Authentication

Student Registration

Book Management

Category Management

Publisher Management

Search Books by Title

Search Books by Author

Search Books by ISBN

Search Books by Category

Book Issue

Book Return

Book Renewal

Fine Calculation

Student Management

Librarian Management

Report Generation

Dashboard Analytics

Database Backup

User Profile Management

Role-Based Access Control

3.2 Non-Functional Requirements

3.2.1 Product Requirements

Usability

The application shall provide a simple and responsive user interface. New users should be able to operate the system after minimal training.

Performance

The system shall respond to user requests within three seconds under normal operating conditions.

Reliability

The system shall achieve at least 99% availability and maintain data consistency during concurrent transactions.

Portability

The application shall run on Windows, Linux, macOS, Android, and iOS through standard web browsers without modification.

Scalability

The system shall support over 5,000 registered students and 100,000 book records while maintaining acceptable performance.

Availability

The application shall be accessible 24×7, except during scheduled maintenance.

Maintainability

The software shall follow a modular Django architecture, enabling future enhancements and easier maintenance.

3.2.2 Organizational Requirements

Developed using Python and Django Framework

PostgreSQL Database

HTML5

CSS3

Bootstrap 5

JavaScript

Git Version Control

Cloudinary for Book Cover Images

Hosted on Render Cloud

3.2.3 External Requirements

Security

Google OAuth Authentication

Role-Based Access Control

HTTPS Communication

Secure Password Management

Interoperability

The application shall integrate with Google Authentication services, Cloudinary for image storage, PostgreSQL database services, and cloud hosting infrastructure.

3.3 Interface Specification

User Interface

Login Page

Student Dashboard

Librarian Dashboard

Administrator Dashboard

Book Search Page

Book Details Page

Issue/Return Page

Reports Page

Hardware Interface

Desktop Computer

Laptop

Tablet

Smartphone

Software Interface

Django Framework

PostgreSQL

Google OAuth

Cloudinary

Render Cloud

Communication Interface

HTTPS Protocol

Secure Database Connectivity

Cloud-Based Deployment

4. Appendices

Hardware Requirements

Intel Core i3 Processor or above

4 GB RAM (Minimum)

20 GB Free Disk Space

Internet Connection

Software Requirements

Windows 10/11 or Linux

Python 3.12+

Django 5.x

PostgreSQL 16+

HTML5

CSS3

Bootstrap 5

JavaScript

Git

Visual Studio Code / PyCharm

Cloudinary

Render Cloud

5. Index

A: Administrator, Authentication, Availability
B: Book, Borrow, Bootstrap
C: Category, Cloudinary, CRUD
D: Dashboard, Database, Django
F: Fine, Functional Requirements
G: Gmail Authentication, GUI
L: Librarian, Library Management System
N: Non-Functional Requirements
P: Performance, PostgreSQL, Publisher, Purpose
R: Reports, Reliability, Renewal
S: Scope, Security, Student, Search
U: User Interface, Usability