from flask import Flask, render_template, redirect, make_response, request, session
from werkzeug.utils import secure_filename
import os
from data1 import db_session
from forms.user import RegisterForm, LoginForm
from data1.users import User
from data1.lessons import Lesson
from forms.lesson import Content, Arr, Image_c
from wtforms import StringField, TextAreaField
import datetime
from PIL import Image
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

UPLOAD_FOLDER = '/static/img/'
app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365)
login_manager = LoginManager()
login_manager.init_app(app)

MAXSIZE = (1028, 1028)
global arr_content


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    global arr_content
    arr_content = Arr()
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        lessons = db_sess.query(Lesson).filter(
            Lesson.user == current_user)
    else:
        lessons = db_sess.query(Lesson)
    return render_template("index.html", lessons=lessons)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/create_lesson')
@login_required
def edit_news():
    return render_template('content.html', title='создание новости')


@app.route('/button/', methods=['GET', 'POST'])
def create_lesson():
    global arr_content
    button = request.form["parameter"]
    commit()
    if button == "img":
        img = Image_c()
        img.img.name = "file" + str(len(arr_content.arr))
        arr_content.arr.append(img)
    elif button == "text":
        content = Content()
        content.text.name = "text" + str(len(arr_content.arr))
        arr_content.arr.append(content)
    return render_template('content.html', title='создание новости', content=arr_content.arr)


def commit():
    global arr_content
    print(str(request.form) + "------------------- POST")
    for i in range(len(arr_content.arr)):
        if arr_content.arr[i].type != "img":
            arr_content.arr[i].text.data = request.form['text' + str(i)]
        else:
            if arr_content.arr[i].img_name == "":
                file = request.files["file" + str(i)]
                if file.filename != "":
                    file.save("static/img/" + str(file.filename))
                    img = Image.open("static/img/" + str(file.filename))
                    arr_content.arr[i].img_name = "img/" + str(file.filename)
                    img.thumbnail(MAXSIZE)
                    img.save("static/img/" + str(file.filename))


def main():
    db_session.global_init("db/lessons.db")
    app.run()


if __name__ == '__main__':
    main()
