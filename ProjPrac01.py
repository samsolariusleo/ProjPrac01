from flask import *
from functools import wraps
import sqlite3

DATABASE = '/home/LionCubFearMe/mysite/sales.db'

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
    cur = g.db.execute('SELECT id, imgurl, item_name, price, availability FROM items')
    listofitems = [dict(id = row[0], imgurl = row[1], item_name = row[2], price = row[3], availability = row[4])
                   for row in cur.fetchall()]
    g.db.close()
    return render_template('shop.html', listofitems = listofitems)

@app.route('/buy', methods = ['POST'])
@login_required
def buy():
    item_id = request.form['id']
    quantity = request.form['quantity']
    g.db = connect_db()
    cur = g.db.execute('SELECT id, imgurl, item_name, price FROM items WHERE id ='+ str(item_id))
    listofdict = [dict(id=row[0], imgurl=row[1], item_name=row[2], price=row[3]) for row in cur.fetchall()]
    currentorder = listofdict[0]
    imgurl = currentorder['imgurl']
    item_name = currentorder['item_name']
    price = currentorder['price']
    g.db.execute('INSERT INTO orders (imgurl, item_name, price, quantity) '
                 'VALUES (?, ?, ?, ?)', [imgurl, item_name, price, quantity])
    g.db.commit()
    flash('Your order has been made')
    return redirect(url_for('shop'))

@app.route('/confirm')
@login_required
def confirm():
    g.db = connect_db()
    cur = g.db.execute('SELECT id, imgurl, item_name, price, quantity FROM orders')
    listorders = [dict(id=row[0], imgurl=row[1], item_name=row[2], price=row[3], quantity=row[4]) for row in cur.fetchall()]
    g.db.close()
    return render_template('confirm.html', listorders = listorders)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    g.db = connect_db()
    cur = g.db.execute('DELETE FROM orders WHERE id='+str(id))
    g.db.commit()
    g.db.close()
    flash('The item has been removed from your cart')
    return redirect(url_for('confirm'))

@app.route('/sendorders', methods=['POST'])
@login_required
def sendorders():
    g.db = connect_db()
    # get all information about current order and send it over to another database
    confirmed = g.db.execute('SELECT * FROM orders')
    listoforders = [dict(id=row[0], imgurl=row[1], item_name=row[2], price=row[3], quantity=row[4])
                    for row in confirmed.fetchall()]
    for i in range(0,len(listoforders)):
        currentorder = listoforders[i]
        imgurl = currentorder['imgurl']
        item_name = currentorder['item_name']
        price = currentorder['price']
        quantity = currentorder['quantity']
        g.db.execute('INSERT INTO confirmed (imgurl, item_name, price, quantity) '
                     'VALUES (?, ?, ?, ?)', [imgurl, item_name, price, quantity])
        g.db.commit()
    cur = g.db.execute('DELETE FROM orders')
    g.db.commit()
    flash('Your order has been confirmed and submitted for processing.')
    return redirect(url_for('history'))

@app.route('/history')
@login_required
def history():
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM confirmed')
    confirmedlist = [dict(id=row[0], imgurl=row[1], item_name=row[2], price=row[3], quantity=row[4])
                     for row in cur.fetchall()]
    g.db.close()
    return render_template('history.html', confirmedlist = confirmedlist)

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
