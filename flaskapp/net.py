"""
Модуль для классификации изображений с использованием предобученной модели ResNet50
"""

import os
from PIL import Image
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.applications import ResNet50
import logging

# Инициализация логгера для записи информации о работе программы
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Загрузка предобученной модели ResNet50 (веса обучены на ImageNet)
model = ResNet50(weights='imagenet')


def read_image_files(files_max_count, dir_name):
    """
    Чтение и подготовка изображений из указанной директории.
    Возвращает количество успешно загруженных изображений и список объектов PIL.Image.
    """
    try:
        # Фильтрация файлов по допустимым расширениям (.png, .jpg, .jpeg)
        valid_extensions = ('.png', '.jpg', '.jpeg')
        files = [f for f in os.listdir(dir_name)
                 if f.lower().endswith(valid_extensions)][:files_max_count]

        images = []
        for file in files:
            try:
                img = Image.open(os.path.join(dir_name, file))
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                logger.warning(f"Пропуск файла {file}: {str(e)}")
                continue

        return len(images), images

    except Exception as e:
        logger.error(f"Ошибка при чтении изображений: {str(e)}")
        return 0, []


def preprocess_image(img):
    """Подготовка изображения к подаче в нейросеть: конвертация в RGB, ресайз, нормализация"""
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img = img.resize((224, 224))  # ResNet50 требует размер 224x224
    x = np.array(img, dtype=np.float32)
    return preprocess_input(np.expand_dims(x, axis=0))


def getresult(image_box):
    """
    Классификация изображений с помощью ResNet50.
    Возвращает список предсказаний в формате (class_id, class_name, confidence).
    """
    try:
        if not image_box:
            return []

        # Пакетная обработка изображений
        processed_images = np.vstack([preprocess_image(img) for img in image_box])

        if processed_images.shape[-1] != 3:
            raise ValueError(f"Ожидается 3 канала (RGB), получено {processed_images.shape[-1]}")

        # Получение и декодирование предсказаний
        preds = model.predict(processed_images)
        return decode_predictions(preds, top=1)  # Только лучший вариант классификации

    except Exception as e:
        logger.error(f"Ошибка классификации: {str(e)}", exc_info=True)
        return []