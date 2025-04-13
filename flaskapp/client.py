import os
import base64
import requests

# Кодирует изображение в base64 строку
def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        img_data = f.read()
        return base64.b64encode(img_data).decode('utf-8')

# Тестирует основной API классификации изображений
def test_api(image_path, api_url='http://localhost:5000/apinet'):
    try:
        b64_image = encode_image_to_base64(image_path)
        jsondata = {'imagebin': b64_image}

        response = requests.post(api_url, json=jsondata, timeout=10)

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

# Тестирует вспомогательное XML API
def test_xml_api():
    try:
        url = 'http://localhost:5000/apixml'
        r = requests.get(url, timeout=10)

        print(f"XML API Status: {r.status_code}")
        if r.status_code == 200:
            print("XML Transformation successful")
            print(r.text[:500])
        return r.status_code == 200
    except Exception as e:
        print(f"XML API Error: {str(e)}")
        return False

# Точка входа - запускает тесты обоих API
if __name__ == "__main__":
    image_path = os.path.join('static', 'image0008.png')

    test_results = [
        test_xml_api(),
        test_api(image_path)
    ]
    # Завершает с кодом 0 при успехе всех тестов, иначе 1
    exit_code = 0 if all(test_results) else 1
    exit(exit_code)
