from flask import Flask, render_template, redirect, request
from data1 import db_session
from forms.user import RegisterForm, LoginForm
from forms.search import SearchForm
from data1.users import User
from data1.lessons import Lesson
from data1.favourites import Favourites
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365)
login_manager = LoginManager()
login_manager.init_app(app)
limit = 5


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    global limit
    db_sess = db_session.create_session()
    search = SearchForm()
    favourites = db_sess.query(Favourites).filter(Favourites.user_id == current_user.id)
    if request.method == "POST":
        limit = 5
        lessons = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search.search.data}%') | Lesson.title.like(
            '%' + str(search.search.data).capitalize() + '%') | Lesson.title.like(
            '%' + str(search.search.data).lower() + '%') | Lesson.title.like(
            '%' + str(search.search.data).upper() + '%')).order_by(-Lesson.rate).limit(limit)
    else:
        lessons = db_sess.query(Lesson).order_by(-Lesson.rate).limit(limit)
    return render_template("index.html", lessons=lessons, search=search, favourites=favourites)


@app.route('/limit')
def lim():
    global limit
    limit += 5
    return redirect("/")


@app.route('/add_favourites/<int:id>')
def add_favourites(id):
    db_sess = db_session.create_session()
    user_id = current_user.id
    favourite = Favourites(lesson_id=id,
                           user_id=user_id)
    db_sess.add(favourite)
    db_sess.commit()
    return redirect("/")


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
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Это имя уже занято")
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


@app.route('/profile/<string:name>')
def watch_profile(name):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name).first()
    return render_template('profile.html', user=user)


@app.route('/lesson/<int:id>')
def edit_news(id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()
    return render_template('lesson.html', lesson=lesson)


def main():
    db_session.global_init("db/lessons.db")
    app.run()


if __name__ == '__main__':
    main()
