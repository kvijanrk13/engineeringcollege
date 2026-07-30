# Week 6 - Unit Testing and Integration Testing

## 1. Objective

Design and execute repeatable test cases for the AEC Library Management System. Unit tests isolate models,
utility functions, and small view helpers. Integration tests exercise connected Django components through the
test client, ORM, authentication, templates, messages, signals, and mocked external services.

## 2. Test Scope

| Area | Included |
|---|---|
| Authentication | Student signup, login, logout, role restrictions |
| Catalogue | Authors, books, search, sorting, recommendations |
| Circulation | Issue request, approval, return, reset, issue history |
| Fines | Fine calculation, update, waiver, payment success/failure |
| Persistence | Foreign keys, one-to-one profile, post-save signal |
| External boundaries | Razorpay mocked at the application boundary |
| Documentation | Week content loads and renders |

Cloudinary and Razorpay live networks must not be called from automated tests. Their clients and returned
payloads are mocked so the suite remains deterministic.

## 3. Test Environment and Data

Use Django `TestCase`, `Client`, `RequestFactory`, `unittest.mock.patch`, and `override_settings`.
Each test runs in an isolated transaction-backed test database.

| Test fixture | Value |
|---|---|
| Department | `CSE(AI&ML)` |
| Student user | username `23CSE001`, password `Test@12345` |
| Admin user | username `librarian`, `is_superuser=True` |
| Author | `Robert C. Martin` |
| Book | `Clean Code`, category `TEXT` |
| Issue due date | Future date for no-fine tests; 3 days past for fine tests |
| Fine rate | ₹10 per overdue day |
| Razorpay order | `order_test_001` |
| Razorpay payment | `pay_test_001` |

## 4. Unit Test Cases

### 4.1 Model and Utility Tests

| ID | Unit under test | Preconditions / input | Test steps | Expected result |
|---|---|---|---|---|
| UT-01 | `Author.__str__` | Author name is `Robert C. Martin` | Create Author; call `str(author)` | Returns `Robert C. Martin` |
| UT-02 | `Book.__str__` | Book name is `Clean Code` | Create Book; call `str(book)` | Returns `Clean Code` |
| UT-03 | `Book.cloudinary_image_url` | Cloud name configured; image name saved | Override Cloudinary setting; access property | URL contains cloud name and image path |
| UT-04 | `Book.cloudinary_image_url` empty case | Book has no usable image name | Access property | Returns an empty string |
| UT-05 | `Student.__str__` | Username `23CSE001`, department exists | Create Student; call `str(student)` | Contains first name, last four username characters, and department |
| UT-06 | `Fine.save` order generation | `order_id=None`; Student and Issue exist | Save Fine | A non-empty unique order ID is generated |
| UT-07 | `Fine.save` preserves order | Existing `order_id=ORDER-1` | Modify amount; save again | `order_id` remains `ORDER-1` |
| UT-08 | `Issue.days_no` future due date | Issued issue due in 5 days | Freeze/patch current time; call `days_no()` | Returns text containing `left` |
| UT-09 | `Issue.days_no` overdue | Issued issue due 3 days ago | Call `days_no()` | Returns text containing `passed` |
| UT-10 | `calcFine` before due date | Issued, not returned, future due date | Call `calcFine(issue)` | Returns `no fine`; no Fine is created |
| UT-11 | `calcFine` overdue | Issued, not returned, due 3 days ago | Call utility; refresh Fine | Fine exists with amount `30.00` |
| UT-12 | `calcFine` paid fine | Existing paid Fine | Call utility after additional overdue time | Paid Fine amount is not recalculated |
| UT-13 | `calcFine` returned issue | `returned=True` | Call utility | Returns `no fine`; no new Fine is created |
| UT-14 | `getmybooks` anonymous user | `AnonymousUser` | Call `getmybooks(user)` | Returns two empty lists |
| UT-15 | `getmybooks` requested book | Student has unissued Issue | Call utility | Book appears only in requested list |
| UT-16 | `getmybooks` issued book | Student has `issued=True` Issue | Call utility | Book appears only in issued list |
| UT-17 | Issue post-save signal | One active issued Issue | Save Issue; load `LibraryStat(id=1)` | `borrowed_books` equals active issued/not-returned count |
| UT-18 | `BookRecommendation.__str__` | Recommendation title is set | Call `str(recommendation)` | Returns title |
| UT-19 | Recommendation fallback | Recommendation title is blank | Call `str(recommendation)` | Returns `Book Recommendation` |
| UT-20 | `google_signin_enabled` | Both OAuth settings present/absent | Run helper under overridden settings | True only when both values are non-empty |

