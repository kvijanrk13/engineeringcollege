# Week 7 - White-Box and Black-Box Testing Techniques

## Test Execution Summary

| Item | Actual output |
|---|---|
| Test command | `python manage.py test library.tests.LibraryWeek7TestingTechniquesTests --settings=engineeringcollege.test_settings` |
| Test database | Isolated in-memory SQLite database |
| White-box tests | 6 |
| Black-box tests | 6 |
| Total tests | 12 |
| Passed / Failed | 12 / 0 |
| Django system check | No issues |
| Execution time | 0.278 seconds |
| Final result | **PASS** |

## 1. Testing Techniques Used

| Testing type | Technique | Simple meaning |
|---|---|---|
| White box | Statement coverage | Execute important program statements at least once |
| White box | Branch coverage | Execute both True and False decision branches |
| White box | Condition coverage | Change individual Boolean conditions |
| White box | Path coverage | Exercise different routes through a function/view |
| White box | Loop coverage | Test zero and nonzero loop iterations |
| White box | Data-flow/signal testing | Verify data changes caused by a save signal |
| Black box | Equivalence partitioning | Test one value from each valid/invalid input group |
| Black box | Boundary-value analysis | Test values at the edge of an allowed range |
| Black box | Decision-table testing | Test results for combinations of conditions and actions |
| Black box | State-transition testing | Verify valid movement between system states |
| Black box | Error guessing | Try likely user mistakes based on experience |

# A. White-Box Testing

White-box testing uses knowledge of the internal Python code, branches, loops, and signals.

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_WB_101 | **Technique: Statement Coverage**<br>1. Create an issued Book overdue by 3 days.<br>2. Call `calcFine(issue)`.<br>3. Read the created Fine. | Overdue statements execute and Fine equals `3 × ₹10 = ₹30`. | Fine was created with amount `30`. | **Pass** |
| BB_WB_102 | **Technique: Branch Coverage**<br>1. Create an issued Book due after 3 days.<br>2. Call `calcFine(issue)`.<br>3. Check Fine records. | The `today > lastdate` False branch returns `no fine`; no Fine is created. | Function returned `no fine` and Fine query was empty. | **Pass** |
| BB_WB_103 | **Technique: Condition Coverage**<br>1. Create an overdue Issue.<br>2. Create a paid Fine of ₹20.<br>3. Call `calcFine(issue)`. | The `not fine.paid` False condition preserves the paid amount. | Paid Fine remained ₹20. | **Pass** |
| BB_WB_104 | **Technique: Path Coverage**<br>1. Create an already-issued Issue.<br>2. Login as Librarian.<br>3. Call Issue Book again. | Already-issued path displays error and does not reset `issued_at`. | Redirect occurred and original issue time was unchanged. | **Pass** |
| BB_WB_105 | **Technique: Loop Coverage**<br>1. Pass `AnonymousUser` to `getmybooks`.<br>2. Inspect both lists. | Zero-iteration path returns empty requested and issued lists. | Both returned lists were empty. | **Pass** |
| BB_WB_106 | **Technique: Data-Flow/Signal Testing**<br>1. Save one active Issue.<br>2. Check LibraryStat.<br>3. Mark Issue returned and save.<br>4. Check LibraryStat again. | Post-save signal changes borrowed count from `1` to `0`. | Borrowed count was `1`, then `0` after return. | **Pass** |

# B. Black-Box Testing

Black-box testing checks inputs and outputs without depending on internal code details.

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_BB_201 | **Technique: Equivalence Partitioning — valid class**<br>1. Enter valid Student ID `23CSE001`.<br>2. Enter valid password.<br>3. Click Login. | Valid input class creates an authenticated session and opens Library Home. | Session was created and response redirected to Library Home. | **Pass** |
| BB_BB_202 | **Technique: Equivalence Partitioning — invalid class**<br>1. Enter valid Student ID.<br>2. Enter invalid password.<br>3. Click Login. | Invalid input class is rejected and no session is created. | Login was rejected and session remained anonymous. | **Pass** |
| BB_BB_203 | **Technique: Boundary-Value Analysis**<br>1. Create an Issue overdue by exactly 1 day.<br>2. Calculate Fine. | Lower overdue boundary produces `1 × ₹10 = ₹10`. | Fine amount was exactly `10`. | **Pass** |
| BB_BB_204 | **Technique: Decision Table**<br>1. Student opens All Issues.<br>2. Librarian opens All Issues.<br>3. Compare responses. | Student is redirected; Librarian receives the page. | Student received redirect; Librarian received HTTP 200. | **Pass** |
| BB_BB_205 | **Technique: State-Transition Testing**<br>1. Student requests Book.<br>2. Librarian issues Book.<br>3. Librarian returns Book.<br>4. Reload Issue. | Issue moves from Requested to Issued to Returned. | Final record had `issued=True` and `returned=True`. | **Pass** |
| BB_BB_206 | **Technique: Error Guessing**<br>1. Login as Student.<br>2. Enter spaces in Search.<br>3. Submit. | Blank-looking search is rejected and user returns to Home with warning. | Response redirected to Library Home as expected. | **Pass** |
