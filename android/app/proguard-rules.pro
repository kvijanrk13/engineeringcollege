# ProGuard rules for the EngineeringCollegeProjects app.
# Code shrinking and obfuscation are enabled for release builds.
# These rules prevent the removal or renaming of essential code.

# Keep the main activity that hosts the WebView. The AndroidManifest.xml
# refers to it by name, so it must not be obfuscated.
-keep public class com.anrkit.engineeringcollegeprojects.MainActivity { *; }

# The BuildConfig class is generated at build time and is often accessed
# from various parts of the app. It's safe to keep it.
-keep class com.anrkit.engineeringcollegeprojects.BuildConfig { *; }

# For WebView-based apps, it's important to keep the WebView class and its
# methods, as they are part of the Android framework and are called by native code.
-keepclassmembers class android.webkit.WebView {
   public *;
}

# If you use a JavaScript interface to communicate between your web page and
# the Android app, the methods called by JavaScript must be kept.
# Replace 'YourJsInterface' with the actual name of your interface class.
# -keepclassmembers class com.anrkit.engineeringcollegeprojects.YourJsInterface {
#    @android.webkit.JavascriptInterface <methods>;
# }

# Keep default constructors for all Views, which is required for inflation from XML.
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}
