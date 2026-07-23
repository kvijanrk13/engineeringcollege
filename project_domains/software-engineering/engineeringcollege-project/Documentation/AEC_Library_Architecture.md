# System Architecture Document
## AEC Library Management System

### 1. System Overview

AEC Library is a standalone Django web application deployed on Render at `https://engineeringcollege.onrender.com/aeclibrary/`. It provides a complete library management solution including textbook/reference book cataloging, student authentication, book issue/return workflows, fine management with Razorpay payments, and an integrated Lorem Ipsum generator tool.

### 2. High-Level Architecture

The system follows Django's **Model-View-Template (MVT)** pattern and is organized as a standalone project with two core applications.

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Render Platform                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Gunicorn WSGI Server                       ││
│  │  ┌───────────────────────────────────────────────────┐  ││
│  │  │              Django AEC Library Project             │  ││
│  │  │  ┌──────────────┐            ┌───────────────┐    │  ││
│  │  │  │  Library App  │            │  Student App  │    │  ││
│  │  │  │  (Models,     │            │  (Auth,       │    │  ││
│  │  │  │   Views,      │            │   Signup)     │    │  ││
│  │  │  │   Templates)  │            │               │    │  ││
│  │  │  └──────────────┘            └───────────────┘    │  ││
│  │  │         │                           │              │  ││
│  │  │         └───────────┬───────────────┘              │  ││
│  │  │                     ▼                              │  ││
│  │  │              ┌──────────────┐                       │  ││
│  │  │              │  Core WSGI   │                       │  ││
│  │  │              │  Application │                       │  ││
│  │  │              └──────────────┘                       │  ││
│  │  └───────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Render PostgreSQL                        │
│                   (aeclibrary-db)                           │
└─────────────────────────────────────────────────────────────┘
```

### 3. Technology Stack

#### 3.1 Backend
- **Framework**: Django 3.1.7
- **Language**: Python 3.9.18
- **WSGI Server**: Gunicorn 20.1.0
- **Database**: PostgreSQL (via `dj-database-url` + `psycopg2-binary`)
- **ORM**: Django ORM with PostgreSQL backend

#### 3.2 Frontend
- **Templating**: Django Templates
- **Styling**: Tailwind CSS (via CDN/static files)
- **JavaScript**: Vanilla JS + jQuery fallback
- **Icons**: Font Awesome / inline SVG

#### 3.3 Static & Media
- **Static Files**: WhiteNoise 5.3.0 with `CompressStaticFilesStorage`
- **Media Files**: Local filesystem (`/media/`)
- **Image Processing**: Pillow 8.1.2
- **PDF Generation**: ReportLab + PyMuPDF (fitz)

#### 3.4 Third-Party Integrations
- **Payments**: Razorpay SDK 1.2.0
- **Legacy Payments**: Paytm Checksum (`paytmchecksum==1.7.0`)
- **Utilities**: Naked 0.1.31, shellescape 3.8.1
- **Cryptography**: pycryptodome 3.10.1

### 4. Application Structure

```
aeclibrary/
├── core/                          # Project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Root URL configuration
│   └── wsgi.py                    # WSGI entry point
├── library/                       # Library management module
│   ├── models.py                  # Book, Author, Issue, Fine
│   ├── views.py                   # Library business logic
│   ├── urls.py                    # Library routes
│   ├── utilities.py               # Helper functions
│   └── migrations/                # Database migrations
├── student/                       # Student authentication module
│   ├── models.py                  # Department, Student
│   ├── views.py                   # Login/signup/logout
│   ├── urls.py                    # Student routes
│   └── migrations/
├── templates/
│   ├── library/                   # Library HTML templates
│   └── student/                   # Student HTML templates
├── static/                        # CSS, JS, images
├── media/                         # Uploaded book covers, docs
├── databases/                     # Local SQLite fallback
├── Documentation/                 # Project docs
├── screenshots/                   # UI screenshots
├── UML Diagrams/                  # System design diagrams
├── Test Cases/                    # Unit/integration tests
├── requirements.txt
├── render.yaml                    # Render deployment config
├── manage.py
└── Procfile                       # Process declaration
```

### 5. Database Schema

#### 5.1 Library Models (`library/models.py`)

```sql
author
├── id (PK)
├── name (CharField 350)
└── description (TextField 450)

