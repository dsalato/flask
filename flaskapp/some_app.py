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

from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdOMuYqAAAAAIT6jiKhsTfhqO0VnrUl6ISNT-MS'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdOMuYqAAAAAJPQiUn6YpIcgHPuxD9ImEc_2RI-'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
class NetForm(FlaskForm):
    openid = StringField('openid', validators = [DataRequired()])
    upload = FileField('Load image', validators=[
    FileRequired(),
    FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    recaptcha = RecaptchaField()
    submit = SubmitField('send')
from werkzeug.utils import secure_filename
import os
import net as neuronet
@app.route("/net",methods=['GET', 'POST'])
def net():
 form = NetForm()
 filename=None
 neurodic = {}
 if form.validate_on_submit():
    filename = os.path.join('./static', secure_filename(form.upload.data.filename))
 fcount, fimage = neuronet.read_image_files(10,'./static')
 decode = neuronet.getresult(fimage)
 for elem in decode:
    neurodic[elem[0][1]] = elem[0][2]
 form.upload.data.save(filename)
 return render_template('net.html',form=form,image_name=filename,neurodic=neurodic)

from flask import request
from flask import Response
import base64
from PIL import Image
from io import BytesIO
import json

@app.route("/apinet",methods=['GET', 'POST'])
def apinet():
    neurodic = {}
    if request.mimetype == 'application/json':
        data = request.get_json()
 # берем содержимое по ключу, где хранится файл
 # закодированный строкой base64
 # декодируем строку в массив байт, используя кодировку utf-8
 # первые 128 байт ascii и utf-8 совпадают, потому можно
        filebytes = data['imagebin'].encode('utf-8')
 # декодируем массив байт base64 в исходный файл изображение
        cfile = base64.b64decode(filebytes)
 # чтобы считать изображение как файл из памяти, используем BytesIO
        img = Image.open(BytesIO(cfile))
        decode = neuronet.getresult([img])
        neurodic = {}
        for elem in decode:
            neurodic[elem[0][1]] = str(elem[0][2])
            print(elem)
 # пример сохранения переданного файла
 # handle = open('./static/f.png','wb')
 # handle.write(cfile)
 # handle.close()
 # преобразуем словарь в json-строку
    ret = json.dumps(neurodic)
 # готовим ответ пользователю
    resp = Response(response=ret,
    status=200,
    mimetype="application/json")
 # возвращаем ответ
    return resp

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
