# ETORS

E-Ticketing – Online Reservation System is a Django railway reservation prototype mounted at `/etors/`.

## Initial features

- Search active trains by source, destination, and journey date.
- View schedule, fares, and calculated seat availability.
- Reserve one passenger in Sleeper or AC 3 Tier.
- Generate and retrieve a 10-digit PNR.
- Cancel a confirmed ticket and release its seat.
- Manage stations, trains, bookings, and passengers through Django admin.
- Use the built-in ETORS chatbot for feature and service guidance. Its knowledge
  discovers named ETORS routes at request time and indexes feature items from the
  ETORS templates, so newly exposed and documented features become answerable.
- Provide daily demonstration trains in both directions between Khammam,
  Vijayawada, and Secunderabad, with browser-based journey-date selection.
- Simulate UPI, card, or net-banking payment, display a successful-payment
  confirmation, and reserve a dummy seat without collecting real money.

This is an academic demonstration and is not affiliated with IRCTC or Indian Railways. No real payment is collected.

## Reference research

The feature set was informed by public railway-reservation repositories, including
`mdsoyaib/Online_Railway_Ticket_Booking_System`. That repository does not declare a license, so ETORS is
an original implementation and does not copy its source.
