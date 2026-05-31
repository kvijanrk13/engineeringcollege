# Gmail Sign-In Setup

The login screen now sends users through Django routes before redirecting to Google. To enable it on Render, create Google OAuth credentials and add them to the Render service environment.

## Google Cloud Console

Create an OAuth 2.0 Client ID for a web application.

Authorized redirect URI:

```text
https://engineeringcollege.onrender.com/google/callback/
```

If you also use the second Render domain, add:

```text
https://anrkitdept.onrender.com/google/callback/
```

## Render Environment Variables

Add these to the Render web service:

```text
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

After saving the variables, redeploy the service.

## Account Matching

Admin Gmail sign-in only works when the Gmail address matches a Django staff user's `email`.

Student Gmail sign-in only works when the Gmail address matches a `Student.email` value.

If the Gmail address is not linked to an account, the user is returned to the login screen with an error message.
