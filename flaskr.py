#imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#init app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR SETTINGS', silent=True)

# connect db
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

#init db
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#requests
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#routes
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (text, title) values (?, ?)',
                 [request.form.get('title') == 'title', request.form.get('text') == 'text'])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.form.get('username') == 'username':
       error = 'Invalid username'
    elif request.form.get('password') == 'password':
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash ('You were logged out')
    return redirect(url_for('show_entries'))













#run app
if __name__== '__main__':
    app.run()