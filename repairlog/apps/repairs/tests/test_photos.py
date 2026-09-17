from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.clients.models import Client
from apps.equipment.models import Brand, Equipment, EquipmentType
from apps.repairs.models import Repair, RepairPhoto

from .helpers import make_uploaded_image

User = get_user_model()


class RepairPhotoViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)
        client_obj = Client.objects.create(name="Ресторан Восток")
        equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        brand = Brand.objects.create(name="Rational")
        equipment = Equipment.objects.create(
            client=client_obj, equipment_type=equipment_type, brand=brand, model="SCC 61"
        )
        self.repair = Repair.objects.create(
            equipment=equipment,
            master=self.user,
            reported_at=timezone.localdate(),
            symptom="Течёт вода",
        )


class RepairPhotoUploadViewTests(RepairPhotoViewsTestCase):
    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("repairs:photo_upload", args=[self.repair.pk]))
        self.assertEqual(response.status_code, 302)

    def test_uploads_multiple_photos(self):
        images = [
            make_uploaded_image(2000, 1000, name="a"),
            make_uploaded_image(800, 600, name="b"),
        ]
        response = self.client.post(
            reverse("repairs:photo_upload", args=[self.repair.pk]),
            {"stage": RepairPhoto.Stage.BEFORE, "caption": "До ремонта", "images": images},
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        self.assertEqual(self.repair.photos.count(), 2)
        photo = self.repair.photos.first()
        self.assertEqual(photo.stage, RepairPhoto.Stage.BEFORE)
        self.assertEqual(photo.caption, "До ремонта")

    def test_compresses_uploaded_photo(self):
        image = make_uploaded_image(3000, 2000)
        self.client.post(
            reverse("repairs:photo_upload", args=[self.repair.pk]),
            {"stage": RepairPhoto.Stage.AFTER, "caption": "", "images": [image]},
        )
        photo = self.repair.photos.get()
        with Image.open(photo.image) as img:
            self.assertLessEqual(max(img.size), 1600)

    def test_invalid_form_creates_no_photos(self):
        response = self.client.post(
            reverse("repairs:photo_upload", args=[self.repair.pk]),
            {"stage": "not-a-real-stage", "caption": ""},
        )
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        self.assertEqual(self.repair.photos.count(), 0)


class RepairPhotoDeleteViewTests(RepairPhotoViewsTestCase):
    def setUp(self):
        super().setUp()
        image = make_uploaded_image(400, 300)
        self.client.post(
            reverse("repairs:photo_upload", args=[self.repair.pk]),
            {"stage": RepairPhoto.Stage.DURING, "caption": "", "images": [image]},
        )
        self.photo = self.repair.photos.get()

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("repairs:photo_delete", args=[self.photo.pk]))
        self.assertEqual(response.status_code, 302)

    def test_deletes_photo(self):
        response = self.client.post(reverse("repairs:photo_delete", args=[self.photo.pk]))
        self.assertRedirects(response, reverse("repairs:detail", args=[self.repair.pk]))
        self.assertFalse(RepairPhoto.objects.filter(pk=self.photo.pk).exists())
