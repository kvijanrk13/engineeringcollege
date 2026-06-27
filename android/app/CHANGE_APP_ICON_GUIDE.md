
# How to Change the App Icon

This guide explains how to change the app icon for your Android application.

## 1. Understanding Android App Icons

Android requires you to provide your app icon in different sizes to ensure it looks great on all devices. These icons are placed in `mipmap` directories in your project's `res` folder.

The standard densities and their corresponding icon sizes are:

*   **mdpi:** 48x48 pixels
*   **hdpi:** 72x72 pixels
*   **xhdpi:** 96x96 pixels
*   **xxhdpi:** 144x144 pixels
*   **xxxhdpi:** 192x192 pixels

You should also provide a round version of your icon for devices that use round icons.

## 2. Using Android Studio's Image Asset Studio (Recommended)

The easiest way to generate these different icon sizes is to use the **Image Asset Studio** built into Android Studio.

1.  **Open your project in Android Studio.**
2.  In the **Project** window, right-click the `app` folder and select **New > Image Asset**.
3.  In the **Asset Type** dropdown, select **Launcher Icons (Adaptive & Legacy)**.
4.  For the **Foreground Layer**, choose your source image (e.g., a high-resolution logo). You can also choose a clipart or text.
5.  Adjust the **Background Layer** and other settings as needed.
6.  Click **Next**, then **Finish**. Android Studio will automatically generate the icons in the correct `mipmap` directories.

## 3. Manually Creating and Placing Icons

If you prefer to create the icons manually, you'll need to create PNG files for each of the sizes listed above and place them in the following directories:

*   `app/src/main/res/mipmap-mdpi/ic_launcher.png`
*   `app/src/main/res/mipmap-hdpi/ic_launcher.png`
*   `app/src/main/res/mipmap-xhdpi/ic_launcher.png`
*   `app/src/main/res/mipmap-xxhdpi/ic_launcher.png`
*   `app/src/main/res/mipmap-xxxhdpi/ic_launcher.png`

You should also create round versions:

*   `app/src/main/res/mipmap-mdpi/ic_launcher_round.png`
*   `app/src/main/res/mipmap-hdpi/ic_launcher_round.png`
*   `app/src/main/res/mipmap-xhdpi/ic_launcher_round.png`
*   `app/src/main/res/mipmap-xxhdpi/ic_launcher_round.png`
*   `app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png`

## 4. Update the AndroidManifest.xml

Finally, ensure your `AndroidManifest.xml` file (located at `app/src/main/AndroidManifest.xml`) references the new icons. The `<application>` tag should have `android:icon` and `android:roundIcon` attributes pointing to your icons in the `mipmap` directories:

```xml
<application
    ...
    android:icon="@mipmap/ic_launcher"
    android:roundIcon="@mipmap/ic_launcher_round"
    ...>
    ...
</application>
```

By default, it already points to `ic_launcher`, so if you follow the naming convention, you don't need to change anything.
