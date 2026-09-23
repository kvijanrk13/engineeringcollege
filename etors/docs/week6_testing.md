# Week 6 - Unit Testing and Integration Testing

## Test Execution Summary

| Item | Actual output |
|---|---|
| Test scope | Existing `etors.tests.EtorsTests` automated suite |
| Test database | Isolated Django test database |
| Integration checks | 8 representative end-to-end workflows |
| Unit checks | 4 service and model behaviour checks |
| Django system check | No issues |
| Final result | **PASS for the documented ETORS checks** |

The cases below are mapped to assertions already present in `etors/tests.py`. They demonstrate the implemented reservation, payment, PNR, cancellation, BOOKMYCAB, privacy, and service rules rather than a separate mock system.

## Test Data

| Test item | Value |
|---|---|
| Test stations | `TST` Test Source → `TEN` Test End |
| Test train | `99999` · Test Express |
| Train capacity | 2 berths |
| Sleeper / AC base fare | ₹250.00 / ₹700.00 |
| Journey date | Today + 2 days |
| Passenger | Asha Kumar · age 24 · Sleeper · Lower berth |
| Train amount | ₹250.00 fare + ₹0.45 insurance = ₹250.45 |
| BOOKMYCAB example | Sedan · ₹500.00 fare + ₹10.00 insurance |
| Cab schedule | Destination station 20 minutes before train arrival |
| Demonstration boundary | No real ticket, payment, insurance, call, or vehicle dispatch |

# A. Integration Testing

## 1. Authentication and Train Search

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| ET_TC_101 | 1. Open ETORS Home.<br>2. Select Test Source and Test End.<br>3. Select the test journey date.<br>4. Search trains. | The matching active train is displayed with schedule and availability. | Response was HTTP 200 and contained `99999 - Test Express`, the 120-day date controls, and the calculated availability. | **Pass** |
| ET_TC_102 | 1. Open the booking URL without a verified ETORS Gmail session.<br>2. Submit no booking data. | Booking is blocked and the browser is sent to Gmail authentication. | Response redirected to the Google login route with `target=etors`; no `Booking` was created. | **Pass** |
| ET_TC_103 | 1. Sign in and mark the session as a verified ETORS Gmail login.<br>2. Open the booking URL. | The authenticated passenger can view the booking form. | Booking page returned HTTP 200 with the train, journey date, fare options, and availability. | **Pass** |

## 2. Reservation, Payment, and PNR

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| ET_TC_104 | 1. Sign in with a verified ETORS Gmail session.<br>2. Open `/etors/payment/` without a pending reservation. | Payment is rejected and the passenger returns to ETORS Home. | Response redirected to `etors:home` with the pending-booking error. | **Pass** |
| ET_TC_105 | 1. Submit the Asha Kumar Sleeper booking.<br>2. Select dummy UPI on the payment page.<br>3. Inspect the confirmation and database records. | A booking, passenger, PNR, seat, and insurance policy are created atomically. | Response contained `PAYMENT SUCCESSFULL` and `S001`; the booking total was `250.45`, PNR length was 10, and one passenger was stored. | **Pass** |
| ET_TC_106 | 1. Open a PNR without the registered mobile number.<br>2. Repeat with the correct registered mobile number. | A PNR alone cannot reveal the booking; the matching pair authorizes the detail page. | Wrong lookup redirected home; the matching lookup redirected to the PNR detail page and displayed the passenger. | **Pass** |

## 3. Cancellation and BOOKMYCAB

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| ET_TC_107 | 1. Create and authorize a confirmed booking with one passenger.<br>2. Cancel it through the protected POST route. | Booking becomes cancelled and its berth is released. | Booking status changed to `CANCELLED`; availability increased from 1 to 2. | **Pass** |
| ET_TC_108 | 1. Book a Sedan for Meera Rao with a destination address.<br>2. Complete dummy train payment.<br>3. Inspect the linked cab and cancel the booking. | Cab is scheduled 20 minutes before arrival, linked to the booking, and cancelled with the train reservation. | Cab reference, driver, vehicle, ₹500 fare, ₹10 insurance, and early-arrival schedule were stored; cancellation changed cab status to `CANCELLED`. | **Pass** |

# B. Unit Testing

## 4. Service and Model Behaviour

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| ET_UT_201 | 1. Call `fare_for()` for GN, SL, 3E, 3A, 2A, and 1A on the test train. | Class fares follow the configured multipliers. | Results were ₹150.00, ₹250.00, ₹630.00, ₹700.00, ₹980.00, and ₹1,400.00. | **Pass** |
| ET_UT_202 | 1. Create a confirmed passenger booking.<br>2. Read `train_availability()`.<br>3. Cancel the booking and read it again. | Availability decreases for a confirmed passenger and increases after cancellation. | Availability changed from 2 to 1 and returned to 2 after cancellation. | **Pass** |
| ET_UT_203 | 1. Call `cab_schedule_for()` for the test train and journey date. | Cab arrival is 20 minutes before train arrival, including overnight handling when needed. | The returned datetimes preserved the 20-minute offset and applied the next-day rule for overnight arrivals. | **Pass** |
| ET_UT_204 | 1. Create a BOOKMYCAB record through the booking workflow.<br>2. Inspect its reference, OTP hash, insurance, driver, and vehicle fields. | Demonstration identifiers are unique, the OTP is not stored in plain text, and required cab data is populated. | A unique cab reference, hashed pickup OTP, policy, driver, vehicle, fare, and schedule were stored. | **Pass** |

## 5. Integration Result

The documented checks cover the complete ETORS path from public train search through authenticated booking, dummy payment, PNR protection, cancellation, destination transport, and privacy-sensitive cab dispatch. All demonstration data remains isolated from real railway, banking, insurance, telephone, and vehicle-dispatch services.
