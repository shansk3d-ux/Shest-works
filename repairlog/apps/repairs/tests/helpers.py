from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def make_uploaded_image(width, height, fmt="PNG", name="photo"):
    buffer = BytesIO()
    Image.new("RGB", (width, height), color=(200, 50, 50)).save(buffer, format=fmt)
    buffer.seek(0)
    return SimpleUploadedFile(
        f"{name}.{fmt.lower()}", buffer.read(), content_type=f"image/{fmt.lower()}"
    )
