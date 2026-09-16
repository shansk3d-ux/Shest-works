(function () {
    "use strict";

    var dueUrl = window.TASKS_DUE_URL;
    if (!dueUrl) {
        return;
    }

    var POLL_INTERVAL_MS = 60000;

    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
    }

    function notifyTask(task) {
        if ("Notification" in window && Notification.permission === "granted") {
            var notification = new Notification(task.title, {
                body: task.description || "Наступило время задачи",
                tag: "repairlog-task-" + task.id,
            });
            notification.onclick = function () {
                window.focus();
                window.location.href = task.url;
            };
        }

        if (task.sound_url) {
            var audio = new Audio(task.sound_url);
            audio.play().catch(function () {
                // Autoplay can be blocked until the user interacts with the page; ignore.
            });
        }
    }

    function checkDueTasks() {
        fetch(dueUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(function (response) {
                return response.ok ? response.json() : { tasks: [] };
            })
            .then(function (data) {
                (data.tasks || []).forEach(notifyTask);
            })
            .catch(function () {
                // Network hiccup: try again on the next poll.
            });
    }

    checkDueTasks();
    setInterval(checkDueTasks, POLL_INTERVAL_MS);
})();
