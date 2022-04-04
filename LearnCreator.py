from flask import Flask, render_template, redirect, request
from data1 import db_session
from forms.user import RegisterForm, LoginForm
from forms.search import SearchForm
from data1.users import User
from data1.lessons import Lesson
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    search = SearchForm()
    if request.method == "POST":
        lessons = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search.search.data}%')).limit(5)
    else:
        lessons = db_sess.query(Lesson).limit(5)
    return render_template("index.html", lessons=lessons, search=search)


@app.route("/results/<string:result>", methods=['GET', 'POST'])
def searching(result):
    db_sess = db_session.create_session()
    search = SearchForm()

    lessons = db_sess.query(Lesson).filter(result == Lesson.title)
    return render_template("index.html", lessons=lessons, search=search)


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


@app.route('/lesson/<int:id>')
@login_required
def edit_news(id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()

    return render_template('lesson.html', lesson=lesson)


def main():
    db_session.global_init("db/lessons.db")
    app.run()


if __name__ == '__main__':
    main()
