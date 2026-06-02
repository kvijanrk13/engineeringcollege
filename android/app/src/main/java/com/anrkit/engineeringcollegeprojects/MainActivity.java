package com.anrkit.engineeringcollegeprojects;

import android.app.Activity;
import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.view.InputDevice;
import android.view.MotionEvent;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

public class MainActivity extends Activity {
    private static final int FILE_CHOOSER_REQUEST_CODE = 1001;
    private static final String AUTH_DEEP_LINK_SCHEME = "engineeringcollegeprojects";
    private static final int MOUSE_WHEEL_SCROLL_MULTIPLIER = 120;

    private WebView webView;
    private ProgressBar progressBar;
    private TextView offlineView;
    private View homeView;
    private View homeButton;
    private View projectsView;
    private ValueCallback<Uri[]> filePathCallback;
    private boolean mainPageLoadFailed;
    private String currentPath = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        offlineView = findViewById(R.id.offlineView);
        homeView = findViewById(R.id.homeView);
        homeButton = findViewById(R.id.homeButton);
        projectsView = findViewById(R.id.projectsView);

        offlineView.setOnClickListener(view -> reloadWebApp());
        homeButton.setOnClickListener(view -> showHome());
        findViewById(R.id.projectsBackButton).setOnClickListener(view -> showHome());
        configureWebView();
        configureSectionTiles();
        configureProjectDomainTiles();

