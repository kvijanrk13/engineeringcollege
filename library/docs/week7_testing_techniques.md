# Week 7 - White-Box and Black-Box Testing

## Result

The Week 7 suite executed **6 white-box** and **6 black-box** tests: **12 passed, 0 failed** in
**0.278 seconds**. Representative techniques are shown below.

## White-Box Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_WB_101 | **Statement coverage:** Run `calcFine` for an Issue overdue by 3 days. | Fine calculation statements produce ₹30. | Fine amount was `30`. | **Pass** |
| BB_WB_102 | **Branch coverage:** Run `calcFine` before the due date. | False overdue branch returns `no fine`. | Returned `no fine`; no Fine created. | **Pass** |
| BB_WB_103 | **Loop coverage:** Call `getmybooks` with AnonymousUser. | Zero-iteration path returns empty lists. | Both lists were empty. | **Pass** |

## Black-Box Tests

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| BB_BB_201 | **Equivalence partitioning:** Login with valid credentials. | Valid class is accepted. | Session created and Home redirect returned. | **Pass** |
| BB_BB_202 | **Boundary value:** Calculate Fine at exactly 1 day overdue. | Fine equals ₹10. | Fine amount was `10`. | **Pass** |
| BB_BB_203 | **State transition:** Request, issue, and return a Book. | Issue moves Requested → Issued → Returned. | Final flags were issued and returned. | **Pass** |

## Run

```bash
python manage.py test library.tests.LibraryWeek7TestingTechniquesTests \
  --settings=engineeringcollege.test_settings
```
