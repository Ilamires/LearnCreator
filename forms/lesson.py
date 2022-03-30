from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Content(FlaskForm):
    content = []


class Text(FlaskForm):
    text = TextAreaField("test")
