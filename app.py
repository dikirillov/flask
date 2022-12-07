import sqlite3
import os
from flask import Flask, session, g, abort, send_file
from flask import render_template, flash, redirect, url_for, request
from submodules import User, LoginForm, ResumeForm, RegistrationForm

# конфигурация

DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)
def connect_db():
    """Соединяет с указанной базой данных."""
    rv = sqlite3.connect(app.config['DATABASE']) # внутри конфигураций надо будет указать БД, в которую мы будем все хранить
    rv.row_factory = sqlite3.Row #инстанс для итерации по строчкам (может брать по строке и выдавать)
    return rv


def get_db():
    """Если ещё нет соединения с базой данных, открыть новое - для текущего контекста приложения"""
    if not hasattr(g, 'sqlite_db'): #g - это наша глобальная переменная, являющасяс объектом отрисовки
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext #декоратор при разрыве connection
def close_db(error): #закрытие может проходить как нормально, так и с ошибкой, которую можно обрабатывать
    """Закрываем БД при разрыве"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    """Инициализируем наше БД"""
    with app.app_context(): # внутри app_context app и g связаны
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/')
def hello_page():
    return render_template("layout.html")


@app.route('/resume', methods=['GET', 'POST'])
def show_entries():
    if not session.get('logged_in'):
        abort(401)

    db = get_db()
    form = ResumeForm()
    query = "SELECT * FROM entries WHERE username = '" + session.get('username') + "' and password_hash = '" + \
            session.get('password') + "'"
    saved = db.execute(query).fetchone()
    form.generate(saved["full_name"], saved["birth_date"], saved["contact_email"], saved["contact_phone"])
    if request.method == 'POST':
        user = User()
        user.username = session.get('username')
        user.password_hash = session.get('password')
        if request.form.get("submit_save"):
            if request.form.get("full_name"):
                user.full_name = request.form.get("full_name")
                query_full_name = "UPDATE entries SET full_name = '" + user.full_name + "' Where username = '" + \
                                  user.username + "' and password_hash = '" + user.password_hash + "'"
                db.execute(query_full_name)
                form.full_name.data = user.full_name
            if request.form.get("birth_date"):
                user.birth_date = request.form.get("birth_date")
                query_birth_date = "UPDATE entries SET birth_date = '" + user.birth_date + "' Where username = '" + \
                                   user.username + "' and password_hash = '" + user.password_hash + "'"
                db.execute(query_birth_date)
                form.birth_date.data = user.birth_date
            if request.form.get("contact_email"):
                user.contact_email = request.form.get("contact_email")
                query_contact_email = "UPDATE entries SET contact_email = '" + user.contact_email + "' Where username = '" + \
                                      user.username + "' and password_hash = '" + user.password_hash + "'"
                db.execute(query_contact_email)
                form.contact_email.data = user.contact_email
            if request.form.get("contact_phone"):
                user.contact_phone = request.form.get("contact_phone")
                query_contact_phone = "UPDATE entries SET contact_phone = '" + user.contact_phone + "' Where username = '" + \
                                      user.username + "' and password_hash = '" + user.password_hash + "'"
                db.execute(query_contact_phone)
                form.contact_phone.data = user.contact_phone
            db.commit()
            return redirect(url_for('show_entries'))
        if request.form.get("submit_create"):
            user = User()
            user.username = session.get('username')
            user.password_hash = session.get('password')
            user.full_name = request.form.get("full_name")
            user.birth_date = request.form.get("birth_date")
            user.contact_email = request.form.get("contact_email")
            user.contact_phone = request.form.get("contact_phone")
            query_full_name = "UPDATE entries SET full_name = '" + user.full_name + "' Where username = '" + \
                              user.username + "' and password_hash = '" + user.password_hash + "'"
            query_birth_date = "UPDATE entries SET birth_date = '" + user.birth_date + "' Where username = '" + \
                              user.username + "' and password_hash = '" + user.password_hash + "'"
            query_contact_email = "UPDATE entries SET contact_email = '" + user.contact_email + "' Where username = '" + \
                              user.username + "' and password_hash = '" + user.password_hash + "'"
            query_contact_phone = "UPDATE entries SET contact_phone = '" + user.contact_phone + "' Where username = '" + \
                              user.username + "' and password_hash = '" + user.password_hash + "'"
            db.execute(query_full_name)
            db.execute(query_birth_date)
            db.execute(query_contact_email)
            db.execute(query_contact_phone)
            db.commit()
            user.create_resume()
            return send_file('resume.pdf', as_attachment=True)
    return render_template('show_entries.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm()
    if request.method == 'POST':
        db = get_db()
        query = "SELECT rowid FROM entries WHERE username = '" + str(form.username.data) + "' and password_hash = '" + str(form.password.data) + "'"
        checker = db.execute(query).fetchone()
        if checker is None:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            session["username"] = form.username.data
            session["password"] = form.password.data
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    form = RegistrationForm()
    if request.method == 'POST':
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.password_hash = form.password.data
        db = get_db()
        user.id = str(len(list(db.execute("select * from entries"))) + 1)
        flash('You were logged in')
        query = "INSERT INTO entries (id, username, email, password_hash, full_name, birth_date, contact_email, contact_phone) VALUES "
        values = "('" + user.id + "', '" + user.username + "', '" + user.email + "', '" + user.password_hash + "', '" + \
                 user.full_name + "', '" + user.birth_date + "', '" + user.contact_email + "', '" + user.contact_phone + "');"
        session["username"] = user.username
        session["password"] = user.password_hash
        query += values
        db.execute(query)
        db.commit()
        session['logged_in'] = True

        return redirect(url_for('show_entries'))
    return render_template('register.html', error=error, form=form)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('password', None)
    flash('You were logged out')
    return redirect(url_for('hello_page'))


if __name__ == '__main__':
    init_db()
    app.run()