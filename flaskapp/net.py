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
    """Читает изображения из директории с обработкой ошибок"""
    try:
        files = [f for f in os.listdir(dir_name)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:files_max_count]

        images = []
        for file in files:
            try:
                img_path = os.path.join(dir_name, file)
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            except Exception as e:
                logger.warning(f"Skipping {file}: {str(e)}")
                continue

        return len(images), images

    except Exception as e:
        logger.error(f"Error in read_image_files: {str(e)}")
        return 0, []


def getresult(image_box):
    """Классификация изображений с обработкой ошибок"""
    try:
        if not image_box:
            return []

        # Подготовка изображений
        processed_images = []
        for img in image_box:
            img = img.resize((224, 224))
            x = np.array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            processed_images.append(x)

        processed_images = np.vstack(processed_images)
        preds = model.predict(processed_images)
        return decode_predictions(preds, top=1)

    except Exception as e:
        logger.error(f"Error in getresult: {str(e)}", exc_info=True)
        return []