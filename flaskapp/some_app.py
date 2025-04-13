import os
import logging
import secrets
import base64
import io
from io import BytesIO

from flask import (
    Flask, render_template, flash, request,
    jsonify, make_response
)
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired, NumberRange
from PIL import Image
import lxml.etree as ET
from werkzeug.utils import secure_filename
from utils.image_processor import resize_image
from utils.color_analysis import plot_color_distribution

try:
    from . import net as neuronet
except ImportError:
    import net as neuronet

# Инициализация Flask приложения
app = Flask(__name__)

# ==============================================
# КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ
# ==============================================
app.config.update(
    # Секретный ключ для защиты от CSRF атак
    SECRET_KEY=secrets.token_hex(32),

    # Настройки reCAPTCHA
    RECAPTCHA_USE_SSL=False,
    RECAPTCHA_PUBLIC_KEY='6LcrggMrAAAAAE9vgK_pMkstxzHV4j8FtZSjtvNn',
    RECAPTCHA_PRIVATE_KEY='6LcrggMrAAAAAMxYmQZrFUcDUHT61hH8EWYWTQfG',
    RECAPTCHA_OPTIONS={'theme': 'light'},

    # Папка для загрузки изображений
    UPLOAD_FOLDER=os.path.join('static', 'uploads'),

    # Максимальный размер загружаемого файла (5MB)
    MAX_CONTENT_LENGTH=5 * 1024 * 1024
)

# Создаем папку для загрузок, если она не существует
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)

