from PIL import Image
import io

# Функция изменения размера изображения с сохранением пропорций
def resize_image(img_bytes, scale_percent):
    # Открытие изображения из байтов
    img = Image.open(io.BytesIO(img_bytes))

    # Расчет новых размеров
    width = int(img.width * scale_percent / 100)
    height = int(img.height * scale_percent / 100)

    # Масштабирование с высококачественной интерполяцией
    resized_img = img.resize((width, height), Image.LANCZOS)
    return resized_img