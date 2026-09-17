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
        if (inn) {
            if (window.copyToClipboard(inn)) {
                alert("ИНН " + inn + " скопирован в буфер обмена.");
            } else {
                alert("Не удалось скопировать ИНН автоматически.\nИНН: " + inn);
            }
        }

        if (/Android/i.test(navigator.userAgent)) {
            // Leaving for the app in the same turn as the copy discards what
            // was just put on the clipboard, so let that settle first.
            setTimeout(function () {
                window.location.href = ANDROID_URL;
            }, 150);
        } else {
            window.open(WEB_URL, "_blank", "noopener");
        }
    });
})();
