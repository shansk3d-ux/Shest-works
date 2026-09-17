from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.tasks.models import Task

User = get_user_model()


class TaskModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="master", password="pass12345")

    def test_default_status_is_new(self):
        task = Task.objects.create(
            title="Позвонить клиенту", due_at=timezone.now(), owner=self.owner
        )
        self.assertEqual(task.status, Task.Status.NEW)

    def test_effective_due_at_uses_due_at_without_postpone(self):
        due_at = timezone.now() + timedelta(hours=1)
        task = Task.objects.create(title="Проверить заявку", due_at=due_at, owner=self.owner)
        self.assertEqual(task.effective_due_at, due_at)

    def test_effective_due_at_uses_postponed_until_when_set(self):
        due_at = timezone.now()
        postponed_until = due_at + timedelta(days=1)
        task = Task.objects.create(
            title="Забрать запчасть",
            due_at=due_at,
            postponed_until=postponed_until,
            owner=self.owner,
        )
        self.assertEqual(task.effective_due_at, postponed_until)

    def test_is_overdue_true_for_past_new_task(self):
        task = Task.objects.create(
            title="Просроченная",
            due_at=timezone.now() - timedelta(hours=1),
            owner=self.owner,
        )
        self.assertTrue(task.is_overdue)

    def test_is_overdue_false_for_future_task(self):
        task = Task.objects.create(
            title="Будущая",
            due_at=timezone.now() + timedelta(hours=1),
            owner=self.owner,
        )
        self.assertFalse(task.is_overdue)

    def test_is_overdue_false_for_done_task(self):
        task = Task.objects.create(
            title="Завершённая",
            due_at=timezone.now() - timedelta(hours=1),
            owner=self.owner,
            status=Task.Status.DONE,
        )
        self.assertFalse(task.is_overdue)

    def test_str_returns_title(self):
        task = Task.objects.create(title="Купить тэн", due_at=timezone.now(), owner=self.owner)
        self.assertEqual(str(task), "Купить тэн")
