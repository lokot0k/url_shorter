from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, email_validator


# форма для ссылки
class UrlForm(FlaskForm):
    url_input = StringField("url_input", validators=[DataRequired()])
    sub_btn = SubmitField("Сократить")