### 4.2 Unit-Test Acceptance Criteria

1. Each test contains one principal behavioral assertion.
2. Tests do not depend on execution order.
3. Time-sensitive tests patch or freeze `timezone.now()`.
4. External services are mocked.
5. Tests pass individually and as a complete suite.

## 5. Integration Test Cases

### 5.1 Authentication and Authorization

| ID | Integrated components | Preconditions | Steps | Expected result |
|---|---|---|---|---|
| IT-01 | Signup view + User + Student + Department | Department exists | POST valid signup form | User and Student created, session authenticated, redirect to library home |
| IT-02 | Signup duplicate handling | Username already exists | POST same student ID | No duplicate User; message shown; redirect to login/signup flow |
| IT-03 | Login view + auth backend + session | Student user exists | POST valid credentials | Session contains authenticated user; redirect to library home |
| IT-04 | Invalid login | Student user exists | POST wrong password | User remains anonymous; invalid-credentials message displayed |
| IT-05 | Protected home | Anonymous client | GET `/aeclibrary/` | Redirect to student signup/login |
| IT-06 | Student blocked from admin operation | Authenticated student | GET add-book or all-issues URL | Redirect/denial according to role decorator |
| IT-07 | Admin blocked from student issue request | Authenticated superuser | Request a book | Redirect/denial; no student Issue created |

### 5.2 Catalogue and Search

| ID | Integrated components | Preconditions | Steps | Expected result |
|---|---|---|---|---|
| IT-08 | Home view + ORM + template | Books and recommendations exist | Login; GET library home | HTTP 200; text/reference groups and totals are in context |
| IT-09 | Search view + query + template | Book `Clean Code` exists | GET search with `clean` | Result contains `Clean Code` |
| IT-10 | Search by category | `TEXT` category book exists | Search for `text` | Matching book returned |
| IT-11 | Empty search validation | Logged-in user | Submit whitespace query | Warning message and redirect to home |
| IT-12 | Admin add book | Admin, Author, uploaded test image | POST add-book form | Book persisted with selected Author and success message |
| IT-13 | Admin delete book cascade | Book has Issue records | Request delete-book | Book removed; dependent Issue records removed by cascade |

### 5.3 Issue and Return Workflow

| ID | Integrated components | Preconditions | Steps | Expected result |
|---|---|---|---|---|
| IT-14 | Issue request + Student + Book + signal | Logged-in student and Book | GET request-book-issue URL | One unissued Issue created; duplicate request does not create another |
| IT-15 | Admin issue approval | Pending Issue; admin logged in | GET issuebook URL | `issued=True`; `issued_at` set; return date approximately 15 days later |
| IT-16 | Duplicate issue approval | Issue already issued | Call issuebook again | Error message; dates/state are not incorrectly reset |
| IT-17 | Student issue history filter | Student has issued and pending records | GET `my-issues/?issued=1` | Context contains only issued records |
| IT-18 | Return before due date | Issued Issue due in future | Admin calls returnbook | `returned=True`; no Fine created |
| IT-19 | Overdue return | Issued Issue due 3 days ago | Admin calls returnbook | `returned=True`; Fine created with amount ₹30 |
| IT-20 | Clear pending issues | Mix of pending and issued Issues | Admin POSTs clear-issues | Pending Issues deleted; issued records retained; statistic recalculated |
| IT-21 | Reset circulation | Active issued Issues and nonzero statistic | POST reset-issued | Statistic becomes zero; active records marked returned/reset |

