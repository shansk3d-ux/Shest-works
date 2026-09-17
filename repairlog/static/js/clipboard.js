(function () {
    "use strict";

    function legacyCopy(text) {
        var area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.top = "0";
        area.style.left = "0";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.focus();
        area.select();
        area.setSelectionRange(0, text.length);
        var copied = false;
        try {
            copied = document.execCommand("copy");
        } catch (error) {
            copied = false;
        }
        document.body.removeChild(area);
        return copied;
    }

    // navigator.clipboard exists only in a secure context, and this app is
    // normally served over plain HTTP on a bare IP, where it is undefined.
    // The deprecated selection copy still works there, but only while the
    // click that triggered it is still being handled — hence no awaiting.
    window.copyToClipboard = function (text) {
        if (window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).catch(function () {
                legacyCopy(text);
            });
            return true;
        }
        return legacyCopy(text);
    };
})();
