# Week 6 - Unit Testing and Integration Testing

## Test Execution Summary

| Item | Actual output |
|---|---|
| Test command | `python manage.py test library.tests.LibraryWeek6Tests --settings=engineeringcollege.test_settings` |
| Test database | Isolated in-memory SQLite database |
| Tests executed | 12 |
| Passed | 12 |
| Failed | 0 |
| Django system check | No issues |
| Execution time | 1.121 seconds |
| Final result | **PASS** |

## Test Data

| Test item | Value |
|---|---|
| Student login | `23CSE001` / `Test@12345` |
| Librarian login | `librarian` / `Admin@12345` |
| Department | `CSE(AI&ML)` |
| Author and Book | `Robert C. Martin` / `Clean Code` |
| Book category | `TEXT` |
| Overdue period | 3 days |
| Fine rate | ₹10 per day |

# A. Integration Testing

## 1. Login and Access Control

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_101 | 1. Open Student Login.<br>2. Enter `23CSE001`.<br>3. Enter `Test@12345`.<br>4. Click Login. | Student is authenticated and redirected to Library Home. | Student session was created and response redirected to `/aeclibrary/`. | **Pass** |
| BB_TC_102 | 1. Open Student Login.<br>2. Enter valid Student ID.<br>3. Enter `wrong-password`.<br>4. Click Login. | Login is rejected and user returns to signup/login. | No authenticated session was created; response redirected to signup. | **Pass** |
| BB_TC_103 | 1. Logout/clear session.<br>2. Open `/aeclibrary/`. | Anonymous user is redirected to student signup/login. | Protected home returned a redirect to the configured login page. | **Pass** |

## 2. Catalogue and Issue Workflow

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_104 | 1. Login as Student.<br>2. Search for `clean`.<br>3. View search results. | `Clean Code` is displayed using case-insensitive search. | Response was HTTP 200 and contained `Clean Code`. | **Pass** |
| BB_TC_105 | 1. Login as Student.<br>2. Request `Clean Code` twice.<br>3. Count matching Issue records. | Only one pending Issue is stored. | Database contained exactly one Student–Book Issue record. | **Pass** |
| BB_TC_106 | 1. Create pending Issue.<br>2. Login as Librarian.<br>3. Click Issue Book. | Issue is approved, issue date is set, and return date is in the future. | `issued=True`; `issued_at` and future `return_date` were saved. | **Pass** |
| BB_TC_107 | 1. Create an issued Book due in 5 days.<br>2. Login as Librarian.<br>3. Return the Book. | Issue is marked returned and no Fine is created. | `returned=True` and the Fine query returned no record. | **Pass** |

## 3. Documentation Integration

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_108 | 1. Open `/aeclibrary/documentation/`.<br>2. Check the section headings. | Week 4 and Week 5 and Week 6 headings are rendered. | Response was HTTP 200 and contained both required headings. | **Pass** |

# B. Unit Testing

## 4. Model Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_UT_201 | 1. Create Author `Robert C. Martin`.<br>2. Create Book `Clean Code`.<br>3. Call `str()` on both objects. | Model string methods return their names. | Author returned `Robert C. Martin`; Book returned `Clean Code`. | **Pass** |
| BB_UT_202 | 1. Save one active issued Issue.<br>2. Read `LibraryStat(id=1)`. | Post-save signal sets borrowed count to 1. | `LibraryStat.borrowed_books` was exactly `1`. | **Pass** |

## 5. Utility Function Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_UT_203 | 1. Create an Issue overdue by 3 days.<br>2. Call `calcFine(issue)`.<br>3. Read the Fine amount. | Fine is calculated as `3 × ₹10 = ₹30`. | Fine record was created with amount `30`. | **Pass** |
| BB_UT_204 | 1. Create an unissued request for the Student.<br>2. Call `getmybooks(user)`.<br>3. Inspect both returned lists. | Book appears in requested list and not in issued list. | Requested list contained `Clean Code`; issued list did not. | **Pass** |
