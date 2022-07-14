import io

from PIL import Image


def transform_image(image_bytes, size):
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail(size, Image.ANTIALIAS)
    return __image_to_byte_array(image)


def __image_to_byte_array(image: Image):
    byte_array = io.BytesIO()
    image.save(byte_array, format=image.format)
    byte_array = byte_array.getvalue()
    return byte_array
