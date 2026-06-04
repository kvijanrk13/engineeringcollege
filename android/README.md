# ENGINEERINGCOLLEGEPROJECTS Android App

This Android project packages the deployed Django site as a Play Store-ready WebView app.

## Current App Settings

- App name: `ENGINEERINGCOLLEGEPROJECTS`
- Package name: `com.anrkit.engineeringcollegeprojects`
- Web app URL: `https://engineeringcollege.onrender.com/`
- Debug emulator URL: `https://engineeringcollege.onrender.com/`
- Minimum Android version: Android 6.0, API 23
- Target SDK: API 35, matching the current Google Play requirement for new apps and app updates.

## Build Requirements

Install Android Studio, then open this `android` folder as the project root. Android Studio will install the Android Gradle plugin, Gradle wrapper, SDK platform, and build tools if they are missing.

## Android Studio Emulator

Debug builds load the deployed Django site through `https://engineeringcollege.onrender.com/`, so icon taps work in the Android Studio Emulator without a local Django server running.

For local-only WebView testing, temporarily change the debug `WEB_APP_URL` in `app/build.gradle` to `http://10.0.2.2:8000/`, then start Django from the `engineeringcollege` folder:

```powershell
python manage.py runserver 0.0.0.0:8000
```

The faculty and student forms are served by Django in the WebView, so emulator debug builds show whatever is deployed on Render by default.

## Build AAB for Play Store

1. Open `engineeringcollege/android` in Android Studio, or build from this folder with `gradlew.bat`.
2. Confirm the web URL in `app/build.gradle`:

   ```gradle
   buildConfigField "String", "WEB_APP_URL", "\"https://engineeringcollege.onrender.com/\""
   ```

3. Choose `Build > Generate Signed App Bundle / APK`.
4. Select `Android App Bundle`.
5. Create or choose a release keystore.
6. Build the release bundle.
7. Upload the generated `.aab` file to Google Play Console.

Command-line build from the `android` folder:

```powershell
.\gradlew.bat bundleRelease
```

Generated bundle:

```text
app/build/outputs/bundle/release/app-release.aab
```

## Play Store Checklist

- Deploy the Django app on HTTPS before review.
- Add a privacy policy URL in Google Play Console.
- Upload `store-assets/play-store-icon.png` as the 512x512 Play Store app icon.
- Use the same package name forever after publishing: `com.anrkit.engineeringcollegeprojects`.
- Increase `versionCode` in `app/build.gradle` for every future release.

Google's target API level reference: https://developer.android.com/google/play/requirements/target-sdk

## Notes

This app depends on the Django server. Keep the Render service and database running, because Android devices will load the live site through the app.