        if (!handleIncomingIntent(getIntent())) {
            showHome();
        }
    }

    private void configureSectionTiles() {
        findViewById(R.id.facultyTile).setOnClickListener(view -> openSection("faculty/list/"));
        findViewById(R.id.studentTile).setOnClickListener(view -> openSection("students/data/password/"));
        findViewById(R.id.examBranchTile).setOnClickListener(view -> openSection("exam-branch/"));
        findViewById(R.id.dashboardTile).setOnClickListener(view -> openSection("mobile-dashboard/"));
        findViewById(R.id.galleryTile).setOnClickListener(view -> openSection("gallery/"));
        findViewById(R.id.subjectsTile).setOnClickListener(view -> openSection("syllabus/"));
        findViewById(R.id.projectsTile).setOnClickListener(view -> showProjects());
    }

    private void configureProjectDomainTiles() {
        attachDomainToast(R.id.aiDomainTile, R.string.ai_domain);
        attachDomainToast(R.id.mlDomainTile, R.string.machine_learning_domain);
        attachDomainToast(R.id.softwareDomainTile, R.string.software_engineering_domain);
        attachDomainToast(R.id.securityDomainTile, R.string.security_domain);
        attachDomainToast(R.id.deepLearningDomainTile, R.string.deep_learning_domain);
        attachDomainToast(R.id.dataScienceDomainTile, R.string.data_science_domain);
        attachDomainToast(R.id.cloudDomainTile, R.string.cloud_computing_domain);
        attachDomainToast(R.id.iotDomainTile, R.string.iot_edge_domain);
    }

    private void attachDomainToast(int tileId, int labelId) {
        findViewById(tileId).setOnClickListener(view ->
                Toast.makeText(this, getString(labelId), Toast.LENGTH_SHORT).show()
        );
    }

    private void configureWebView() {
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);

        webView.setVerticalScrollBarEnabled(true);
        webView.setHorizontalScrollBarEnabled(true);
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
        webView.setOnGenericMotionListener((view, event) -> {
            if ((event.getSource() & InputDevice.SOURCE_CLASS_POINTER) == 0
                    || event.getAction() != MotionEvent.ACTION_SCROLL) {
                return false;
            }

            float verticalScroll = event.getAxisValue(MotionEvent.AXIS_VSCROLL);
            float horizontalScroll = event.getAxisValue(MotionEvent.AXIS_HSCROLL);
            if (verticalScroll == 0 && horizontalScroll == 0) {
                return false;
            }

            webView.scrollBy(
                    Math.round(-horizontalScroll * MOUSE_WHEEL_SCROLL_MULTIPLIER),
                    Math.round(-verticalScroll * MOUSE_WHEEL_SCROLL_MULTIPLIER)
            );
            return true;
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String scheme = uri.getScheme();

                if ("http".equals(scheme) || "https".equals(scheme)) {
                    if (isGoogleLoginStart(uri)) {
                        openGoogleLoginInBrowser(uri);
                        return true;
                    }
                    progressBar.setVisibility(View.VISIBLE);
                    return false;
                }

                if (AUTH_DEEP_LINK_SCHEME.equals(scheme)) {
                    handleAuthDeepLink(uri);
                    return true;
                }

                startActivity(new Intent(Intent.ACTION_VIEW, uri));
                return true;
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                if (currentPath == null || currentPath.isEmpty()) {
                    showHome();
                    return;
                }
                mainPageLoadFailed = false;
                offlineView.setVisibility(View.GONE);
                homeView.setVisibility(View.GONE);
                homeButton.setVisibility(View.VISIBLE);
                webView.setVisibility(View.VISIBLE);
                progressBar.setVisibility(View.VISIBLE);
            }

            @Override
            public void onReceivedError(
                    WebView view,
                    WebResourceRequest request,
                    WebResourceError error
            ) {
                if (request.isForMainFrame()) {
                    mainPageLoadFailed = true;
                    showOfflineMessage();
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                if (currentPath == null || currentPath.isEmpty()) {
                    showHome();
                    return;
                }
                progressBar.setVisibility(View.GONE);
                if (!mainPageLoadFailed) {
                    offlineView.setVisibility(View.GONE);
                    homeView.setVisibility(View.GONE);
                    homeButton.setVisibility(View.VISIBLE);
                    webView.setVisibility(View.VISIBLE);
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setVisibility(newProgress < 100 ? View.VISIBLE : View.GONE);
                progressBar.setProgress(newProgress);
            }

            @Override
            public boolean onShowFileChooser(
                    WebView webView,
                    ValueCallback<Uri[]> filePathCallback,
                    FileChooserParams fileChooserParams
            ) {
                if (MainActivity.this.filePathCallback != null) {
                    MainActivity.this.filePathCallback.onReceiveValue(null);
                }

                MainActivity.this.filePathCallback = filePathCallback;
                Intent intent = fileChooserParams.createIntent();
                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST_CODE);
                } catch (Exception exception) {
                    MainActivity.this.filePathCallback = null;
                    Toast.makeText(MainActivity.this, R.string.file_picker_error, Toast.LENGTH_SHORT).show();
                    return false;
                }
                return true;
            }
        });

        webView.setDownloadListener(createDownloadListener());
    }

    private DownloadListener createDownloadListener() {
        return (url, userAgent, contentDisposition, mimeType, contentLength) -> {
            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
            String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
            String cookies = CookieManager.getInstance().getCookie(url);

            if (mimeType != null && !mimeType.isEmpty()) {
                request.setMimeType(mimeType);
            }
            if (userAgent != null && !userAgent.isEmpty()) {
                request.addRequestHeader("User-Agent", userAgent);
            }
            if (cookies != null && !cookies.isEmpty()) {
                request.addRequestHeader("Cookie", cookies);
            }
            request.setTitle(fileName);
            request.setDescription(getString(R.string.download_description));
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);

            DownloadManager downloadManager = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
            if (downloadManager != null) {
                downloadManager.enqueue(request);
                Toast.makeText(this, R.string.download_started, Toast.LENGTH_SHORT).show();
            }
        };
    }

    private boolean isOnline() {
        ConnectivityManager connectivityManager =
                (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);

        if (connectivityManager == null || connectivityManager.getActiveNetwork() == null) {
            return false;
        }

        NetworkCapabilities capabilities =
                connectivityManager.getNetworkCapabilities(connectivityManager.getActiveNetwork());

        return capabilities != null
                && capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
    }

    private void showOfflineMessage() {
        progressBar.setVisibility(View.GONE);
        homeView.setVisibility(View.GONE);
        projectsView.setVisibility(View.GONE);
        homeButton.setVisibility(View.GONE);
        webView.setVisibility(View.GONE);
        offlineView.setVisibility(View.VISIBLE);
    }

    private void showHome() {
        currentPath = "";
        progressBar.setVisibility(View.GONE);
        offlineView.setVisibility(View.GONE);
        webView.setVisibility(View.GONE);
        homeButton.setVisibility(View.GONE);
        projectsView.setVisibility(View.GONE);
        homeView.setVisibility(View.VISIBLE);
    }

    private void showProjects() {
        currentPath = "";
        progressBar.setVisibility(View.GONE);
        offlineView.setVisibility(View.GONE);
        webView.setVisibility(View.GONE);
        homeButton.setVisibility(View.GONE);
        homeView.setVisibility(View.GONE);
        projectsView.setVisibility(View.VISIBLE);
    }

    private void openSection(String path) {
        currentPath = path;
        if (isOnline()) {
            progressBar.setVisibility(View.VISIBLE);
            offlineView.setVisibility(View.GONE);
            homeView.setVisibility(View.GONE);
            projectsView.setVisibility(View.GONE);
            homeButton.setVisibility(View.VISIBLE);
            webView.setVisibility(View.VISIBLE);
            webView.loadUrl(BuildConfig.WEB_APP_URL + path);
        } else {
            showOfflineMessage();
        }
    }

    private void reloadWebApp() {
        if (currentPath == null || currentPath.isEmpty()) {
            showHome();
            return;
        }
        openSection(currentPath);
    }

    private boolean handleIncomingIntent(Intent intent) {
        if (intent == null || intent.getData() == null) {
            return false;
        }

        Uri uri = intent.getData();
        if (AUTH_DEEP_LINK_SCHEME.equals(uri.getScheme())) {
            handleAuthDeepLink(uri);
            return true;
        }

        return false;
    }

    private boolean isGoogleLoginStart(Uri uri) {
        String host = uri.getHost();
        String path = uri.getPath();
        return host != null
                && host.equals(Uri.parse(BuildConfig.WEB_APP_URL).getHost())
                && "/google/login/".equals(path);
    }

    private void openGoogleLoginInBrowser(Uri uri) {
        Uri.Builder builder = uri.buildUpon();
        if (uri.getQueryParameter("mobile") == null) {
            builder.appendQueryParameter("mobile", "1");
        }
        startActivity(new Intent(Intent.ACTION_VIEW, builder.build()));
    }

    private void handleAuthDeepLink(Uri uri) {
        String token = uri.getQueryParameter("token");
        if (token == null || token.isEmpty()) {
            Toast.makeText(this, R.string.google_signin_error, Toast.LENGTH_SHORT).show();
            reloadWebApp();
            return;
        }

        try {
            String encodedToken = URLEncoder.encode(token, "UTF-8");
            currentPath = "google/mobile-complete/";
            homeView.setVisibility(View.GONE);
            projectsView.setVisibility(View.GONE);
            homeButton.setVisibility(View.VISIBLE);
            webView.setVisibility(View.VISIBLE);
            webView.loadUrl(BuildConfig.WEB_APP_URL + "google/mobile-complete/?token=" + encodedToken);
        } catch (UnsupportedEncodingException exception) {
            Toast.makeText(this, R.string.google_signin_error, Toast.LENGTH_SHORT).show();
            reloadWebApp();
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        if (!handleIncomingIntent(intent)) {
            showHome();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode != FILE_CHOOSER_REQUEST_CODE || filePathCallback == null) {
            return;
        }

        Uri[] results = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
        filePathCallback.onReceiveValue(results);
        filePathCallback = null;
    }

    @Override
    public void onBackPressed() {
        if (homeView.getVisibility() == View.VISIBLE) {
            super.onBackPressed();
            return;
        }
        if (projectsView.getVisibility() == View.VISIBLE) {
            showHome();
            return;
        }
        if (currentPath != null && !currentPath.isEmpty()) {
            showHome();
            return;
        }
        showHome();
    }
}
