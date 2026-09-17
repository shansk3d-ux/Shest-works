from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.clients.models import Client
from apps.equipment.models import Brand, Equipment, EquipmentType

User = get_user_model()


class EquipmentViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="master", password="pass12345")
        self.client.force_login(self.user)
        self.client_obj = Client.objects.create(name="Ресторан Восток")
        self.equipment_type = EquipmentType.objects.create(
            name="Пароконвектомат", category=EquipmentType.Category.KITCHEN
        )
        self.brand = Brand.objects.create(name="Rational")
        self.equipment = Equipment.objects.create(
            client=self.client_obj,
            equipment_type=self.equipment_type,
            brand=self.brand,
            model="SCC 61",
            serial_number="SN-001",
        )


class EquipmentListViewTests(EquipmentViewsTestCase):
    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("equipment:list"))
        self.assertEqual(response.status_code, 302)

    def test_lists_active_equipment_by_default(self):
        response = self.client.get(reverse("equipment:list"))
        self.assertContains(response, "SCC 61")

    def test_archived_equipment_hidden_by_default(self):
        self.equipment.is_archived = True
        self.equipment.save(update_fields=["is_archived"])
        response = self.client.get(reverse("equipment:list"))
        self.assertNotContains(response, "SCC 61")

    def test_archived_equipment_shown_with_filter(self):
        self.equipment.is_archived = True
        self.equipment.save(update_fields=["is_archived"])
        response = self.client.get(reverse("equipment:list"), {"archived": "1"})
        self.assertContains(response, "SCC 61")

    def test_search_by_serial_number(self):
        Equipment.objects.create(
            client=self.client_obj,
            equipment_type=self.equipment_type,
            brand=self.brand,
            model="Other",
            serial_number="ZZZ",
        )
        response = self.client.get(reverse("equipment:list"), {"q": "SN-001"})
        self.assertContains(response, "SCC 61")
        self.assertNotContains(response, "Other")

    def test_filter_by_brand(self):
        other_brand = Brand.objects.create(name="Unox")
        Equipment.objects.create(
            client=self.client_obj,
            equipment_type=self.equipment_type,
            brand=other_brand,
            model="XVC",
        )
        response = self.client.get(reverse("equipment:list"), {"brand": self.brand.pk})
        self.assertContains(response, "SCC 61")
        self.assertNotContains(response, "XVC")


class EquipmentDetailViewTests(EquipmentViewsTestCase):
    def test_shows_equipment_info(self):
        response = self.client.get(reverse("equipment:detail", args=[self.equipment.pk]))
        self.assertContains(response, "SCC 61")
        self.assertContains(response, "SN-001")


