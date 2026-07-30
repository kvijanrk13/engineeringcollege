# Week 6 - Unit Testing and Integration Testing

## Test Case Execution Note

The tables use the requested test-record format. **Actual Result** and **Status** are execution fields.
They are intentionally marked `Pending execution` and `Not Run`; the tester must replace them with observed
evidence and `Success` or `Fail` after executing each case.

## Test Data

| Test item | Test value |
|---|---|
| Student ID / password | `23CSE001` / `Test@12345` |
| Librarian ID / password | `librarian` / `Admin@12345` |
| Department | `CSE(AI&ML)` |
| Author / book | `Robert C. Martin` / `Clean Code` |
| Category | `TEXT` |
| Fine rate | ₹10 per overdue day |
| Mock payment IDs | `order_test_001`, `pay_test_001`, `signature_test_001` |

# A. Integration Testing Test Cases

## 1. Login and Authentication

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_101 | 1. Open Student Login page.<br>2. Enter valid Student ID `23CSE001`.<br>3. Enter valid password `Test@12345`.<br>4. Click **Login**. | Student is authenticated and the Library Home page is displayed. | Pending execution | Not Run |
| BB_TC_102 | 1. Open Student Login page.<br>2. Enter valid Student ID.<br>3. Enter an invalid password.<br>4. Click **Login**. | An invalid-credentials message is displayed and no authenticated session is created. | Pending execution | Not Run |
| BB_TC_103 | 1. Open the protected Library Home URL without logging in.<br>2. Observe the response. | User is redirected to the student signup/login page. | Pending execution | Not Run |
| BB_TC_104 | 1. Open Student Signup page.<br>2. Enter a new Student ID, name, department, and valid password.<br>3. Submit the form. | User and Student profile are created, the user is logged in, and Library Home is displayed. | Pending execution | Not Run |
| BB_TC_105 | 1. Open Student Signup page.<br>2. Enter an already registered Student ID.<br>3. Submit the form. | Duplicate User is not created and an existing-user message is displayed. | Pending execution | Not Run |
| BB_TC_106 | 1. Login as a student.<br>2. Open an admin-only URL such as Add Book or All Issues. | Student is redirected or denied access; admin page is not displayed. | Pending execution | Not Run |
| BB_TC_107 | 1. Login as Librarian/Admin.<br>2. Open an admin-only URL.<br>3. Verify page access. | Librarian/Admin interface is displayed successfully. | Pending execution | Not Run |
| BB_TC_108 | 1. Login as any valid user.<br>2. Click **Logout**.<br>3. Open a protected URL. | Session is terminated and protected URL redirects to login/signup. | Pending execution | Not Run |

## 2. Catalogue and Search

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_201 | 1. Login as student.<br>2. Open Library Home.<br>3. Observe Text Books, Reference Books, recommendations, and totals. | Catalogue groups and availability totals are displayed from database records. | Pending execution | Not Run |
| BB_TC_202 | 1. Create Book `Clean Code` in test data.<br>2. Enter `clean` in search.<br>3. Submit search. | Search results contain `Clean Code` using case-insensitive matching. | Pending execution | Not Run |
| BB_TC_203 | 1. Create a book with category `TEXT`.<br>2. Search for `text`. | Matching TEXT-category book is displayed. | Pending execution | Not Run |
| BB_TC_204 | 1. Open search.<br>2. Enter only spaces.<br>3. Submit. | Warning asks for a search term and user is redirected to Library Home. | Pending execution | Not Run |
| BB_TC_205 | 1. Login as Admin.<br>2. Open Add Book.<br>3. Select Author.<br>4. Enter name/category and upload a test image.<br>5. Submit. | Book is saved with the selected Author and a success message is displayed. | Pending execution | Not Run |
| BB_TC_206 | 1. Login as Admin.<br>2. Select an existing Book.<br>3. Click Delete Book.<br>4. Confirm deletion. | Book is removed and related Issue records follow configured cascade deletion. | Pending execution | Not Run |
| BB_TC_207 | 1. Create Authors and Books starting with different letters.<br>2. Sort by Author and then Book.<br>3. Select a starting letter. | Only records beginning with the selected value are displayed in the correct sort mode. | Pending execution | Not Run |