book
├── id (PK)
├── name (CharField 350)
├── author (FK → Author)
├── image (ImageField)
└── category (CharField 220)

issue
├── id (PK)
├── student (FK → Student)
├── book (FK → Book)
├── created_at (DateTime)
├── issued (Boolean)
├── issued_at (DateTime, nullable)
├── returned (Boolean)
└── return_date (DateTime, nullable)

fine
├── id (PK)
├── student (FK → Student)
├── issue (FK → Issue)
├── amount (Decimal)
├── paid (Boolean)
├── order_id (CharField, unique)
├── datetime_of_payment (DateTime, nullable)
├── razorpay_order_id (CharField)
├── razorpay_payment_id (CharField)
└── razorpay_signature (CharField)

library_stat
├── id (PK)
└── borrowed_books (PositiveInteger)
```

#### 5.2 Student Models (`student/models.py`)

```sql
department
├── id (PK)
└── name (CharField 200)

student
├── id (PK)
├── first_name (CharField 120)
├── last_name (CharField 120)
├── department (FK → Department)
└── student_id (OneToOne → User)
```

### 6. URL Routing

#### 6.1 Root URLs (`core/urls.py`)
```
/admin/                    → Django Admin
/student/                  → Student App URLs
/                          → Library App URLs
/media/<path>              → Media files
/static/<path>             → Static files
```

#### 6.2 Library URLs (`library/urls.py`)
```
/                          → allbooks (library home)
/search/                   → search books/authors
/sort/                     → sort books/authors
/addbook/                  → add new book (admin)
/deletebook/<bookID>/      → delete book (admin)
/request-book-issue/<bookID>/ → request book issue
/my-issues/                → student's issued books
/my-fines/                 → student's fines
/payfines/<fineID>/        → pay fine via Razorpay
/paystatus/<fineID>/       → payment status callback
/all-issues/               → all issue requests (admin)
/all-fines/                → all fines (admin)
/issuebook/<issueID>/      → approve issue (admin)
/returnbook/<issueID>/     → return book (admin)
/delete-fine/<fineID>/     → delete fine (admin)
```

#### 6.3 Student URLs (`student/urls.py`)
```
/signup/                   → student registration
/login/                    → student login
/logout/                   → student logout
```

### 7. Key Features & Workflows

#### 7.1 Book Catalog Management
- View all textbooks and reference books
- Search by book name or author
- Sort by book name or author
- Add/delete books (admin only)
- Book cover image upload via Pillow
- Category-based classification

#### 7.2 Issue & Return Workflow
```
Student Request → Admin Approval → Book Issued → Due Date Set
                                                    ↓
                                            Student Returns
                                                    ↓
                                            Fine Calculated
                                                    ↓
                                            Payment via Razorpay
