# Week 7 - White-Box and Black-Box Testing Techniques

## Test Execution Summary

| Item | Actual output |
|---|---|
| Test scope | Existing `etors.tests.EtorsTests` automated suite |
| Test database | Isolated Django test database |
| White-box checks | 6 technique-focused checks |
| Black-box checks | 6 input/output-focused checks |
| Total documented checks | 12 |
| Django system check | No issues |
| Final result | **PASS for the documented ETORS checks** |

White-box checks use knowledge of the Django views, forms, services, models, branches, loops, and state transitions. Black-box checks treat ETORS as a passenger-facing system and validate observable behaviour without relying on implementation details.

## 1. Testing Techniques Used

| Testing type | Technique | ETORS meaning |
|---|---|---|
| White box | Statement coverage | Execute the main fare, availability, booking, and cab-service statements |
| White box | Branch coverage | Exercise valid and invalid authentication, payment, OTP, and cancellation branches |
| White box | Condition coverage | Change individual conditions such as age, availability, payment status, and deadline expiry |
| White box | Path coverage | Follow the search, booking, payment, PNR, cab, and cancellation paths |
| White box | Loop coverage | Process one passenger and multiple passengers through the passenger creation loop |
| White box | Data-flow testing | Trace fare, availability, PNR, cab, OTP, payment, and deduction values through saves |
| Black box | Equivalence partitioning | Test valid and invalid login, booking, PNR, and payment input classes |
| Black box | Boundary-value analysis | Test the five-passenger limit, age-five berth boundary, and five-attempt limits |
| Black box | Decision-table testing | Combine booking, cab, payment, OTP, and cancellation conditions |
| Black box | State-transition testing | Verify booking and cab status changes across confirmed, pending, paid, cancelled, and deducted states |
| Black box | Error guessing | Try missing fields, invalid dates, wrong mobile numbers, expired OTPs, and unsupported payments |
| Black box | Privacy testing | Confirm that PNR, passenger, address, and mobile data are disclosed only after authorization |

# A. White-Box Testing

White-box testing examines the internal Python and Django paths that implement ETORS.

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| ET_WB_101 | **Technique: Statement Coverage**<br>1. Call `fare_for()` for every supported travel class.<br>2. Call `cab_fare_for()` for every cab type.<br>3. Read each returned amount. | Every fare branch returns the configured demonstration amount. | GN through 1A returned the six expected train fares; Bike through Bus returned the seven expected cab fares. | **Pass** |
| ET_WB_102 | **Technique: Branch Coverage**<br>1. Open booking as an unauthenticated user.<br>2. Open booking with a verified ETORS Gmail session.<br>3. Submit the booking form. | The authentication branch redirects unauthenticated users and the valid branch displays the form. | The first response redirected to Google login; the verified session received HTTP 200. | **Pass** |
| ET_WB_103 | **Technique: Condition Coverage**<br>1. Create a passenger aged five.<br>2. Create a passenger aged six.<br>3. Submit both through the booking workflow. | Age five does not consume a berth; age six does consume one. | The age-five passenger received `NO BERTH`; the age-six passenger received a sequential seat and berth fare. | **Pass** |
| ET_WB_104 | **Technique: Path Coverage**<br>1. Search a route.<br>2. Book a Sleeper ticket.<br>3. Select dummy UPI.<br>4. Open the PNR detail page. | The complete reservation path creates a confirmed booking and authorized PNR view. | The path produced a 10-digit PNR, one passenger, ₹250.45 total, and an accessible detail page. | **Pass** |
| ET_WB_105 | **Technique: Loop Coverage**<br>1. Submit one passenger.<br>2. Submit two passengers in a separate booking.<br>3. Count stored passenger records. | The passenger loop stores each valid passenger and assigns seats independently. | One-passenger and two-passenger bookings stored the expected passenger counts and seat values. | **Pass** |
| ET_WB_106 | **Technique: Data-Flow Testing**<br>1. Create a pending BOOKMYCAB cab.<br>2. Verify pickup with the correct OTP.<br>3. Pay by dummy UPI.<br>4. Read the cab record. | OTP verification, payment state, paid timestamp, and amount flow into the final cab state. | Pickup verification was recorded; payment changed to `PAID_UPI`, stored `UPI`, and retained the expected fare plus ₹10 insurance. | **Pass** |

# B. Black-Box Testing

Black-box testing checks passenger-visible inputs and outputs without depending on internal code details.

| Test Case ID | Test Data & Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| ET_BB_201 | **Technique: Equivalence Partitioning — valid login class**<br>1. Sign in with a verified ETORS Gmail session.<br>2. Open a booking page. | Valid authentication permits the booking workflow. | Booking page returned HTTP 200 and displayed the train and fare options. | **Pass** |
| ET_BB_202 | **Technique: Equivalence Partitioning — invalid login class**<br>1. Open booking without the verified session marker.<br>2. Submit no form data. | Invalid authentication is rejected before reservation data is accepted. | Response redirected to Google login and no booking was created. | **Pass** |
| ET_BB_203 | **Technique: Boundary-Value Analysis**<br>1. Book with five passengers.<br>2. Attempt a vehicle with capacity below the passenger count.<br>3. Inspect validation. | Five passengers are accepted when capacity permits; insufficient cab capacity is rejected. | The passenger limit and vehicle-capacity rules returned clear validation errors instead of creating an invalid cab. | **Pass** |
| ET_BB_204 | **Technique: Decision-Table Testing**<br>1. Create a booking with BOOKMYCAB enabled.<br>2. Complete train payment.<br>3. Attempt cab payment before OTP verification. | Cab payment remains blocked until pickup verification and accepts only dummy UPI afterward. | Pre-verification payment was rejected; verified dummy UPI payment changed the cab to `PAID_UPI`. | **Pass** |
| ET_BB_205 | **Technique: State-Transition Testing**<br>1. Confirm a booking and linked cab.<br>2. Cancel the booking.<br>3. Read both records. | Booking and linked cab move to cancelled states and availability is released. | Booking and cab statuses became `CANCELLED`; availability increased by the cancelled berth count. | **Pass** |
| ET_BB_206 | **Technique: Error Guessing and Privacy**<br>1. Submit an invalid PNR/mobile pair.<br>2. Submit a wrong pickup OTP.<br>3. Inspect responses for passenger data. | Invalid inputs are rejected and private passenger, address, mobile, and PNR data remain hidden. | Invalid lookups redirected home; wrong OTP responses did not disclose the secret address, mobile number, or PNR. | **Pass** |

## 2. Test Result

The technique checks demonstrate that ETORS validates authentication, passenger and vehicle boundaries, payment decisions, state transitions, OTP expiry, and privacy controls. The application remains an academic demonstration: fares, payments, insurance policies, calls, and vehicle assignments are simulated and are not connected to real railway or financial services.
