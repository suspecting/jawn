# J.A.W.N. (Just Another WeenNet)
# By Lua


from flask import Flask, request, session, render_template, redirect, url_for, flash
from markupsafe import escape
import sqlite3
import uuid
import secret


app = Flask(__name__)
app.secret_key = secret.password
con = sqlite3.connect("main.db", check_same_thread=False)


# THE MEAT AND POTATOES ARE BELOW

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST']) # WIP: Add e-mail verification or something similar.
def register():
    if request.method == 'POST':
        session['username'] = request.form['username']
        username = request.form['username']
        cur = con.cursor()
        cur.execute("INSERT INTO users (user, userkey) VALUES (?, ?)", (f"{escape(username)}", str(uuid.uuid4())))
        con.commit()
        session['logged_in'] = True
        return redirect(url_for('main'))
    if session['logged_in'] == True:
        return redirect(url_for('main'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        session['userkey'] = request.form['userkey']
        key = request.form['userkey']
        cur = con.cursor()
        cur.execute('SELECT userkey FROM users WHERE userkey = ?', (key,))
        if key == cur.fetchone()[0]:
            session['logged_in'] = True
            cur.execute('SELECT user FROM users WHERE userkey = ?', (key,))
            session['username'] = cur.fetchone()[0]
            cur.execute('SELECT dolla FROM users WHERE userkey = ?', (key,))
            session['dolla'] = cur.fetchone()[0]
            return redirect(url_for('main'))
        # WIP: add ELSE function... 500 Internal Error occurs if you type your key incorrectly. Sorry bout that.
        if session['logged_in'] == True:
            return redirect(url_for('main'))
    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('userkey', None)
    session['logged_in'] = False
    return redirect(url_for('main'))

@app.route('/settings', methods=['GET', 'POST']) # This is a work in progress...
def settings():
    error = None
    if session['logged_in'] == False:
        flash("You aren't logged in", 'error')
        return redirect(url_for('main'))
    if request.method == 'POST':
        cur = con.cursor()
        if request.form['description'] or request.form['username'] == '':
            flash('Thats not a thing', 'error')
            return render_template('settings.html')
        else:
            return "Kill"
            
    return render_template('settings.html')

@app.route('/user/<username>')
def user(username): # Code no longer repetitive
    cur = con.cursor()
    cur.execute('SELECT user, rank, description FROM users WHERE user = ?', (username,))
    user, rank, description = cur.fetchone()
    return render_template('user.html', username=user, rank=rank, description=description)
    
