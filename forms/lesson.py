from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Content(FlaskForm):
    text = TextAreaField("Новый абзац")
    type = "text"


class Arr(FlaskForm):
    arr = []


class Image(FlaskForm):
    img = FileField("file", validators=[FileAllowed(['jpg','jpeg','png'])])
    img_name = ""
    type = "img"