# Инициализация расширений
bootstrap = Bootstrap(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==============================================
# ФОРМЫ ДЛЯ РАБОТЫ С ИЗОБРАЖЕНИЯМИ
# ==============================================
class NetForm(FlaskForm):
    """
    Форма для загрузки изображения и классификации нейросетью
    """
    openid = StringField('Ваш идентификатор', validators=[DataRequired()])
    upload = FileField('Загрузите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Классифицировать')


class ResizeForm(FlaskForm):
    """
    Форма для изменения размера изображения и анализа цветов
    """
    image = FileField('Выберите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    scale = IntegerField('Процент масштаба', validators=[
        DataRequired(),
        NumberRange(min=1, max=500, message="Допустимый диапазон: 1-500%")
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Изменить')


# ==============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================
def process_uploaded_image(file):
    """
    Обрабатывает загруженное изображение:
    1. Проверяет имя файла на безопасность
    2. Конвертирует RGBA в RGB при необходимости
    3. Сохраняет изображение в папку загрузок

    Возвращает:
    - безопасное имя файла
    - полный путь к сохраненному файлу
    """
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)

    img = Image.open(file.stream)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img.save(save_path)

    return filename, save_path


def get_classification_results(image_path):
    """
    Получает результаты классификации изображения нейросетью

    Возвращает словарь с предсказаниями в формате:
    {'класс1': 'вероятность1%', 'класс2': 'вероятность2%'}
    """
    _, images = neuronet.read_image_files(1, os.path.dirname(image_path))
    decode = neuronet.getresult(images)
    return {elem[0][1]: f"{elem[0][2] * 100:.2f}%" for elem in decode}


# ==============================================
# ОСНОВНЫЕ МАРШРУТЫ ПРИЛОЖЕНИЯ
# ==============================================
@app.route("/", methods=['GET', 'POST'])
def resize_image_route():
    """
    Главная страница приложения с формой для изменения размера изображений.
    Также показывает анализ цветов оригинального и измененного изображения.
    """
    form = ResizeForm()

    if form.validate_on_submit():
        try:
            # Получаем данные из формы
            file = form.image.data
            scale = float(form.scale.data)
            img_bytes = file.read()

            # Изменяем размер изображения
            resized_img = resize_image(img_bytes, scale)

            # Создаем графики распределения цветов
            original_img = Image.open(io.BytesIO(img_bytes))
            original_plot = plot_color_distribution(original_img, "исходное")
            resized_plot = plot_color_distribution(resized_img, "измененное")

            # Конвертируем изображения в base64 для отображения в HTML
            buffered = io.BytesIO()
            resized_img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

            return render_template('resize.html',
                                   form=form,
                                   img_data=img_str,
                                   original_plot=base64.b64encode(original_plot.getvalue()).decode('utf-8'),
                                   resized_plot=base64.b64encode(resized_plot.getvalue()).decode('utf-8'),
                                   scale=scale)

        except Exception as e:
            logger.error(f"Ошибка при изменении размера изображения: {str(e)}")
            flash('Произошла ошибка при обработке изображения', 'danger')

    return render_template('resize.html', form=form)


@app.route("/net", methods=['GET', 'POST'])
def net():
    """
    Страница для классификации изображений нейросетью
    """
    form = NetForm()

    if form.validate_on_submit():
        try:
            # Обрабатываем загруженное изображение
            filename, save_path = process_uploaded_image(form.upload.data)

            # Получаем результаты классификации
            neurodic = get_classification_results(save_path)

            return render_template('net.html',
                                   form=form,
                                   image_name=f"uploads/{filename}",
                                   neurodic=neurodic)
        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {str(e)}")
            flash('Ошибка обработки изображения', 'danger')

    return render_template('net.html', form=form)


@app.route("/apinet", methods=['POST'])
def apinet():
    """
    API endpoint для классификации изображений.
    Принимает изображение в base64, возвращает JSON с результатами.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Запрос должен быть в формате JSON"}), 400

        data = request.get_json()

        if 'imagebin' not in data or not isinstance(data['imagebin'], str):
            return jsonify({"error": "Неверное или отсутствующее поле 'imagebin'"}), 400

        try:
            # Декодируем изображение из base64
            filebytes = data['imagebin'].encode('utf-8')
            cfile = base64.b64decode(filebytes)

            # Проверяем размер файла
            if len(cfile) > app.config['MAX_CONTENT_LENGTH']:
                return jsonify({"error": "Изображение слишком большое (максимум 5MB)"}), 400

            # Открываем изображение
            img = Image.open(BytesIO(cfile))

            # Проверяем формат
            if img.format not in ['JPEG', 'PNG']:
                return jsonify({"error": "Поддерживаются только JPEG и PNG изображения"}), 400

            # Получаем результаты классификации
            decode = neuronet.getresult([img])
            neurodic = {elem[0][1]: float(elem[0][2]) for elem in decode}

            logger.info(f"Результаты классификации: {neurodic}")
            return jsonify(neurodic)

        except (base64.binascii.Error, OSError) as e:
            logger.error(f"Ошибка обработки изображения: {str(e)}")
            return jsonify({"error": "Неверные данные изображения"}), 400

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route("/apixml", methods=['GET'])
def apixml():
    """
    Преобразует XML в HTML с помощью XSLT.
    Используется для демонстрации работы с XML.
    """
    try:
        xml_dir = os.path.join(app.root_path, 'static', 'xml')
        xml_path = os.path.join(xml_dir, 'file.xml')
        xslt_path = os.path.join(xml_dir, 'file.xslt')

        if not all(os.path.exists(p) for p in [xml_path, xslt_path]):
            return "XML или XSLT файл не найден", 404

        # Преобразуем XML с помощью XSLT
        dom = ET.parse(xml_path)
        xslt = ET.parse(xslt_path)
        transform = ET.XSLT(xslt)
        result = transform(dom)

        response = make_response(ET.tostring(result, encoding='unicode'))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response

    except Exception as e:
        logger.error(f"Ошибка в apixml: {str(e)}")
        return f"Ошибка обработки XML: {str(e)}", 500


@app.route("/hello")
def hello():
    """Простая тестовая страница"""
    return "<html><head></head><body>Hello World!</body></html>"


@app.route("/data_to")
def data_to():
    """Демонстрация передачи данных в шаблон"""
    template_data = {
        'some_str': 'Hello my dear friends!',
        'some_value': 10,
        'some_pars': {'user': 'Ivan', 'color': 'red'}
    }
    return render_template('simple.html', **template_data)


# Запуск приложения
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)