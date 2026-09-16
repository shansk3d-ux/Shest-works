from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.tasks.models import Task

User = get_user_model()

DATETIME_LOCAL_FORMAT = "%Y-%m-%dT%H:%M"


class TaskViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)


class TaskListViewTests(TaskViewsTestCase):
    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("tasks:list"))
        self.assertEqual(response.status_code, 302)

    def test_active_filter_hides_done_and_cancelled(self):
        Task.objects.create(title="Новая", due_at=timezone.now(), owner=self.user)
        Task.objects.create(
            title="Завершённая",
            due_at=timezone.now(),
            owner=self.user,
            status=Task.Status.DONE,
        )
        response = self.client.get(reverse("tasks:list"))
        self.assertContains(response, "Новая")
        self.assertNotContains(response, "Завершённая")

    def test_status_filter_all_shows_everything(self):
        Task.objects.create(
            title="Отменённая",
            due_at=timezone.now(),
            owner=self.user,
            status=Task.Status.CANCELLED,
        )
        response = self.client.get(reverse("tasks:list"), {"status": "all"})
        self.assertContains(response, "Отменённая")

    def test_search_by_title(self):
        Task.objects.create(title="Позвонить клиенту", due_at=timezone.now(), owner=self.user)
        Task.objects.create(title="Заказать тэн", due_at=timezone.now(), owner=self.user)
        response = self.client.get(reverse("tasks:list"), {"q": "клиенту"})
        self.assertContains(response, "Позвонить клиенту")
        self.assertNotContains(response, "Заказать тэн")


class TaskDetailViewTests(TaskViewsTestCase):
    def test_shows_task_info(self):
        task = Task.objects.create(
            title="Проверить компрессор", due_at=timezone.now(), owner=self.user
        )
        response = self.client.get(reverse("tasks:detail", args=[task.pk]))
        self.assertContains(response, "Проверить компрессор")


class TaskCreateViewTests(TaskViewsTestCase):
    def test_creates_task_and_sets_owner(self):
        due_at = timezone.now() + timedelta(hours=2)
        response = self.client.post(
            reverse("tasks:create"),
            {
                "title": "Купить фильтр",
                "description": "",
                "due_at": due_at.strftime(DATETIME_LOCAL_FORMAT),
                "repair": "",
                "notify_sound": Task.NotifySound.DEFAULT,
            },
        )
        task = Task.objects.get(title="Купить фильтр")
        self.assertRedirects(response, reverse("tasks:detail", args=[task.pk]))
        self.assertEqual(task.owner, self.user)


class TaskActionViewTests(TaskViewsTestCase):
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            title="Забрать запчасть", due_at=timezone.now(), owner=self.user
        )

    def test_complete_sets_status_done(self):
        response = self.client.post(reverse("tasks:complete", args=[self.task.pk]))
        self.assertRedirects(response, reverse("tasks:detail", args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.DONE)

    def test_cancel_sets_status_cancelled(self):
        response = self.client.post(reverse("tasks:cancel", args=[self.task.pk]))
        self.assertRedirects(response, reverse("tasks:detail", args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.CANCELLED)

    def test_postpone_sets_postponed_until_and_status(self):
        self.task.notified_at = timezone.now()
        self.task.save(update_fields=["notified_at"])

        postpone_to = timezone.now() + timedelta(days=1)
        response = self.client.post(
            reverse("tasks:postpone", args=[self.task.pk]),
            {"postponed_until": postpone_to.strftime(DATETIME_LOCAL_FORMAT)},
        )
        self.assertRedirects(response, reverse("tasks:detail", args=[self.task.pk]))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.POSTPONED)
        self.assertIsNotNone(self.task.postponed_until)
        self.assertIsNone(self.task.notified_at)


class TaskDueNotificationsViewTests(TaskViewsTestCase):
    def test_returns_overdue_task_and_marks_notified(self):
        task = Task.objects.create(
            title="Просроченная задача",
            due_at=timezone.now() - timedelta(minutes=5),
            owner=self.user,
        )
        response = self.client.get(reverse("tasks:due"))
        data = response.json()
        self.assertEqual(len(data["tasks"]), 1)
        self.assertEqual(data["tasks"][0]["title"], "Просроченная задача")
        task.refresh_from_db()
        self.assertIsNotNone(task.notified_at)

    def test_does_not_return_future_task(self):
        Task.objects.create(
            title="Будущая задача",
            due_at=timezone.now() + timedelta(hours=1),
            owner=self.user,
        )
        response = self.client.get(reverse("tasks:due"))
        self.assertEqual(response.json()["tasks"], [])

    def test_does_not_return_already_notified_task(self):
        Task.objects.create(
            title="Уже уведомили",
            due_at=timezone.now() - timedelta(minutes=5),
            owner=self.user,
            notified_at=timezone.now(),
        )
        response = self.client.get(reverse("tasks:due"))
        self.assertEqual(response.json()["tasks"], [])

    def test_does_not_return_other_users_tasks(self):
        other_user = User.objects.create_user(username="other", password="pass12345")
        Task.objects.create(
            title="Чужая задача",
            due_at=timezone.now() - timedelta(minutes=5),
            owner=other_user,
        )
        response = self.client.get(reverse("tasks:due"))
        self.assertEqual(response.json()["tasks"], [])

    def test_includes_sound_url(self):
        Task.objects.create(
            title="Со звуком",
            due_at=timezone.now() - timedelta(minutes=5),
            owner=self.user,
            notify_sound=Task.NotifySound.BELL,
        )
        response = self.client.get(reverse("tasks:due"))
        self.assertIn("bell.wav", response.json()["tasks"][0]["sound_url"])
