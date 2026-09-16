import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Idempotent one-shot setup for a throwaway public demo (e.g. a free-tier
    PaaS deploy with no shell access): seeds reference data and makes sure a
    known demo superuser exists, so the person deploying can log in right
    after the first build without running any commands by hand."""

    help = "Seeds reference data and ensures a demo superuser exists"

    def handle(self, *args, **options):
        call_command("seed")

        username = os.environ.get("DEMO_USERNAME", "demo")
        password = os.environ.get("DEMO_PASSWORD", "opyat-rabota-demo")

        user, created = User.objects.get_or_create(
            username=username, defaults={"is_staff": True, "is_superuser": True}
        )
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "Создан" if created else "Обновлён"
        self.stdout.write(self.style.SUCCESS(f"{action} демо-пользователь «{username}»."))
