WEEK–3

SOFTWARE DESIGN DOCUMENT (SDD)

1. SYSTEM ARCHITECTURE

Figure 3.1: System Architecture of Engineering College Library Management System

Figure 3.1 illustrates the layered architecture of the Anurag Engineering College Library Management System. The architecture follows a modular and scalable design in which users interact with the system through secure authentication. The application is developed using the Django MVC framework, while PostgreSQL stores application data and Cloudinary stores book cover images. The entire application is deployed on the Render cloud platform.

![System Architecture](/static/docs/images/sdd_image6.jpeg)

1.1 Architecture Overview

The Engineering College Library Management System follows a layered architecture consisting of six logical layers. Each layer performs a specific responsibility and communicates only with the adjacent layer. This separation improves modularity, maintainability, scalability, and security.

The layers are:

Users Layer

Authentication Layer

Application Layer

Modules Layer

Data Layer

Deployment Layer

This layered approach ensures that modifications in one layer have minimal impact on the remaining layers.

2. USERS LAYER

The Users Layer represents the primary users interacting with the application. The system defines three categories of users.

2.1 Student

Students are the primary users of the system.

The student module provides facilities to

Search books using title, author, ISBN, publisher, or category.

View complete book information.

Check real-time book availability.

Borrow books.

Renew issued books before the due date.

Return borrowed books.

View borrowing history.

View overdue fine details.

Update personal profile.

Responsibilities

Authenticate using Gmail.

Search available books.

Borrow books according to library rules.

Return books before the due date.

Maintain profile information.

2.2 Librarian

The Librarian manages day-to-day library operations.

The librarian is responsible for

Adding new books.

Updating book information.

Removing obsolete books.

Issuing books.

Receiving returned books.

Managing student accounts.

Calculating overdue fines.

Generating reports.

Responsibilities

Maintain accurate inventory.

Verify issued books.

Update stock.

Monitor overdue books.

Prepare daily and monthly reports.

2.3 Administrator

The Administrator supervises the complete application.

The administrator can

Manage librarians.

Manage departments.

Manage categories.

Manage publishers.

Configure application settings.

Monitor dashboard.

Perform database backup.

Generate statistical reports.

Responsibilities

Manage users.

Configure security.

Monitor application performance.

Perform backup and recovery.

3. AUTHENTICATION LAYER

The Authentication Layer provides secure access to the application.

The Engineering College Library Management System uses Google Gmail Authentication (OAuth 2.0) for user verification.

Functions

Secure Login

Secure Logout

Session Management

Identity Verification

Role-Based Access Control

Advantages

Eliminates password management.

Improves security.

Prevents unauthorized access.

Supports institutional Gmail accounts.

4. APPLICATION LAYER

The application layer contains the complete business logic of the system.

The project is developed using the Django MVC Architecture.

The application layer contains

URL Routing

Templates

Views

Models

Business Logic

Services

URL Routing

Receives HTTP requests and forwards them to the corresponding Django Views.

Views

Processes user requests and communicates with the database.

Models

Represent database tables and business entities.

Templates

Generate responsive HTML pages using Bootstrap.

Services

Perform

Fine calculation

Report generation

Validation

Notifications

5. MODULES LAYER

The Modules Layer is divided into six major modules.

5.1 Book Management Module

This module manages all library books.

Functions include

Add Books

Edit Books

Delete Books

Search Books

View Availability

Update Stock

5.2 Student Management Module

This module maintains student information.

Functions

Register Students

Update Student Profile

Search Students

View Student History

Manage Student Status

5.3 Issue / Return Management

Responsible for circulation management.

Functions

Issue Books

Return Books

Renew Books

Update Due Date

Update Stock

5.4 Fine Management

Automatically calculates overdue penalties.

Functions

Calculate Fine

View Fine

Fine Collection

Payment History

5.5 Reports & Dashboard

Provides analytical reports.

Reports include

Available Books Report

Issue Report

Return Report

Fine Report

Student Activity Report

Dashboard Statistics

5.6 Notifications

Provides system notifications.

Notifications include

Due Date Reminder

Fine Reminder

Book Availability Alerts

System Announcements

6. DATA LAYER

The Data Layer stores all application information.

PostgreSQL Database

Stores

Student Details

Book Details

Librarian Details

Issue Records

Return Records

Fine Details

Categories

Departments

Publishers

Advantages

ACID Compliance

High Reliability

Multi-user Support

Fast Query Processing

Cloudinary

Cloudinary stores

Book Cover Images

Advantages

Cloud Storage

Fast Image Delivery

Automatic Image Optimization

Secure Access

7. DEPLOYMENT LAYER

The application is deployed using Render Cloud Platform.

Render provides

Application Hosting

SSL Security

Static File Hosting

Automatic Deployment

Auto Scaling

Backup Support

Advantages

