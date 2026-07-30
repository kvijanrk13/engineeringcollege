# Week 3 - Software Design Document

## 1. Architecture

The project follows Django’s Model–Template–View structure.

| Layer | Main elements |
|---|---|
| Presentation | Django templates, Tailwind CSS, documentation SVGs |
| Routing | Project, `library`, and `student` URL configurations |
| Application | Library and authentication views, fine utility functions |
| Domain | Author, Book, Student, Issue, Fine, and related models |
| Data | Django ORM with PostgreSQL |
| External | Cloudinary and Razorpay |

## 2. Main Modules

- **Student module:** signup, login, logout, Department and Student profiles.
- **Library module:** catalogue, search, requests, issues, returns, recommendations, and statistics.
- **Fine module:** overdue calculation, updates, waiver, order creation, and payment verification.
- **Documentation module:** renders weekly Markdown and UML diagrams.

## 3. Core Workflow

1. Student logs in and searches the catalogue.
2. Student requests a Book.
3. Librarian approves the Issue and sets a 15-day return date.
4. Librarian records the return.
5. The system creates an overdue Fine when required.
6. Student pays the Fine through Razorpay or Librarian waives it.

## 4. Security Design

- Django authentication and sessions.
- `login_required` and role checks on protected views.
- CSRF protection on POST forms.
- Razorpay signature verification before marking a Fine paid.
- Secrets supplied through environment variables.

## 5. Deployment Design

The browser connects over HTTPS to Gunicorn/Django on Render. Django uses PostgreSQL through
`DATABASE_URL`, Cloudinary for media URLs, and Razorpay for payments.

## 6. Design Result

The design separates presentation, business logic, persistence, and external integrations so that each
part can be maintained and tested independently.
