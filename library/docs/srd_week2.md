# Week 2 - Software Requirements Document

## 1. Purpose and Scope

The AEC Library system manages authentication, catalogue browsing, book circulation, overdue fines,
online payments, and librarian administration at `/aeclibrary/`.

## 2. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Students and librarians shall authenticate securely. |
| FR-02 | Librarians shall add and delete catalogue books. |
| FR-03 | Users shall search books by title, author, or category. |
| FR-04 | Students shall request available books. |
| FR-05 | Librarians shall approve issues and assign a 15-day return date. |
| FR-06 | Librarians shall record returns. |
| FR-07 | The system shall calculate overdue fines at ₹10 per day. |
| FR-08 | Students shall view and pay fines through Razorpay. |
| FR-09 | Librarians shall update, waive, or delete fines. |
| FR-10 | The system shall maintain issue and borrowed-book statistics. |

## 3. Non-Functional Requirements

- **Security:** role-based authorization, CSRF protection, protected payment verification.
- **Usability:** responsive pages, clear messages, searchable tables.
- **Reliability:** database constraints, migrations, and deterministic automated tests.
- **Performance:** indexed ORM queries and externally hosted media.
- **Availability:** deployed through Render using PostgreSQL.

## 4. Main Data

`Author`, `Book`, `Department`, `Student`, `Issue`, `Fine`, `LibraryStat`, and `BookRecommendation`.

## 5. External Interfaces

| Interface | Purpose |
|---|---|
| PostgreSQL | Persistent application data |
| Cloudinary | Book and recommendation images |
| Razorpay | Fine order creation and payment verification |
| Browser | Student and librarian user interface |

## 6. Acceptance

The system is acceptable when authorized users can complete the request–issue–return–fine workflow,
invalid access is rejected, payments are verified, and all critical automated tests pass.