```

#### 7.3 Fine Management & Payments
- Automatic fine calculation based on return date
- Razorpay order creation
- Payment signature verification
- Payment status callback handling

#### 7.4 Student Authentication
- Google OAuth / Username-Password signup/login
- Department-based student categorization
- Session-based authentication

#### 7.5 Lorem Ipsum Generator Tool
- Integrated utility for generating placeholder text
- Accessible within the library interface

### 8. Deployment Architecture

#### 8.1 Render Configuration
- **Service Type**: Web Service
- **Plan**: Free
- **Branch**: main
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `gunicorn core.wsgi:application`
- **Health Check**: `/`
- **Python Version**: 3.9.18

#### 8.2 Environment Variables
- `SECRET_KEY` - Django secret key (auto-generated on Render)
- `DEBUG` - Set to `False` in production
- `DATABASE_URL` - PostgreSQL connection string (from Render database)
- `RAZORPAY_KEY_ID` - Razorpay public key
- `RAZORPAY_KEY_SECRET` - Razorpay secret key

#### 8.3 Database Provisioning
- **Provider**: Render PostgreSQL
- **Database Name**: aeclibrary
- **Plan**: Free tier
- **Connection**: SSL-enabled via `dj-database-url`

### 9. Security Considerations

#### 9.1 Authentication & Authorization
- `@login_required` decorator for protected views
- `@user_passes_test` for admin-only operations
- Django's built-in session management
- Password validation (min length, numeric, common password)

#### 9.2 Payment Security
- Razorpay signature verification
- Secure order creation with HMAC
- Webhook validation for payment callbacks

#### 9.3 Static File Security
- WhiteNoise for secure static file serving
- Compressed static files for performance
- No direct access to source files

### 10. Third-Party Dependencies Analysis

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 3.1.7 | Web framework |
| gunicorn | 20.1.0 | WSGI HTTP Server |
| whitenoise | 5.3.0 | Static file serving |
| psycopg2-binary | 2.9.9 | PostgreSQL adapter |
| dj-database-url | 0.5.0 | Database URL parsing |
| razorpay | 1.2.0 | Payment gateway |
| Pillow | 8.1.2 | Image processing |
| pycryptodome | 3.10.1 | Cryptographic operations |
| django-environ | 0.4.5 | Environment variable management |
| Naked | 0.1.31 | Shell utility |
| paytmchecksum | 1.7.0 | Paytm payment checksum (legacy) |

### 11. Database Tables - Detailed Schema

#### Week 3: Database Design & Data Tables

| Table Name | Field Name | Data Type | Constraints | Description |
|------------|------------|-----------|-------------|-------------|
| **author** | id | BigInt | PRIMARY KEY, Auto Increment | Unique identifier for author |
| | name | Varchar(350) | NOT NULL | Author full name |
| | description | Varchar(450) | NOT NULL | Author biography/details |
| **book** | id | BigInt | PRIMARY KEY, Auto Increment | Unique identifier for book |
| | name | Varchar(350) | NOT NULL | Book title |
| | author_id | BigInt | FOREIGN KEY → author(id), CASCADE | Reference to author |
| | image | Varchar(100) | NOT NULL | Book cover image path |
| | category | Varchar(220) | NOT NULL | Textbook / Reference |
| **issue** | id | BigInt | PRIMARY KEY, Auto Increment | Unique identifier for issue |
| | student_id | BigInt | FOREIGN KEY → student(id), CASCADE | Student who requested book |
| | book_id | BigInt | FOREIGN KEY → book(id), CASCADE | Book being issued |
| | created_at | DateTime | NOT NULL, auto_now=True | Request timestamp |
| | issued | Boolean | DEFAULT=False | Issue approval status |
| | issued_at | DateTime | NULL, blank=True | Approval timestamp |
| | returned | Boolean | DEFAULT=False | Return status |
| | return_date | DateTime | NULL, blank=True | Due date for return |
| **fine** | id | BigInt | PRIMARY KEY, Auto Increment | Unique identifier for fine |
| | student_id | BigInt | FOREIGN KEY → student(id), CASCADE | Student who paid fine |
| | issue_id | BigInt | FOREIGN KEY → issue(id), CASCADE | Related issue record |
| | amount | Decimal(10,2) | DEFAULT=0.00 | Fine amount in INR |
| | paid | Boolean | DEFAULT=False | Payment status |
| | order_id | Varchar(500) | UNIQUE, NULL, blank=True | Razorpay order ID |
| | datetime_of_payment | DateTime | NULL, blank=True | Payment timestamp |
| | razorpay_order_id | Varchar(500) | NULL, blank=True | Razorpay order reference |
| | razorpay_payment_id | Varchar(500) | NULL, blank=True | Razorpay payment ID |
| | razorpay_signature | Varchar(500) | NULL, blank=True | Payment verification signature |
| **library_stat** | id | BigInt | PRIMARY KEY, Auto Increment | Unique identifier |
| | borrowed_books | PositiveInteger | DEFAULT=0 | Total books currently borrowed |
| **department** | id | BigInt | PRIMARY KEY, Auto Increment | Unique identifier for department |
| | name | Varchar(200) | NOT NULL | Department name |
| **student** | id | BigInt | PRIMARY KEY, Auto Increment | Unique identifier for student |
| | first_name | Varchar(120) | NOT NULL | Student first name |
| | last_name | Varchar(120) | NOT NULL | Student last name |
| | department_id | BigInt | FOREIGN KEY → department(id), CASCADE | Student department |
| | student_id | BigInt | ONE TO ONE → auth_user(id), CASCADE | Linked Django user account |
| **auth_user** (Django) | id | BigInt | PRIMARY KEY, Auto Increment | User unique ID |
| | username | Varchar(150) | UNIQUE, NOT NULL | Login username |
| | password | Varchar(128) | NOT NULL | Hashed password |
| | email | Varchar(254) | NOT NULL | Email address |
| | is_active | Boolean | DEFAULT=True | Account status |
| | is_staff | Boolean | DEFAULT=False | Admin access flag |
| | is_superuser | Boolean | DEFAULT=False | Superuser flag |
| | last_login | DateTime | NULL | Last login timestamp |
| | date_joined | DateTime | NOT NULL | Account creation timestamp |

### 12. Architecture Diagram - MVC Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         Request                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  URL Router (core/urls.py)                                  │
│  - Routes to library/ or student/ app                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  View Layer                                                 │
│  ┌──────────────┐               ┌──────────────────────┐   │
│  │ Library      │               │ Student              │   │
│  │ Views        │               │ Views                │   │
│  │ - allbooks   │               │ - login              │   │
│  │ - search     │               │ - signup             │   │
│  │ - sort       │               │ - logout             │   │
│  │ - addbook    │               └──────────────────────┘   │
│  │ - issuerequest│                                        │
│  │ - myissues    │                                        │
│  │ - payfine     │                                        │
│  └──────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Template Layer                                             │
│  ┌──────────────┐               ┌──────────────────────┐   │
│  │ Library      │               │ Student              │   │
│  │ Templates    │               │ Templates            │   │
│  │ - home.html  │               │ - login.html         │   │
│  │ - ...        │               │ - signup.html        │   │
│  └──────────────┘               └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Model Layer                                                │
│  ┌────────────────┐           ┌────────────────────┐      │
│  │ Book           │           │ Student            │      │
│  │ Author         │           │ Department         │      │
│  │ Issue          │           └────────────────────┘      │
│  │ Fine           │                                         │
│  │ LibraryStat    │                                         │
│  └────────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL on Render)                            │
│  Tables: author, book, issue, fine, library_stat,           │
│          department, student, auth_user                     │
└─────────────────────────────────────────────────────────────┘
```

