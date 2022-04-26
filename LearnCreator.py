from flask import Flask, render_template, redirect, request
import json
from data1 import db_session
from forms.user import RegisterForm, LoginForm
from forms.search import SearchForm
from forms.lesson import Content, Arr, Image
from data1.users import User
from data1.lessons import Lesson
from data1.favourites import Favourites
from data1.rates_lessons import LessonsRates
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

UPLOAD_FOLDER = '/static/img/'
app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
lessons_now_count = 0
rates = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']


def start_parameters():
    return ['', '', 0, 5]


search_now, user_now, FirstResult, limit = start_parameters()


def estimating(id, url):
    search = SearchForm()
    if search.estimate.data in rates:
        db_sess = db_session.create_session()
        lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()
        users_rates = [x.user_id for x in
                       db_sess.query(LessonsRates.user_id).filter(LessonsRates.lesson_id == id).distinct()]
        if current_user.id not in users_rates:
            new_rate = LessonsRates(
                lesson_id=id,
                user_id=current_user.id,
                rate=search.estimate.data
            )
            db_sess.add(new_rate)
            lesson.rates_count += 1
        else:
            new_rate = db_sess.query(LessonsRates).filter(LessonsRates.lesson_id == id,
                                                          LessonsRates.user_id == current_user.id).first()
            new_rate.rate = search.estimate.data
        lesson_rates = [x.rate for x in
                        db_sess.query(LessonsRates.rate).filter(LessonsRates.lesson_id == id).distinct()]
        lesson.rate = round(sum(lesson_rates) / len(lesson_rates), 2)
        db_sess.commit()
    return redirect(url)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index():
    global limit, FirstResult, search_now, lessons_now_count
    db_sess = db_session.create_session()
    search = SearchForm()
    favourites_ids = []
    if current_user.is_authenticated:
        favourites_ids = [x.lesson_id for x in
                          db_sess.query(Favourites.lesson_id).filter(Favourites.user_id == current_user.id).distinct()]
    if request.method == "POST":
        FirstResult = 0
        limit = 5
        search_now = search.search.data
    lessons = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
        '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
        '%' + str(search_now).lower() + '%') | Lesson.title.like(
        '%' + str(search_now).upper() + '%')).order_by(-Lesson.rate, -Lesson.added_to_favorites_count)[
              FirstResult:limit]
    lessons_now_count = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
        '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
        '%' + str(search_now).lower() + '%') | Lesson.title.like(
        '%' + str(search_now).upper() + '%')).count()
    return render_template("index.html", lessons=lessons, search=search, favourites_ids=favourites_ids,
                           FirstResult=FirstResult, lessons_now_count=lessons_now_count, limit=limit)


@app.route("/profile", methods=['GET', 'POST'])
def profiles():
    global limit, FirstResult, search_now, lessons_now_count
    db_sess = db_session.create_session()
    search = SearchForm()
    if request.method == "POST":
        FirstResult = 0
        limit = 5
        search_now = search.search.data
    users = db_sess.query(User).filter(User.name.like(f'%{search_now}%') | User.name.like(
        '%' + str(search_now).capitalize() + '%') | User.name.like(
        '%' + str(search_now).lower() + '%') | User.name.like(
        '%' + str(search_now).upper() + '%')).order_by(-User.created_date)[FirstResult:limit]
    users_now_count = db_sess.query(User).filter(User.name.like(f'%{search_now}%') | User.name.like(
        '%' + str(search_now).capitalize() + '%') | User.name.like(
        '%' + str(search_now).lower() + '%') | User.name.like(
        '%' + str(search_now).upper() + '%')).count()
    return render_template("profiles.html", users=users, search=search, FirstResult=FirstResult,
                           users_now_count=users_now_count, limit=limit)


@app.route('/limit')
def lim():
    global limit, FirstResult
    FirstResult += 5
    limit += 5
    return redirect("/")


@app.route('/back')
def back():
    global limit, FirstResult
    FirstResult -= 5
    limit -= 5
    return redirect("/")


@app.route('/limit_profile')
def lim_profile():
    global limit, FirstResult
    FirstResult += 5
    limit += 5
    return redirect(f"/profile/{user_now}")


@app.route('/back_profile')
def back_profile():
    global limit, FirstResult
    FirstResult -= 5
    limit -= 5
    return redirect(f"/profile/{user_now}")


@app.route('/estimate/<int:id>', methods=['GET', 'POST'])
def estimate(id):
    return estimating(id, '/')


@app.route('/estimate_profile/<int:id>', methods=['GET', 'POST'])
def estimate_profile(id):
    return estimating(id, f'/profile/{user_now}')


@app.route('/main')
def main():
    global limit, FirstResult, search_now, user_now
    search_now, user_now, FirstResult, limit = start_parameters()
    return redirect("/")


@app.route('/authors')
def authors():
    global limit, FirstResult, search_now, user_now
    search_now, user_now, FirstResult, limit = start_parameters()
    return redirect("/profile")


@app.route('/delete_favourites/<int:id>')
def delete_favourites(id):
    db_sess = db_session.create_session()
    user_id = current_user.id
    favourite = db_sess.query(Favourites).filter(user_id == Favourites.user_id, id == Favourites.lesson_id).first()
    db_sess.delete(favourite)
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.favourites_lessons_count -= 1
    lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()
    lesson.added_to_favorites_count -= 1
    db_sess.commit()
    return redirect("/")


