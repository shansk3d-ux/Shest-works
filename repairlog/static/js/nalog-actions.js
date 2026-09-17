(function () {
    "use strict";

    var WEB_URL = "https://lknpd.nalog.ru/";
    // Chrome for Android routes an intent: URL to the app that owns the
    // package and follows browser_fallback_url when it is not installed.
    var ANDROID_URL =
        "intent://lknpd.nalog.ru/#Intent;scheme=https;" +
        "package=com.gnivts.selfemployed;S.browser_fallback_url=" +
        encodeURIComponent(WEB_URL) +
        ";end";

    document.addEventListener("click", function (event) {
        var btn = event.target.closest(".nalog-btn");
        if (!btn) {
            return;
        }

        var inn = btn.dataset.inn;
        if (inn && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(inn).catch(function () {
                // Clipboard access can be blocked; the alert below still
                // shows the number, so there is nothing further to do.
            });
            alert("ИНН " + inn + " скопирован в буфер обмена.");
        }

        if (/Android/i.test(navigator.userAgent)) {
            window.location.href = ANDROID_URL;
        } else {
            window.open(WEB_URL, "_blank", "noopener");
        }
    });
})();
