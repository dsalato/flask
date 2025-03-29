from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return "<html><head></head><body>Hello World!</body></html>"

@app.route("/data_to")
def data_to():
    some_pars = {'user': 'Ivan', 'color': 'red'}
    some_str = 'Hello my dear friends!'
    some_value = 10
    return render_template('simple.html', some_str=some_str, some_value=some_value, some_pars=some_pars)

from flask import render_template
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
import os
import net as neuronet
import secrets

SECRET_KEY = secrets.token_hex(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcrggMrAAAAAE9vgK_pMkstxzHV4j8FtZSjtvNn'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcrggMrAAAAAMxYmQZrFUcDUHT61hH8EWYWTQfG'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'light'}

from flask_bootstrap import Bootstrap

bootstrap = Bootstrap(app)

os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)

class NetForm(FlaskForm):
    openid = StringField('Ваш идентификатор', validators=[DataRequired()])
    upload = FileField('Загрузите изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения!')
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Классифицировать')


@app.route("/net", methods=['GET', 'POST'])
def net():
    form = NetForm()
    filename = None
    neurodic = {}

    if form.validate_on_submit():
        # Сохраняем загруженный файл
        f = form.upload.data
        filename = secure_filename(f.filename)
        filepath = os.path.join(
            app.root_path,
            'static',
            'uploads',
            filename
        )
        f.save(filepath)

        # Классификация изображения
        _, images = neuronet.read_image_files(1, os.path.dirname(filepath))
        decode = neuronet.getresult(images)

        # Формируем результаты
        for elem in decode:
            neurodic[elem[0][1]] = f"{elem[0][2] * 100:.2f}%"

        # Относительный путь для HTML
        filename = f"uploads/{filename}"

    return render_template(
        'net.html',
        form=form,
        image_name=filename,
        neurodic=neurodic
    )


from flask import request, Response, jsonify
import base64
from PIL import Image
from io import BytesIO
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/apinet", methods=['POST'])
def apinet():
    """API endpoint для классификации изображений"""
    try:
        # Проверка Content-Type
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()

        # Валидация входных данных
        if 'imagebin' not in data or not isinstance(data['imagebin'], str):
            return jsonify({"error": "Invalid or missing 'imagebin' field"}), 400

        try:
            # Декодирование base64
            filebytes = data['imagebin'].encode('utf-8')
            cfile = base64.b64decode(filebytes)

            # Проверка размера изображения (макс. 5MB)
            if len(cfile) > 5 * 1024 * 1024:
                return jsonify({"error": "Image too large (max 5MB)"}), 400

            # Открытие изображения
            img = Image.open(BytesIO(cfile))

            # Проверка формата изображения
            if img.format not in ['JPEG', 'PNG']:
                return jsonify({"error": "Only JPEG and PNG images supported"}), 400

            # Классификация
            decode = neuronet.getresult([img])
            neurodic = {elem[0][1]: float(elem[0][2]) for elem in decode}

            logger.info(f"Classification result: {neurodic}")
            return jsonify(neurodic)

        except (base64.binascii.Error, OSError) as e:
            logger.error(f"Image processing error: {str(e)}")
            return jsonify({"error": "Invalid image data"}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

from flask import make_response
import lxml.etree as ET
import os

@app.route("/apixml", methods=['GET'])
def apixml():
    try:
        # Проверяем существование файлов
        xml_path = os.path.join(app.root_path, 'static', 'xml', 'file.xml')
        xslt_path = os.path.join(app.root_path, 'static', 'xml', 'file.xslt')

        if not os.path.exists(xml_path) or not os.path.exists(xslt_path):
            return "XML or XSLT file not found", 404

        # Парсинг и преобразование
        dom = ET.parse(xml_path)
        xslt = ET.parse(xslt_path)
        transform = ET.XSLT(xslt)
        result = transform(dom)

        # Создаем ответ с правильным MIME-типом
        response = make_response(ET.tostring(result, encoding='unicode'))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response

    except Exception as e:
        app.logger.error(f"Error in apixml: {str(e)}")
        return f"Error processing XML: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
