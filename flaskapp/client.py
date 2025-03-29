import os
import base64
import requests
from PIL import Image
from io import BytesIO


def encode_image_to_base64(image_path):
    """Кодирует изображение в base64"""
    with open(image_path, 'rb') as f:
        img_data = f.read()
        return base64.b64encode(img_data).decode('utf-8')


def test_api(image_path, api_url='http://localhost:5000/apinet'):
    """Тестирует API классификации"""
    try:
        # Подготовка данных
        b64_image = encode_image_to_base64(image_path)
        jsondata = {'imagebin': b64_image}

        # Отправка запроса
        response = requests.post(api_url, json=jsondata, timeout=10)

        # Обработка ответа
        if response.ok:
            result = response.json()
            print("Успешный ответ:")
            for class_name, probability in result.items():
                print(f"{class_name}: {probability:.4f}")
            return result
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {str(e)}")
        return None


if __name__ == "__main__":
    # Пример использования
    image_path = os.path.join('static', 'image0008.png')
    test_api(image_path)