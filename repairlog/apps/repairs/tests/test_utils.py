from django.test import TestCase
from PIL import Image

from apps.repairs.utils import compress_image

from .helpers import make_uploaded_image


class CompressImageTests(TestCase):
    def test_resizes_large_image_to_max_dimension(self):
        uploaded = make_uploaded_image(3000, 1500)
        result = compress_image(uploaded)
        with Image.open(result) as image:
            self.assertLessEqual(max(image.size), 1600)

    def test_preserves_aspect_ratio(self):
        uploaded = make_uploaded_image(3200, 1600)
        result = compress_image(uploaded)
        with Image.open(result) as image:
            self.assertAlmostEqual(image.size[0] / image.size[1], 2.0, places=2)

    def test_keeps_small_image_size_unchanged(self):
        uploaded = make_uploaded_image(400, 300)
        result = compress_image(uploaded)
        with Image.open(result) as image:
            self.assertEqual(image.size, (400, 300))

    def test_output_is_jpeg(self):
        uploaded = make_uploaded_image(200, 200)
        result = compress_image(uploaded)
        with Image.open(result) as image:
            self.assertEqual(image.format, "JPEG")

    def test_output_name_has_jpg_extension(self):
        uploaded = make_uploaded_image(200, 200, name="my-photo")
        result = compress_image(uploaded)
        self.assertEqual(result.name, "my-photo.jpg")
