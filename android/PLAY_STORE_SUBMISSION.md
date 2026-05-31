# Play Store Submission Guide

## App Identity

- App name: `ENGINEERINGCOLLEGEPROJECTS`
- Package name: `com.anrkit.engineeringcollegeprojects`
- First release version: `1.0.0`
- First release version code: `1`
- App type: Android WebView client for the Django web application

## Required Before Upload

1. Confirm the Django app is deployed and reachable over HTTPS:

   `https://anrkitdept.onrender.com/`

2. Open `android` in Android Studio.
3. Let Android Studio sync the Gradle project.
4. Run the app on an Android emulator or physical phone.
5. Test login, dashboard navigation, file upload, PDF download, and logout.
6. Generate a signed Android App Bundle using:

   `Build > Generate Signed App Bundle / APK > Android App Bundle`

7. Upload the `.aab` file to Google Play Console.

## Store Listing Assets

Google Play Console normally requires:

- 512 x 512 app icon
- 1024 x 500 feature graphic
- Phone screenshots
- Short description
- Full description
- Privacy policy URL
- App category
- Data safety declaration
- Content rating questionnaire

Source artwork is included in `store-assets`. Export those SVG files to PNG before uploading them in Play Console.

## Suggested Listing Text

Short description:

`Engineering college department dashboard for students, faculty, certificates, reports, and academic resources.`

Full description:

`ENGINEERINGCOLLEGEPROJECTS provides Android access to the engineering college department portal. Students and faculty can open dashboards, view academic resources, manage department information, access reports, and download generated documents from the deployed Django platform.`

## Future Updates

For every new Play Store upload, increase `versionCode` in `app/build.gradle`.

Example:

```gradle
versionCode 2
versionName "1.0.1"
```
