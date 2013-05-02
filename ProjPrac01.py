from flask import *
from functools import wraps
import sqlite3

DATABASE = 'sales.db'

app = Flask(__name__)
app.config.from_object(__name__)

app.secret_key = 'this is giving me headaches'

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('log'))
    return wrap

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/shop')
@login_required
def shop():
    g.db = connect_db()
    cur = g.db.execute('SELECT item_name, price, availability FROM items')
    listofitems = [dict(item_name = row[0], price = row[1], availability = row[2]) for row in cur.fetchall()]
    g.db.close()
    return render_template('shop.html', listofitems = listofitems)

@app.route('/history')
@login_required
def history():
    return render_template('history.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('log'))

@app.route('/log', methods=['GET', 'POST'])
def log():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template('log.html', error=error)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