### 13. File Storage Architecture

```
Media Files (Local Filesystem)
├── book_covers/              # Book cover images
│   ├── <Book ID>_<slug>.png
│   └── ...
├── student_photos/           # Student profile photos
└── ...

Static Files (WhiteNoise)
├── CSS/                      # Stylesheets
├── JS/                       # JavaScript files
└── images/                   # UI assets, icons
```

### 14. Data Flow - Book Issue Process

```
1. Student logs in via /student/login/
   ├── Session created
   └── Redirected to library home

2. Student browses books at /
   ├── allbooks() fetches all Book objects
   ├── getmybooks() determines user's issued/requested books
   └── Renders library/home.html

3. Student requests a book
   └── POST to /request-book-issue/<bookID>/
       ├── Issue record created (issued=False)
       └── Admin notified

4. Admin approves issue
   └── POST to /issuebook/<issueID>/
       ├── issue.issued = True
       ├── issue.issued_at = now()
       ├── issue.return_date = now() + 15 days
       └── LibraryStat updated

5. Student returns book
   └── POST to /returnbook/<issueID>/
       ├── issue.returned = True
       ├── Fine calculated via calcFine()
       └── Fine record created if overdue

6. Student pays fine
   └── POST to /payfines/<fineID>/
       ├── Razorpay order created
       ├── Payment signature verified
       └── Fine.marked as paid
```

### 15. Testing Architecture

#### 15.1 Test Coverage Areas
- Model validation (Book, Author, Issue, Fine)
- View function responses
- URL routing correctness
- Payment callback verification
- Fine calculation logic
- Authentication flow
- Search and sort functionality

#### 15.2 Test Cases Location
```
Test Cases/
├── Test Cases Index.md
├── unit_tests/               # Model and utility tests
├── integration_tests/        # End-to-end workflow tests
└── payment_tests/            # Razorpay callback tests
```

### 16. Scalability & Future Enhancements

1. **API Layer**: Convert to REST API using Django REST Framework
2. **Caching**: Redis for session and frequent queries
3. **Search**: Elasticsearch/Algolia for advanced book search
4. **Notifications**: Email/SMS alerts for due dates
5. **Barcode Integration**: Scan ISBN for book entry
6. **Analytics**: Borrowing trends dashboard
7. **Multi-branch**: Support multiple library branches

---

*Document Version: 1.0*
*Project: AEC Library Management System*
*Live URL: https://engineeringcollege.onrender.com/aeclibrary/*
*Last Updated: 2026-07-23*
