import os
from PIL import Image
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.applications import ResNet50
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = ResNet50(weights='imagenet')


def read_image_files(files_max_count, dir_name):
    """Чтение изображений с проверкой формата"""
    try:
        valid_extensions = ('.png', '.jpg', '.jpeg')
        files = [f for f in os.listdir(dir_name)
                 if f.lower().endswith(valid_extensions)][:files_max_count]

        images = []
        for file in files:
            try:
                img_path = os.path.join(dir_name, file)
                img = Image.open(img_path)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                logger.warning(f"Skipping {file}: {str(e)}")
                continue

        return len(images), images

    except Exception as e:
        logger.error(f"Error reading images: {str(e)}")
        return 0, []


def preprocess_image(img):
    """Конвертирует и подготавливает изображение для модели"""
    # Конвертируем RGBA в RGB, если нужно
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img = img.resize((224, 224))
    x = np.array(img, dtype=np.float32)
    x = np.expand_dims(x, axis=0)
    return preprocess_input(x)


def getresult(image_box):
    """Классификация изображений"""
    try:
        if not image_box:
            return []

        # Обработка всех изображений
        processed_images = [preprocess_image(img) for img in image_box]
        processed_images = np.vstack(processed_images)

        # Проверка размерности
        if processed_images.shape[-1] != 3:
            raise ValueError(f"Expected 3 channels, got {processed_images.shape[-1]}")

        preds = model.predict(processed_images)
        return decode_predictions(preds, top=1)

    except Exception as e:
        logger.error(f"Error in getresult: {str(e)}", exc_info=True)
        return []