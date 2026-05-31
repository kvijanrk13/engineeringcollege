# Android Release Checklist

## Before Building

- Confirm the Django site is live at `https://engineeringcollege.onrender.com/`.
- Confirm the privacy policy opens at `https://engineeringcollege.onrender.com/privacy-policy/`.
- Test admin login, student login, Gmail login, file upload, and PDF download on the website.
- Open the `android` folder in Android Studio and let Gradle sync.

## Build

- Use `Build > Generate Signed App Bundle / APK`.
- Select `Android App Bundle`.
- Use a release keystore and keep it backed up.
- Upload the generated `.aab` file to Google Play Console.

## Play Console

- App name: `ENGINEERINGCOLLEGEPROJECTS`
- Package name: `com.anrkit.engineeringcollegeprojects`
- Privacy policy: `https://engineeringcollege.onrender.com/privacy-policy/`
- Category: Education
- Data safety: declare account/profile data, student/faculty records, files/documents, and app activity as applicable.
- Target SDK: 35

## Future Releases

Increase `versionCode` in `android/app/build.gradle` before each new Play Store upload.
