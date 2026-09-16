from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_DIMENSION = 1600
JPEG_QUALITY = 85


def compress_image(uploaded_file):
    """Downscales an uploaded photo to at most MAX_DIMENSION px and re-encodes it as JPEG."""
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    buffer.seek(0)

    original_name = getattr(uploaded_file, "name", "photo")
    base_name = original_name.rsplit(".", 1)[0]
    return ContentFile(buffer.read(), name=f"{base_name}.jpg")
