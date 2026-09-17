(function () {
    "use strict";

    document.addEventListener("click", function (event) {
        var noPhoneBtn = event.target.closest(".no-phone-btn");
        if (noPhoneBtn) {
            alert("У клиента не указан номер телефона.");
            window.location.href = noPhoneBtn.dataset.editUrl + "#id_phone";
            return;
        }

        var maxBtn = event.target.closest(".write-max-btn");
        if (maxBtn) {
            var phone = maxBtn.dataset.phone;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(phone).catch(function () {
                    // Clipboard access can be blocked; the alert below still
                    // shows the number, so nothing further to do.
                });
            }
            // MAX has no public "open chat by phone number" link (unlike
            // wa.me) — copy the number and send the user to search for it.
            alert(
                "Номер " + phone + " скопирован в буфер обмена.\n" +
                "Вставьте его в поиск контактов в MAX — прямых ссылок по номеру телефона MAX не даёт."
            );
            window.open("https://max.ru/", "_blank", "noopener");
        }
    });
})();
