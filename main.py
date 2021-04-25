from flask import Flask, render_template, redirect, jsonify, make_response
from flask import session
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
import data.api
from data.user import User
from data import db_session
from login_form import LoginForm, RegForm
from url_form import UrlForm
from link_shortener import short_link

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zxcbruh123'
app.path = '127.0.0.1:8080'
login_manager = LoginManager()
login_manager.init_app(app)
# blueprint для rest-api
blueprint = data.api.blueprint


# стандартный обработчик для правильной работы login_manager
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# обработчик, ответственный за само сокращение ссылки
@app.route("/link", methods=["GET"])
def link():
    # првоерка, перешел пользователь по прямому адресу, или по кнопке с главной страницы
    # нужно для правильной работы кнопки
    if not session.get("last", None):
        session["last"] = "index"
    sess = session.get("link", None)
    if sess:
        session["ok"] = True
    else:
        session["ok"] = False
    shorted_url = short_link(sess)[8:]
    if session["ok"]:
        # записываем в бд ссылку пользователя
        # нужно для сбора статистики
        if current_user.is_authenticated:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            links = user.links
            # правильно записываем ссылку в бд, если это первая ссылка пользователя
            if links:
                links += " " + session['link'] + ":-:" + shorted_url
            else:
                links = session["link"] + ":-:" + shorted_url
            user.links = links
            db_sess.commit()
    return render_template("link.html", title="Ссылка", url=shorted_url)


# Главная страница приложения

@app.route("/index", methods=['POST', 'GET'])
def index():
    session['last'] = 'index'
    url_form = UrlForm()
    if url_form.validate_on_submit():
        url = url_form.url_input.data
        # проверяем ссылку на подлинность
        import re
        regex = r"https?://[a-zA-Z0-9_.+-/#~]+"
        if re.match(regex, url):
            sess = session.get("link", 0)
            # записываем, если все хорошо
            session["link"] = url_form.url_input.data
        else:
            # если ссылка невалидна, отправляем None
            session["link"] = None
        return redirect("/link")
    return render_template("index.html", title="Главная", form=url_form)


# переводит пользователя на главную страницу приложения
# не работает с численным IP, так как в этом случае браузер стирает последний слэш
# но работает с обычными доменными именами, типа "abcd.com/"
@app.route("/", methods=["GET"])
def red_index():
    redirect("/index")


# обработчик для входа пользователя на сайт
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    error_msg = ""
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/index')
        else:
            error_msg = "Неправильно введен логин или пароль. Попробуйте еще раз"
    return render_template('login.html', title='Авторизация', form=form, error_msg=error_msg)


# обработчик для выход пользователя
@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')


# обработчик, ответственный за регистрацию пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    err_msg = ""
    if form.validate_on_submit():
        if form.password.data == form.password_req.data:
            db_sess = db_session.create_session()
            user = User()
            user.login = form.login.data
            if db_sess.query(User).filter(User.login == user.login).first():
                err_msg = "Пользователь с таким логином уже существует"
            else:
                user.hashed_password = generate_password_hash(form.password.data)
                db_sess.add(user)
                db_sess.commit()
                return redirect('/index')
        else:
            err_msg = "Пароли не совпадают"
    return render_template('reg.html', title="Register", form=form, err_msg=err_msg)


# обработчик для ошибки 404
# может возникнуть при обращении к rest-api
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Обработчик, ответственный за вывод странички со всеми генерированными ссылками пользователя
# Для входа требуется аутентификация
@login_required
@app.route("/stats")
def stats():
    db_sess = db_session.create_session()
    links = db_sess.query(User).filter(current_user.id == User.id).first().links
    print(links)
    links = links.split(" ")
    link_arr = [x.split(":-:") for x in links]
    print(links)
    return render_template("stats.html", title="Статистика", links=link_arr)


# отправная точка приложения, создает базу данных, если ее нет
def main():
    app.register_blueprint(blueprint)
    db_session.global_init("db/db.db")
    app.run(host="127.0.0.1", port="8080")