### 5.4 Fine and Payment Workflow

| ID | Integrated components | Preconditions | Steps | Expected result |
|---|---|---|---|---|
| IT-22 | My fines + calculation utility | Student has overdue Issue | GET my-fines | Fine is calculated and displayed |
| IT-23 | Admin update fine | Fine exists | POST numeric amount | Amount updated and success message shown |
| IT-24 | Invalid fine amount | Fine exists | POST nonnumeric amount | Amount unchanged; validation message shown |
| IT-25 | Waive fine | Unpaid Fine exists | Admin calls waive-fine | Amount becomes zero and `paid=True` |
| IT-26 | Payment order creation | Unpaid Fine; mocked Razorpay client | GET payfines URL | Mock called with paise amount, INR, receipt; payment template rendered |
| IT-27 | Payment verification success | Mock verifier returns success (`None`) | POST payment IDs/signature | Fine becomes paid; IDs, signature, and payment datetime saved |
| IT-28 | Payment verification failure | Mock verifier raises exception | POST payment callback | Fine remains unpaid; failure message shown |

### 5.5 Documentation and Data Integrity

| ID | Integrated components | Preconditions | Steps | Expected result |
|---|---|---|---|---|
| IT-29 | Documentation view + Markdown + template | Week files exist | GET documentation URL | HTTP 200; Week 1 through Week 6 headings rendered |
| IT-30 | Department cascade | Department has Student and related Issues/Fines | Delete Department | Student and dependent records follow configured cascade behavior |
| IT-31 | User one-to-one constraint | Student profile already exists for User | Attempt second Student for same User | Database raises `IntegrityError` |
| IT-32 | Fine unique order ID | Fine with order ID exists | Create second Fine with same ID | Database raises `IntegrityError` |

## 6. Requirement-to-Test Traceability

| Requirement | Covered by |
|---|---|
| Student registration and login | IT-01 to IT-05 |
| Role-based access | IT-06, IT-07 |
| Catalogue management | IT-08 to IT-13 |
| Issue and return processing | IT-14 to IT-21 |
| Fine calculation and administration | UT-10 to UT-13, IT-18, IT-19, IT-22 to IT-25 |
| Online fine payment | IT-26 to IT-28 |
| Model integrity and signals | UT-06, UT-07, UT-17, IT-30 to IT-32 |
| Documentation availability | IT-29 |

## 7. Suggested Django Test Structure

```text
library/
  tests/
    __init__.py
    test_models.py
    test_utilities.py
    test_catalogue_views.py
    test_issue_workflow.py
    test_fine_payment.py
student/
  tests/
    __init__.py
    test_auth_views.py
```

Use a shared fixture mixin or factory helpers for Department, User, Student, Author, Book, and Issue.
Patch the object where it is used, for example `library.views.get_razorpay_client`.

## 8. Execution Commands

```bash
python manage.py makemigrations --check --dry-run
python manage.py test library student
python manage.py test library.tests.test_utilities
python manage.py test library.tests.test_issue_workflow
python manage.py test --keepdb
```

For coverage:

```bash
coverage run manage.py test library student
coverage report -m
coverage html
```

## 9. Entry and Exit Criteria

### Entry criteria

- Test database configuration is available.
- All migrations apply successfully.
- Required fixtures and uploaded test files are prepared.
- Razorpay and time-dependent code can be mocked.

### Exit criteria

- All critical tests (authentication, issue, return, fine, payment) pass.
- No test performs a live Razorpay or Cloudinary network call.
- No migration drift is reported.
- Each failed test has a recorded defect and reproducible input.
- Recommended line coverage for `library` and `student` business logic is at least 80%.

## 10. Test Result Record

| Field | Value to record |
|---|---|
| Test run ID | Date/build identifier |
| Environment | Local, CI, or staging |
| Database | Django test database |
| Total tests | Number executed |
| Passed / failed / skipped | Result counts |
| Coverage | Statement percentage |
| Defects | Linked defect IDs |
| Tester | Name and signature |
| Final status | Pass / Conditional pass / Fail |
