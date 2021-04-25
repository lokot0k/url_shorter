from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, BooleanField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

# формы для входа и регистрации
class LoginForm(FlaskForm):
    login = StringField('Ваша почта или логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegForm(FlaskForm):
    login = StringField('Укажите желаемый логин', validators=[DataRequired()])
    password = PasswordField('Укажите пароль', validators=[DataRequired()])
    password_req = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