High Availability

Secure HTTPS Access

Continuous Deployment

Low Maintenance

8. DESIGN GOALS

The proposed architecture is designed to achieve

High Security

Scalability

Reliability

Performance

Modular Development

Easy Maintenance

Cloud Deployment

User-Friendly Interface

9. ADVANTAGES OF THE PROPOSED ARCHITECTURE

Layered Architecture

Modular Design

Secure Gmail Authentication

Cloud-Based Deployment

Automatic Fine Calculation

Easy Report Generation

Centralized Database

Better Performance

Easier Maintenance

High Scalability

10. Data Tables

Table 1: Student Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Student_ID | Integer | Primary Key | Unique identification number |
| 2 | Roll_Number | Varchar | 20 | College Roll Number |
| 3 | Student_Name | Varchar | 100 | Name of Student |
| 4 | Email | Varchar | 100 | College Gmail Address |
| 5 | Department | Varchar | 50 | Department Name |
| 6 | Semester | Integer | 2 | Current Semester |
| 7 | Phone_Number | Varchar | 15 | Contact Number |
| 8 | Status | Boolean | - | Active / Inactive |

Table 2: Librarian Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Librarian_ID | Integer | Primary Key | Unique Librarian ID |
| 2 | Librarian_Name | Varchar | 100 | Name of Librarian |
| 3 | Email | Varchar | 100 | Official Email |
| 4 | Phone | Varchar | 15 | Mobile Number |
| 5 | Username | Varchar | 50 | Login Username |
| 6 | Password | Varchar | 255 | Encrypted Password |

Table 3: Administrator Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Admin_ID | Integer | Primary Key | Administrator ID |
| 2 | Admin_Name | Varchar | 100 | Administrator Name |
| 3 | Email | Varchar | 100 | Official Email |
| 4 | Username | Varchar | 50 | Login Username |
| 5 | Password | Varchar | 255 | Encrypted Password |

Table 4: Book Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Book_ID | Integer | Primary Key | Unique Book ID |
| 2 | ISBN | Varchar | 20 | International Standard Book Number |
| 3 | Book_Title | Varchar | 200 | Title of Book |
| 4 | Author | Varchar | 150 | Author Name |
| 5 | Publisher | Varchar | 100 | Publisher Name |
| 6 | Category | Varchar | 50 | Book Category |
| 7 | Department | Varchar | 50 | Department |
| 8 | Edition | Varchar | 20 | Edition |
| 9 | Price | Decimal | 10,2 | Book Cost |
| 10 | Rack_Number | Varchar | 20 | Rack Location |
| 11 | Quantity | Integer | - | Total Copies |
| 12 | Available_Copies | Integer | - | Available Books |
| 13 | Book_Cover | Varchar | 255 | Cloudinary Image URL |

Table 5: Issue Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Issue_ID | Integer | Primary Key | Issue Transaction ID |
| 2 | Student_ID | Integer | Foreign Key | Borrowing Student |
| 3 | Book_ID | Integer | Foreign Key | Issued Book |
| 4 | Issue_Date | Date | 10 | Book Issue Date |
| 5 | Due_Date | Date | 10 | Expected Return Date |
| 6 | Return_Date | Date | 10 | Actual Return Date |
| 7 | Status | Varchar | 20 | Issued / Returned |

Table 6: Fine Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Fine_ID | Integer | Primary Key | Fine ID |
| 2 | Issue_ID | Integer | Foreign Key | Book Issue Record |
| 3 | Fine_Amount | Decimal | 10,2 | Fine Amount |
| 4 | Fine_Status | Varchar | 20 | Paid / Unpaid |
| 5 | Payment_Date | Date | 10 | Date of Payment |

Table 7: Category Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Category_ID | Integer | Primary Key | Category ID |
| 2 | Category_Name | Varchar | 100 | Category Name |
| 3 | Description | Text | - | Category Description |

Table 8: Department Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Department_ID | Integer | Primary Key | Department ID |
| 2 | Department_Name | Varchar | 100 | Department Name |
| 3 | HOD_Name | Varchar | 100 | Head of Department |

Table 9: Publisher Table

| S.No | Column Name | Data Type | Length | Description |
|------|-------------|-----------|--------|-------------|
| 1 | Publisher_ID | Integer | Primary Key | Publisher ID |
| 2 | Publisher_Name | Varchar | 100 | Publisher Name |
| 3 | Address | Text | - | Publisher Address |
| 4 | Phone_Number | Varchar | 15 | Contact Number |

11. CONCLUSION

The proposed layered architecture provides a secure, modular, scalable, and maintainable design for the Engineering College Library Management System. By separating user interaction, authentication, application logic, functional modules, data storage, and deployment into independent layers, the system becomes easier to develop, test, maintain, and extend. This architecture is well suited for modern engineering college libraries and aligns with best practices in software engineering.