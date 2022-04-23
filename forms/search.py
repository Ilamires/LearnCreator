from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class SearchForm(FlaskForm):
    search = StringField('Поиск')
    select = SubmitField('Поиск')
    further = SubmitField('Далее')
    back = SubmitField('Назад')
