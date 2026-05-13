from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

app = Flask(__name__)

app.secret_key = "idleminds9538561984"

client = MongoClient('mongodb://localhost:27017/')
db = client.idleMinds
users_collection = db.users

def get_xp_needed(level):
    # Level 1 = 100, Level 2 = 130, Level 3 = 169, Level 4 = 219...
    return int(100 * (1.3 ** (level - 1)))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if users_collection.find_one({'username': username}):
            flash("Username already exists! Choose another.")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        # NEW: Initialize user with Level 1 and 0 XP
        users_collection.insert_one({
            'username': username, 
            'password': hashed_password,
            'level': 1,
            'xp': 0
        })
        
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = users_collection.find_one({'username': session['username']})
    
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    xp_needed = get_xp_needed(level)
    progress = int((xp / xp_needed) * 100)

    return render_template('hub.html', username=user['username'], level=level, xp=xp, next_xp=xp_needed, progress=progress)

# NEW: A route to test the level-up logic!
@app.route('/test_xp')
def test_xp():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = users_collection.find_one({'username': session['username']})
    
    # Let's say winning a game gives 35 XP
    new_xp = user.get('xp', 0) + 35
    level = user.get('level', 1)
    xp_needed = level * 100

    # Check for Level Up!
    if new_xp >= xp_needed:
        new_xp = new_xp - xp_needed # Carry over the extra XP
        level += 1
        
    # Save the new stats back to MongoDB
    users_collection.update_one(
        {'username': session['username']}, 
        {'$set': {'xp': new_xp, 'level': level}}
    )
    
    return redirect(url_for('home'))

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

@app.route('/play/sudoku')
def play_sudoku():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': session['username']})
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    return render_template('sudoku.html', username=user['username'], level=level, xp=xp, next_xp=get_xp_needed(level), progress=int((xp / get_xp_needed(level)) * 100))

@app.route('/play/pips')
def play_pips():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': session['username']})
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    return render_template('pips.html', username=user['username'], level=level, xp=xp, next_xp=get_xp_needed(level), progress=int((xp / get_xp_needed(level)) * 100))

@app.route('/play/zips')
def play_zips():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': session['username']})
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    return render_template('zips.html', username=user['username'], level=level, xp=xp, next_xp=get_xp_needed(level), progress=int((xp / get_xp_needed(level)) * 100))

@app.route('/play/wordcraft')
def play_wordcraft():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': session['username']})
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    return render_template('wordcraft.html', username=user['username'], level=level, xp=xp, next_xp=get_xp_needed(level), progress=int((xp / get_xp_needed(level)) * 100))

@app.route('/play/connections')
def play_connections():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': session['username']})
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    return render_template('connections.html', username=user['username'], level=level, xp=xp, next_xp=get_xp_needed(level), progress=int((xp / get_xp_needed(level)) * 100))

from flask import jsonify, request # Make sure request and jsonify are imported

# --- ROUTE 1: For Flet to report the win securely ---
@app.route('/api/server_win', methods=['POST'])
def server_win():
    username = request.args.get('user')
    if not username: return "No user provided", 400
        
    user = users_collection.find_one({'username': username})
    if not user: return "User not found", 404

    level = user.get('level', 1)
    new_xp = user.get('xp', 0) + 35 # Award 35 XP
    
    # Calculate level ups
    while True:
        xp_needed = get_xp_needed(level) # Make sure your get_xp_needed function is still at the top of app.py!
        if new_xp >= xp_needed:
            new_xp -= xp_needed
            level += 1
        else:
            break
            
    users_collection.update_one({'username': username}, {'$set': {'xp': new_xp, 'level': level}})
    return "Win recorded", 200

# --- ROUTE 2: For the browser to silently check for UI updates ---
@app.route('/api/get_xp')
def get_xp():
    if 'username' not in session: return jsonify({"error": "Not logged in"}), 401
    
    user = users_collection.find_one({'username': session['username']})
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    next_xp = get_xp_needed(level)
    progress = int((xp / next_xp) * 100)
    
    return jsonify({"level": level, "xp": xp, "next_xp": next_xp, "progress": progress})

if __name__ == '__main__':
    app.run(debug=True, port=5000)