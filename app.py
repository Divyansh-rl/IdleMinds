from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "idleminds9538561984"

client = MongoClient('mongodb://localhost:27017/')
db = client.idleMinds
users_collection = db.users

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if users_collection.find_one({'username': username}):
            flash("Username already exists! Choose another.")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})
        
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users_collection.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('hub.html',username=session['username'])

@app.route('/play/sudoku')
def play_sudoku():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('sudoku.html', username=session['username'])

@app.route('/play/pips')
def play_pips():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('pips.html', username=session['username'])

@app.route('/play/zips')
def play_zips():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('zips.html', username=session['username'])

@app.route('/play/wordcraft')
def play_wordcraft():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('wordcraft.html', username=session['username'])

@app.route('/play/connections')
def play_connections():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('connections.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)