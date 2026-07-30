# Week 6 - Unit and Integration Testing

## Result

The executable Week 6 suite completed successfully: **12 passed, 0 failed** in **1.121 seconds** using an
isolated in-memory test database. Representative cases are shown below.

## Integration Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_101 | 1. Enter valid Student ID and password.<br>2. Click Login. | Student session is created and Library Home opens. | Session created; redirected to `/aeclibrary/`. | **Pass** |
| BB_TC_102 | 1. Search for `clean`.<br>2. View results. | `Clean Code` is displayed. | HTTP 200 response contained `Clean Code`. | **Pass** |
| BB_TC_103 | 1. Request the same Book twice.<br>2. Count Issue records. | Only one Issue exists. | Exactly one Issue was stored. | **Pass** |
| BB_TC_104 | 1. Librarian approves a pending Issue.<br>2. Reload record. | Issue date and future return date are saved. | `issued=True` and both dates were saved. | **Pass** |

## Unit Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_UT_201 | 1. Create a Book overdue by 3 days.<br>2. Call `calcFine`. | Fine equals ₹30. | Fine amount was `30`. | **Pass** |
| BB_UT_202 | 1. Save one active Issue.<br>2. Read LibraryStat. | Borrowed count equals 1. | Borrowed count was `1`. | **Pass** |

## Run

```bash
python manage.py test library.tests.LibraryWeek6Tests \
  --settings=engineeringcollege.test_settings
```