@app.route('/delete_favourites_profile/<int:id>')
def delete_favourites_profile(id):
    db_sess = db_session.create_session()
    user_id = current_user.id
    favourite = db_sess.query(Favourites).filter(user_id == Favourites.user_id, id == Favourites.lesson_id).first()
    db_sess.delete(favourite)
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.favourites_lessons_count -= 1
    lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()
    lesson.added_to_favorites_count -= 1
    db_sess.commit()
    return redirect(f"/profile/{user_now}")


@app.route('/add_favourites/<int:id>')
def add_favourites(id):
    db_sess = db_session.create_session()
    user_id = current_user.id
    favourite = Favourites(lesson_id=id,
                           user_id=user_id)
    db_sess.add(favourite)
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.favourites_lessons_count += 1
    lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()
    lesson.added_to_favorites_count += 1
    db_sess.commit()
    return redirect("/")


@app.route('/add_favourites_profile/<int:id>')
def add_favourites_profile(id):
    db_sess = db_session.create_session()
    user_id = current_user.id
    favourite = Favourites(lesson_id=id,
                           user_id=user_id)
    db_sess.add(favourite)
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.favourites_lessons_count += 1
    lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()
    lesson.added_to_favorites_count += 1
    db_sess.commit()
    return redirect(f"/profile/{user_now}")


@app.route('/your_lessons')
def your_les():
    global profile, search_now, user_now, FirstResult, limit
    search_now, x, FirstResult, limit = start_parameters()
    profile = 'your_lessons'
    return redirect(f"/profile/{user_now}")


@app.route('/your_favourites')
def your_fav():
    global profile, search_now, user_now, FirstResult, limit
    search_now, x, FirstResult, limit = start_parameters()
    profile = 'your_favourites'
    return redirect(f"/profile/{user_now}")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    global limit, FirstResult, search_now
    search_now, user_now, FirstResult, limit = start_parameters()
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
    global limit, FirstResult, search_now
    search_now, user_now, FirstResult, limit = start_parameters()
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
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


@app.route('/profile/<string:name>', methods=['GET', 'POST'])
def watch_profile(name):
    global limit, user_now, profile, FirstResult, search_now, lessons_now_count
    search = SearchForm()
    if name != user_now:
        profile = 'your_lessons'
        search_now, user_now, FirstResult, limit = start_parameters()
    if request.method == "POST":
        FirstResult = 0
        limit = 5
        search_now = search.search.data
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name).first()
    user_now = user.name
    db_sess = db_session.create_session()

    my_favourites_ids = []
    if current_user.is_authenticated:
        my_favourites_ids = [x.lesson_id for x in
                             db_sess.query(Favourites.lesson_id).filter(
                                 Favourites.user_id == current_user.id).distinct()]
    favourites_ids = [x.lesson_id for x in
                      db_sess.query(Favourites.lesson_id).filter(Favourites.user_id == user.id).distinct()]
    if profile == 'your_lessons':
        lessons = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
            '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
            '%' + str(search_now).lower() + '%') | Lesson.title.like(
            '%' + str(search_now).upper() + '%'), Lesson.user_id == user.id).order_by(-Lesson.rate,
                                                                                      -Lesson.added_to_favorites_count)[
                  FirstResult:limit]
        lessons_now_count = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
            '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
            '%' + str(search_now).lower() + '%') | Lesson.title.like(
            '%' + str(search_now).upper() + '%'), Lesson.user_id == user.id).count()
    else:
        lessons = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
            '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
            '%' + str(search_now).lower() + '%') | Lesson.title.like(
            '%' + str(search_now).upper() + '%'), Lesson.id.in_(favourites_ids)).order_by(-Lesson.rate,
                                                                                          -Lesson.added_to_favorites_count)[
                  FirstResult:limit]
        lessons_now_count = db_sess.query(Lesson).filter(Lesson.title.like(f'%{search_now}%') | Lesson.title.like(
            '%' + str(search_now).capitalize() + '%') | Lesson.title.like(
            '%' + str(search_now).lower() + '%') | Lesson.title.like(
            '%' + str(search_now).upper() + '%'), Lesson.id.in_(favourites_ids)).count()
    return render_template('profile.html', user=user, profile=profile, lessons=lessons, search=search,
                           lessons_now_count=lessons_now_count, FirstResult=FirstResult, limit=limit,
                           my_favourites_ids=my_favourites_ids)


@app.route('/lesson/<int:id>')
def watch_lesson(id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == id).first()
    return render_template('lesson.html', lesson=lesson)


@app.route('/create_lesson')
@login_required
def edit_lesson():
    return render_template('content.html', title='создание новости')


@app.route('/button/', methods=['GET', 'POST'])
def create_lesson():
    arr_content = Arr()
    if request.method == 'POST':
        print(str(request.form) + "------------------- POST")
        for i in range(len(arr_content.arr)):
            if arr_content.arr[i].type != "img":
                arr_content.arr[i].text.data = request.form['text' + str(i)]
            else:
                if arr_content.arr[i].img_name == "":
                    file = request.files["file" + str(i)]
                    if file.filename != "":
                        arr_content.arr[i].img_name = "img/" + str(file.filename)
                        print(arr_content.arr[i].img_name)
                        file.save("static/img/" + str(file.filename))
        img = Image()
        img.img.name = "file" + str(len(arr_content.arr))
        arr_content.arr.append(img)
        content = Content()
        content.text.name = "text" + str(len(arr_content.arr))
        arr_content.arr.append(content)
    return render_template('content.html', title='создание новости', content=arr_content.arr)


def main():
    db_session.global_init("db/lessons.db")
    app.run()


if __name__ == '__main__':
    main()
