(function () {
    "use strict";

    // Shows/hides a wrapper of extra fields depending on whether a <select>
    // (populated with existing catalog values plus a "__new__" sentinel
    // option) currently has that sentinel selected.
    function bindNewOptionToggle(selectId, wrapperId) {
        var select = document.getElementById(selectId);
        var wrapper = document.getElementById(wrapperId);
        if (!select || !wrapper) {
            return;
        }
        function sync() {
            wrapper.classList.toggle("d-none", select.value !== "__new__");
        }
        select.addEventListener("change", sync);
        sync();
    }

    window.bindNewOptionToggle = bindNewOptionToggle;
})();
