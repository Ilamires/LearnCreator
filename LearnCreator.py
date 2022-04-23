from flask import Flask, render_template, redirect, request
import json
from data1 import db_session
from forms.user import RegisterForm, LoginForm
from forms.search import SearchForm
from data1.users import User
from data1.lessons import Lesson
from data1.favourites import Favourites
from data1.rates import Rates
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
user_now = ''
lessons_now_count = 0


def start_parameters():
    return ['', 0, 5]


search_now, FirstLesson, limit = start_parameters()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    global limit, FirstLesson, search_now, lessons_now_count
    db_sess = db_session.create_session()
    search = SearchForm()
    favourites_ids = [x.lesson_id for x in db_sess.query(Favourites.lesson_id).distinct()]
    if request.method == "POST":
        FirstLesson = 0
        limit = 5
        search_now = search.search.data
    lessons = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
        '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
        '%' + str(search_now).lower() + '%') | Lesson.title.like(
        '%' + str(search_now).upper() + '%')).order_by(-Lesson.rate)[FirstLesson:limit]
    lessons_now_count = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
        '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
        '%' + str(search_now).lower() + '%') | Lesson.title.like(
        '%' + str(search_now).upper() + '%')).count()
    return render_template("index.html", lessons=lessons, search=search, favourites_ids=favourites_ids,
                           FirstLesson=FirstLesson, lessons_now_count=lessons_now_count, limit=limit)


@app.route('/limit')
def lim():
    global limit, FirstLesson
    FirstLesson += 5
    limit += 5
    return redirect("/")


@app.route('/back')
def back():
    global limit, FirstLesson
    FirstLesson -= 5
    limit -= 5
    return redirect("/")


@app.route('/main')
def main():
    global limit, FirstLesson, search_now
    search_now, FirstLesson, limit = start_parameters()
    return redirect("/")


@app.route('/delete_favourites/<int:id>')
def delete_favourites(id):
    db_sess = db_session.create_session()
    user_id = current_user.id
    favourite = db_sess.query(Favourites).filter(user_id == Favourites.user_id, id == Favourites.lesson_id).first()
    db_sess.delete(favourite)
    db_sess.commit()
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


@app.route('/your_lessons')
def your_les():
    global profile
    profile = 'your_lessons'
    return redirect(f"/profile/{user_now}")


@app.route('/your_favourites')
def your_fav():
    global profile
    profile = 'your_favourites'
    return redirect(f"/profile/{user_now}")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    global limit, FirstLesson, search_now
    search_now, FirstLesson, limit = start_parameters()
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
    global limit, FirstLesson, search_now
    search_now, FirstLesson, limit = start_parameters()
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
    global limit, user_now, profile, FirstLesson, search_now
    if name != user_now:
        profile = 'your_lessons'
    search_now, FirstLesson, limit = start_parameters()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name).first()
    user_now = user.name
    db_sess = db_session.create_session()
    if profile == 'your_lessons':
        lessons = db_sess.query(Lesson).filter(Lesson.user_id == user.id).order_by(-Lesson.rate).limit(limit)
    else:
        favourites_ids = [x.lesson_id for x in
                          db_sess.query(Favourites.lesson_id).filter(Favourites.user_id == user.id).distinct()]
        lessons = db_sess.query(Lesson).filter(Lesson.id.in_(favourites_ids)).order_by(-Lesson.rate).limit(limit)
    return render_template('profile.html', user=user, profile=profile, lessons=lessons)


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