## 3. Book Issue Request and Approval

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_301 | 1. Login as student.<br>2. Select an available Book.<br>3. Click **Request Book Issue**. | One pending Issue record is created and a success message is displayed. | Pending execution | Not Run |
| BB_TC_302 | 1. Repeat the same request for the same Student and Book.<br>2. Inspect Issue records. | `get_or_create` prevents a duplicate Issue record. | Pending execution | Not Run |
| BB_TC_303 | 1. Login as Admin.<br>2. Open All Issues.<br>3. Select a pending Issue.<br>4. Click Issue Book. | `issued=True`; `issued_at` is set; return date is set approximately 15 days ahead. | Pending execution | Not Run |
| BB_TC_304 | 1. Attempt to approve an already issued record again. | Error message states that the Book is already issued and issue dates are not reset. | Pending execution | Not Run |
| BB_TC_305 | 1. Create pending and issued Issues for a Student.<br>2. Open My Issues with issued filter.<br>3. Repeat with pending filter. | Each filter displays only the corresponding Issue state. | Pending execution | Not Run |
| BB_TC_306 | 1. Login as Admin.<br>2. Search issue requests by valid Student ID. | Pending Issues for that Student are displayed. | Pending execution | Not Run |
| BB_TC_307 | 1. Search issue requests using an unknown Student ID. | No-student message is displayed and user returns to All Issues. | Pending execution | Not Run |
| BB_TC_308 | 1. Create both pending and issued Issues.<br>2. Admin submits Clear Pending Issues. | Pending Issues are deleted, issued records remain, and LibraryStat is recalculated. | Pending execution | Not Run |

## 4. Book Return and Fine Management

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_401 | 1. Create an issued Book with future return date.<br>2. Login as Admin.<br>3. Return the Book. | Issue is marked returned and no Fine is created. | Pending execution | Not Run |
| BB_TC_402 | 1. Create an issued Book overdue by 3 days.<br>2. Return the Book. | Issue is marked returned and a Fine of ₹30 is created. | Pending execution | Not Run |
| BB_TC_403 | 1. Login as student with an overdue Issue.<br>2. Open My Fines. | Fine calculation runs and the unpaid Fine is displayed. | Pending execution | Not Run |
| BB_TC_404 | 1. Login as Admin.<br>2. Open All Fines.<br>3. Enter a valid numeric amount.<br>4. Submit update. | Fine amount is updated and success message is displayed. | Pending execution | Not Run |
| BB_TC_405 | 1. Open an existing Fine.<br>2. Enter nonnumeric amount `abc`.<br>3. Submit. | Fine amount remains unchanged and invalid-amount message is displayed. | Pending execution | Not Run |
| BB_TC_406 | 1. Open an unpaid Fine as Admin.<br>2. Click **Waive Fine**. | Fine amount becomes zero and `paid=True`. | Pending execution | Not Run |
| BB_TC_407 | 1. Open an existing Fine as Admin.<br>2. Click Delete Fine.<br>3. Confirm. | Fine record is deleted and success message is displayed. | Pending execution | Not Run |
| BB_TC_408 | 1. Create active issued records and nonzero LibraryStat.<br>2. Submit Reset Circulation. | Borrowed count becomes zero and active issue records are reset/marked returned. | Pending execution | Not Run |

## 5. Razorpay Fine Payment

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_501 | 1. Create unpaid Fine of ₹30.<br>2. Mock Razorpay client.<br>3. Open Pay Fine. | Razorpay order is created for `3000` paise, currency `INR`, using Fine order ID as receipt. | Pending execution | Not Run |
| BB_TC_502 | 1. Mock order response as `order_test_001`.<br>2. Open Pay Fine page. | Payment template displays ₹30 and contains the mocked Razorpay order ID. | Pending execution | Not Run |
| BB_TC_503 | 1. Mock signature verification success.<br>2. POST order ID, payment ID, and signature to payment status URL. | Fine becomes paid; payment IDs, signature, and payment date are saved. | Pending execution | Not Run |
| BB_TC_504 | 1. Mock signature verification failure/exception.<br>2. POST payment callback. | Fine remains unpaid and Payment Failure message is displayed. | Pending execution | Not Run |
| BB_TC_505 | 1. Execute payment tests with mocked client.<br>2. Monitor network calls. | No real Razorpay request is made during automated testing. | Pending execution | Not Run |

