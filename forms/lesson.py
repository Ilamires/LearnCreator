from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Content(FlaskForm):
    text = TextAreaField("Новый абзац")
    type = "text"


class Arr(FlaskForm):
    arr = []


class Image_c(FlaskForm):
    img = FileField("file", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    img_name = ""
    type = "img"
