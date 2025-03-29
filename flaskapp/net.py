from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import os
from PIL import Image

# Загрузка предобученной модели ResNet50
model = ResNet50(weights='imagenet')


def read_image_files(files_max_count, dir_name):
    """Чтение изображений из указанной директории"""
    files = [f for f in os.listdir(dir_name)
             if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:files_max_count]
    images = []
    for file in files:
        img_path = os.path.join(dir_name, file)
        try:
            img = Image.open(img_path)
            images.append(img)
        except:
            continue
    return len(images), images


def getresult(image_box):
    try:
        images_resized = []
        for img in image_box:
            # Конвертируем RGBA в RGB, если нужно
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            img = img.resize((224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            images_resized.append(x)

        images_resized = np.vstack(images_resized)
        preds = model.predict(images_resized)
        return decode_predictions(preds, top=1)
    except Exception as e:
        print(f"Error in getresult: {str(e)}")
        return []