## 6. Documentation and Database Integration

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_TC_601 | 1. Open `/aeclibrary/documentation/`.<br>2. Inspect section headings. | Week 1, Week 2, Week 3, Week 4 and Week 5, and Week 6 are rendered. | Pending execution | Not Run |
| BB_TC_602 | 1. Delete an Author that owns Books.<br>2. Inspect database records. | Related Books and dependent records follow configured cascade behavior. | Pending execution | Not Run |
| BB_TC_603 | 1. Create a Student profile for a User.<br>2. Attempt a second Student profile for the same User. | Database rejects the second profile with one-to-one integrity error. | Pending execution | Not Run |
| BB_TC_604 | 1. Create Fine with a fixed order ID.<br>2. Attempt another Fine with the same order ID. | Database rejects duplicate order ID with uniqueness error. | Pending execution | Not Run |

# B. Unit Testing Test Cases

## 7. Model Unit Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_UT_701 | 1. Create Author named `Robert C. Martin`.<br>2. Call `str(author)`. | Returns `Robert C. Martin`. | Pending execution | Not Run |
| BB_UT_702 | 1. Create Book named `Clean Code`.<br>2. Call `str(book)`. | Returns `Clean Code`. | Pending execution | Not Run |
| BB_UT_703 | 1. Configure Cloudinary cloud name.<br>2. Set Book image name.<br>3. Access `cloudinary_image_url`. | Generated URL contains the configured cloud name and image path. | Pending execution | Not Run |
| BB_UT_704 | 1. Create Student linked to `23CSE001` and Department.<br>2. Call `str(student)`. | String contains first name, last four username characters, and department. | Pending execution | Not Run |
| BB_UT_705 | 1. Create Fine with `order_id=None`.<br>2. Save Fine. | A non-empty unique order ID is generated. | Pending execution | Not Run |
| BB_UT_706 | 1. Save Fine with `order_id=ORDER-1`.<br>2. Change amount and save again. | Existing order ID remains `ORDER-1`. | Pending execution | Not Run |
| BB_UT_707 | 1. Create issued Issue with future due date.<br>2. Call `days_no()`. | Result contains `left`. | Pending execution | Not Run |
| BB_UT_708 | 1. Create issued Issue overdue by 3 days.<br>2. Call `days_no()`. | Result contains `passed`. | Pending execution | Not Run |
| BB_UT_709 | 1. Save one active issued Issue.<br>2. Load `LibraryStat(id=1)`. | Post-save signal sets borrowed count to active issued/not-returned count. | Pending execution | Not Run |
| BB_UT_710 | 1. Create blank-title BookRecommendation.<br>2. Call `str(recommendation)`. | Returns `Book Recommendation`. | Pending execution | Not Run |

## 8. Utility and Helper Unit Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_UT_801 | 1. Create issued Issue with future return date.<br>2. Call `calcFine(issue)`. | Returns `no fine` and creates no Fine. | Pending execution | Not Run |
| BB_UT_802 | 1. Create issued Issue overdue by 3 days.<br>2. Call `calcFine(issue)`.<br>3. Refresh Fine. | Fine exists with amount ₹30. | Pending execution | Not Run |
| BB_UT_803 | 1. Create an overdue Issue with an already paid Fine.<br>2. Call `calcFine(issue)`. | Paid Fine amount is not recalculated. | Pending execution | Not Run |
| BB_UT_804 | 1. Create returned Issue.<br>2. Call `calcFine(issue)`. | Returns `no fine` and creates no new Fine. | Pending execution | Not Run |
| BB_UT_805 | 1. Pass AnonymousUser to `getmybooks`.<br>2. Inspect returned lists. | Requested and issued lists are both empty. | Pending execution | Not Run |
| BB_UT_806 | 1. Create Student with pending Issue.<br>2. Call `getmybooks(user)`. | Book appears only in requested list. | Pending execution | Not Run |
| BB_UT_807 | 1. Create Student with issued Issue.<br>2. Call `getmybooks(user)`. | Book appears only in issued list. | Pending execution | Not Run |
| BB_UT_808 | 1. Override both Google OAuth settings with values.<br>2. Call `google_signin_enabled()`.<br>3. Repeat with one missing value. | Returns True only when both client ID and secret are non-empty. | Pending execution | Not Run |

## 9. Execution and Result Recording

Run the Django tests:

```bash
python manage.py makemigrations --check --dry-run
python manage.py test library student
```

After each test:

1. Replace `Pending execution` with the observed result.
2. Replace `Not Run` with `Success` when actual and expected results match.
3. Use `Fail` when they differ.
4. Record a defect ID and screenshot/log evidence for every failed test.
5. Never mark a test `Success` without executing it.