class EquipmentCreateViewTests(EquipmentViewsTestCase):
    def test_creates_equipment_and_redirects_to_detail(self):
        response = self.client.post(
            reverse("equipment:create"),
            {
                "client": self.client_obj.pk,
                "equipment_type": self.equipment_type.name,
                "brand": self.brand.name,
                "model": "SCC 101",
            },
        )
        equipment = Equipment.objects.get(model="SCC 101")
        self.assertRedirects(response, reverse("equipment:detail", args=[equipment.pk]))
        self.assertEqual(equipment.equipment_type, self.equipment_type)
        self.assertEqual(equipment.brand, self.brand)

    def test_client_prefilled_from_query_param(self):
        response = self.client.get(reverse("equipment:create"), {"client": self.client_obj.pk})
        self.assertEqual(response.context["form"].initial["client"], str(self.client_obj.pk))

    def test_picking_new_option_and_typing_a_name_creates_and_keeps_it(self):
        response = self.client.post(
            reverse("equipment:create"),
            {
                "client": self.client_obj.pk,
                "equipment_type": "__new__",
                "equipment_type_new_name": "Слайсер",
                "equipment_type_category": EquipmentType.Category.KITCHEN,
                "brand": "__new__",
                "brand_new_name": "Berkel",
                "model": "330M",
            },
        )
        equipment = Equipment.objects.get(model="330M")
        self.assertRedirects(response, reverse("equipment:detail", args=[equipment.pk]))
        self.assertEqual(equipment.equipment_type.name, "Слайсер")
        self.assertEqual(equipment.equipment_type.category, EquipmentType.Category.KITCHEN)
        self.assertEqual(equipment.brand.name, "Berkel")
        # It's now a real catalog entry, not just attached to this one piece of equipment.
        self.assertTrue(EquipmentType.objects.filter(name="Слайсер").exists())
        self.assertTrue(Brand.objects.filter(name="Berkel").exists())

    def test_new_brand_name_reuses_an_existing_one_case_insensitively(self):
        # Latin names here: SQLite's UPPER()/LOWER() (unlike Postgres's) only
        # case-folds ASCII, so a Cyrillic case-insensitive match would only
        # work against the real Postgres used in production.
        response = self.client.post(
            reverse("equipment:create"),
            {
                "client": self.client_obj.pk,
                "equipment_type": self.equipment_type.name,
                "brand": "__new__",
                "brand_new_name": self.brand.name.upper(),
                "model": "SCC 102",
            },
        )
        equipment = Equipment.objects.get(model="SCC 102")
        self.assertRedirects(response, reverse("equipment:detail", args=[equipment.pk]))
        self.assertEqual(equipment.equipment_type, self.equipment_type)
        self.assertEqual(equipment.brand, self.brand)
        matching = Brand.objects.filter(name__iexact=self.brand.name)
        self.assertEqual(matching.count(), 1)

    def test_new_type_without_category_is_rejected(self):
        response = self.client.post(
            reverse("equipment:create"),
            {
                "client": self.client_obj.pk,
                "equipment_type": "__new__",
                "equipment_type_new_name": "Слайсер",
                "brand": self.brand.name,
                "model": "330M",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Equipment.objects.filter(model="330M").exists())
        self.assertFalse(EquipmentType.objects.filter(name="Слайсер").exists())

    def test_new_type_without_name_is_rejected(self):
        response = self.client.post(
            reverse("equipment:create"),
            {
                "client": self.client_obj.pk,
                "equipment_type": "__new__",
                "equipment_type_category": EquipmentType.Category.KITCHEN,
                "brand": self.brand.name,
                "model": "330M",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Equipment.objects.filter(model="330M").exists())

    def test_form_uses_native_select_not_datalist(self):
        response = self.client.get(reverse("equipment:create"))
        self.assertNotContains(response, "<datalist")
        self.assertContains(response, "+ Новый тип оборудования")
        self.assertContains(response, "+ Новый бренд")


class EquipmentArchiveViewTests(EquipmentViewsTestCase):
    def test_archive_requires_confirmation_page(self):
        response = self.client.get(reverse("equipment:archive", args=[self.equipment.pk]))
        self.assertEqual(response.status_code, 200)
        self.equipment.refresh_from_db()
        self.assertFalse(self.equipment.is_archived)

    def test_archive_post_soft_deletes(self):
        response = self.client.post(reverse("equipment:archive", args=[self.equipment.pk]))
        self.assertRedirects(response, reverse("equipment:detail", args=[self.equipment.pk]))
        self.equipment.refresh_from_db()
        self.assertTrue(self.equipment.is_archived)

    def test_restore_clears_archived_flag(self):
        self.equipment.is_archived = True
        self.equipment.save(update_fields=["is_archived"])
        response = self.client.post(reverse("equipment:restore", args=[self.equipment.pk]))
        self.assertRedirects(response, reverse("equipment:detail", args=[self.equipment.pk]))
        self.equipment.refresh_from_db()
        self.assertFalse(self.equipment.is_archived)


class EquipmentFormFieldOrderTests(EquipmentViewsTestCase):
    def test_brand_field_comes_before_equipment_type_field(self):
        response = self.client.get(reverse("equipment:create"))
        content = response.content.decode()
        self.assertLess(content.index("id_brand"), content.index("id_equipment_type"))


class EquipmentTypeSuggestionsViewTests(EquipmentViewsTestCase):
    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("equipment:type_suggestions"))
        self.assertEqual(response.status_code, 302)

    def test_groups_types_seen_with_the_given_brand_first(self):
        other_type = EquipmentType.objects.create(
            name="Тестомес", category=EquipmentType.Category.KITCHEN
        )
        response = self.client.get(
            reverse("equipment:type_suggestions"), {"brand": self.brand.name}
        )
        content = response.content.decode()
        self.assertIn("Характерно для Rational", content)
        self.assertIn(self.equipment_type.name, content)
        self.assertIn(other_type.name, content)
        # The characteristic type should be listed before the unrelated one.
        self.assertLess(
            content.index(self.equipment_type.name), content.index(other_type.name)
        )

    def test_suggests_seeded_typical_types_even_without_equipment_history(self):
        # A fresh brand with no Equipment rows yet, but with a pre-seeded
        # typical_equipment_types link — suggestions should still work.
        fresh_brand = Brand.objects.create(name="Convotherm")
        combi = EquipmentType.objects.create(
            name="Пароконвектомат-новый", category=EquipmentType.Category.KITCHEN
        )
        fresh_brand.typical_equipment_types.add(combi)

        response = self.client.get(
            reverse("equipment:type_suggestions"), {"brand": fresh_brand.name}
        )
        content = response.content.decode()
        self.assertIn("Характерно для Convotherm", content)
        self.assertIn(combi.name, content)

    def test_unknown_brand_returns_flat_list_without_grouping(self):
        response = self.client.get(
            reverse("equipment:type_suggestions"), {"brand": "Совсем новый бренд"}
        )
        content = response.content.decode()
        self.assertNotIn("Характерно для", content)
        self.assertIn(self.equipment_type.name, content)

    def test_new_brand_sentinel_returns_flat_list(self):
        response = self.client.get(
            reverse("equipment:type_suggestions"), {"brand": "__new__"}
        )
        content = response.content.decode()
        self.assertNotIn("Характерно для", content)

    def test_marks_the_currently_selected_type_as_selected(self):
        response = self.client.get(
            reverse("equipment:type_suggestions"),
            {"brand": self.brand.name, "equipment_type": self.equipment_type.name},
        )
        content = response.content.decode()
        self.assertIn(f'value="{self.equipment_type.name}" selected', content)

    def test_jumps_to_top_suggestion_when_previous_type_is_unrelated_to_brand(self):
        unrelated_type = EquipmentType.objects.create(
            name="Аппарат", category=EquipmentType.Category.HOUSEHOLD
        )
        response = self.client.get(
            reverse("equipment:type_suggestions"),
            {"brand": self.brand.name, "equipment_type": unrelated_type.name},
        )
        content = response.content.decode()
        self.assertIn(f'value="{self.equipment_type.name}" selected', content)
        self.assertNotIn(f'value="{unrelated_type.name}" selected', content)

    def test_always_includes_the_new_type_option(self):
        response = self.client.get(reverse("equipment:type_suggestions"))
        self.assertContains(response, "+ Новый тип оборудования")
