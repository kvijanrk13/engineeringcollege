# PhonePe Payment Gateway Setup

This project uses PhonePe Standard Checkout to receive a merchant payment before
allowing the EngineeringCollege source ZIP download. It does not implement
peer-to-peer transfers or payouts.

## Required environment variables

```text
PHONEPE_ENVIRONMENT=sandbox
PHONEPE_CLIENT_ID=
PHONEPE_CLIENT_SECRET=
PHONEPE_CLIENT_VERSION=1
PHONEPE_CALLBACK_USERNAME=
PHONEPE_CALLBACK_PASSWORD=
```

Use long, randomly generated callback credentials. Store all values only in the
deployment provider's secret/environment settings. Never commit them to Git.
Immediately rotate any Cloudinary, admin, PhonePe, or other credentials that
were previously committed, because deleting them from the current files does
not remove them from Git history.

Set `PHONEPE_ENVIRONMENT=production` only after PhonePe approves the live
merchant account and provides production credentials.

## PhonePe dashboard configuration

Configure this HTTPS server callback URL in the PhonePe merchant dashboard:

```text
https://YOUR-DOMAIN/payments/phonepe/callback/
```

Configure the same callback username and password in PhonePe and in the
application environment. The callback route validates PhonePe's authorization
hash and then independently calls PhonePe's Order Status API. A callback body or
browser redirect alone can never unlock the ZIP.

## Deployment checklist

1. Complete PhonePe merchant onboarding and KYC.
2. Add the sandbox credentials and callback credentials as deployment secrets.
3. Run `python manage.py migrate`.
4. Test successful, failed, cancelled, pending, wrong-amount, and duplicate
   callback cases in sandbox.
5. Switch to production credentials only after sandbox verification.
6. Keep `DEBUG=False`, HTTPS redirect enabled, and database backups configured.

The protected ZIP URL is session-bound and re-checks the payment with PhonePe
before every download.

The `Show Payment QR` action first creates a PhonePe order, then displays a QR
containing PhonePe's hosted checkout URL. It is not a static UPI QR, so the
payment remains linked to the order and can be securely verified before the ZIP
is unlocked.
