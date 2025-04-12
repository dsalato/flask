from PIL import Image
import io
import numpy as np


def resize_image(img_bytes, scale_percent):
    img = Image.open(io.BytesIO(img_bytes))

    width = int(img.width * scale_percent / 100)
    height = int(img.height * scale_percent / 100)

    resized_img = img.resize((width, height), Image.LANCZOS)
    return resized_img