from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "idleminds9538561984"

client = MongoClient('mongodb://localhost:27017/')
db = client.idleMinds
users_collection = db.users

def get_xp_needed(level):
    return int(100 * (1.3 ** (level - 1)))

def manage_daily_login(username):
    user = users_collection.find_one({'username': username})
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    last_login = user.get('last_login_date', '')
    streak = user.get('streak', 0)
    
    if last_login == yesterday_str:
        streak += 1
    elif last_login != today_str:
        streak = 1 
        
    # 2. Update Quest
    quest_date = user.get('quest_date', '')
    if quest_date != today_str:
        # It's a new day! Give them a fresh quest
        updates = {
            'last_login_date': today_str,
            'streak': streak,
            'quest_date': today_str,
            'quest_progress': 0,
            'quest_goal': 2,
            'quest_completed': False
        }
    else:
        # Just update login date and streak if they are logging in again today
        updates = {'last_login_date': today_str, 'streak': streak}
        
    users_collection.update_one({'username': username}, {'$set': updates})
    
    # Return the updated user so the route can use the fresh data
    return users_collection.find_one({'username': username})

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
    if 'username' not in session: return redirect(url_for('login'))
    
    user = manage_daily_login(session['username'])
    
    if 'join_date' not in user:
        new_date = datetime.now().strftime('%b %Y') # e.g., 'May 2026'
        users_collection.update_one({'username': session['username']}, {'$set': {'join_date': new_date}})
        user['join_date'] = new_date
        
   
    games_played = user.get('games_played', 0)
    games_won = user.get('games_won', 0)
    win_rate = int((games_won / games_played) * 100) if games_played > 0 else 0

    level = user.get('level', 1)
    xp = user.get('xp', 0)
    xp_needed = get_xp_needed(level)
    progress = int((xp / xp_needed) * 100)
    
    quest_progress = user.get('quest_progress', 0)
    quest_goal = user.get('quest_goal', 2)
    quest_percent = min(int((quest_progress / quest_goal) * 100), 100)
    
    top_users_cursor = users_collection.find({}, {'username': 1, 'level': 1, 'xp': 1}).sort([('level', -1), ('xp', -1)]).limit(10)

    
    return render_template('hub.html', 
                           username=user['username'], level=level, xp=xp, 
                           next_xp=xp_needed, progress=progress, top_users=list(top_users_cursor),
                           streak=user.get('streak', 1), quest_progress=quest_progress, 
                           quest_goal=quest_goal, quest_percent=quest_percent, 
                           quest_completed=user.get('quest_completed', False),
                           join_date=user['join_date'], games_played=games_played, 
                           games_won=games_won, win_rate=win_rate)

@app.route('/test_xp')
def test_xp():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = users_collection.find_one({'username': session['username']})
    
    
    new_xp = user.get('xp', 0) + 35
    level = user.get('level', 1)
    xp_needed = level * 100

    if new_xp >= xp_needed:
        new_xp = new_xp - xp_needed 
        level += 1
        
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
    if 'username' not in session: return redirect(url_for('login'))
    
    user = users_collection.find_one({'username': session['username']})
    
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    xp_needed = get_xp_needed(level)
    progress = int((xp / xp_needed) * 100)
    
    return render_template('sudoku.html', 
                           username=user['username'], 
                           level=level, 
                           xp=xp, 
                           next_xp=xp_needed, 
                           progress=progress,
                           streak=user.get('streak', 1), 
                           quest_progress=user.get('quest_progress', 0),
                           quest_goal=user.get('quest_goal', 2),
                           quest_percent=int((user.get('quest_progress', 0) / user.get('quest_goal', 2)) * 100) if user.get('quest_goal', 2) > 0 else 0,
                           quest_completed=user.get('quest_completed', False))

@app.route('/play/pips')
def play_pips():
    if 'username' not in session: return redirect(url_for('login'))
 
    user = users_collection.find_one({'username': session['username']})
    
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    xp_needed = get_xp_needed(level)
    progress = int((xp / xp_needed) * 100)
    
    # 2. Pass EVERYTHING to the template, including the streak!
    return render_template('pips.html', 
                           username=user['username'], 
                           level=level, 
                           xp=xp, 
                           next_xp=xp_needed, 
                           progress=progress,
                           streak=user.get('streak', 1), # <-- THIS IS THE MISSING PIECE!
                           quest_progress=user.get('quest_progress', 0),
                           quest_goal=user.get('quest_goal', 2),
                           quest_percent=int((user.get('quest_progress', 0) / user.get('quest_goal', 2)) * 100) if user.get('quest_goal', 2) > 0 else 0,
                           quest_completed=user.get('quest_completed', False))

@app.route('/play/zips')
def play_zips():
    if 'username' not in session: return redirect(url_for('login'))
   
    user = users_collection.find_one({'username': session['username']})
    
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    xp_needed = get_xp_needed(level)
    progress = int((xp / xp_needed) * 100)
  
    return render_template('zips.html', 
                           username=user['username'], 
                           level=level, 
                           xp=xp, 
                           next_xp=xp_needed, 
                           progress=progress,
                           streak=user.get('streak', 1), # <-- THIS IS THE MISSING PIECE!
                           quest_progress=user.get('quest_progress', 0),
                           quest_goal=user.get('quest_goal', 2),
                           quest_percent=int((user.get('quest_progress', 0) / user.get('quest_goal', 2)) * 100) if user.get('quest_goal', 2) > 0 else 0,
                           quest_completed=user.get('quest_completed', False))

@app.route('/play/wordcraft')
def play_wordcraft():
    if 'username' not in session: return redirect(url_for('login'))
    
  
    user = users_collection.find_one({'username': session['username']})
    
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    xp_needed = get_xp_needed(level)
    progress = int((xp / xp_needed) * 100)
    
    
    return render_template('wordcraft.html', 
                           username=user['username'], 
                           level=level, 
                           xp=xp, 
                           next_xp=xp_needed, 
                           progress=progress,
                           streak=user.get('streak', 1), # <-- THIS IS THE MISSING PIECE!
                           quest_progress=user.get('quest_progress', 0),
                           quest_goal=user.get('quest_goal', 2),
                           quest_percent=int((user.get('quest_progress', 0) / user.get('quest_goal', 2)) * 100) if user.get('quest_goal', 2) > 0 else 0,
                           quest_completed=user.get('quest_completed', False))

@app.route('/play/connections')
def play_connections():
    if 'username' not in session: return redirect(url_for('login'))
    
  
    user = users_collection.find_one({'username': session['username']})
    
    level = user.get('level', 1)
    xp = user.get('xp', 0)
    xp_needed = get_xp_needed(level)
    progress = int((xp / xp_needed) * 100)
    
  
    return render_template('connections.html', 
                           username=user['username'], 
                           level=level, 
                           xp=xp, 
                           next_xp=xp_needed, 
                           progress=progress,
                           streak=user.get('streak', 1), 
                           quest_progress=user.get('quest_progress', 0),
                           quest_goal=user.get('quest_goal', 2),
                           quest_percent=int((user.get('quest_progress', 0) / user.get('quest_goal', 2)) * 100) if user.get('quest_goal', 2) > 0 else 0,
                           quest_completed=user.get('quest_completed', False))

from flask import jsonify, request 

@app.route('/api/server_win', methods=['POST'])
def server_win():
    username = request.args.get('user')
    if not username: return "No user provided", 400
        
    user = users_collection.find_one({'username': username})
    if not user: return "User not found", 404

    games_played = user.get('games_played', 0) + 1
    games_won = user.get('games_won', 0) + 1
    users_collection.update_one({'username': username}, {'$set': {'games_played': games_played, 'games_won': games_won}})

    level = user.get('level', 1)
    new_xp = user.get('xp', 0) + 35 
    
  
    quest_progress = user.get('quest_progress', 0)
    quest_completed = user.get('quest_completed', False)
    quest_goal = user.get('quest_goal', 2)
    today_str = datetime.now().strftime('%Y-%m-%d')
    
   
    if not quest_completed and user.get('quest_date') == today_str:
        quest_progress += 1
        if quest_progress >= quest_goal:
            new_xp += 100 # BONUS 100 XP FOR COMPLETING THE QUEST!
            quest_completed = True
            
        users_collection.update_one({'username': username}, {'$set': {'quest_progress': quest_progress, 'quest_completed': quest_completed}})

    
    while True:
        xp_needed = get_xp_needed(level)
        if new_xp >= xp_needed:
            new_xp -= xp_needed
            level += 1
        else:
            break
            
    users_collection.update_one({'username': username}, {'$set': {'xp': new_xp, 'level': level}})
    return "Win recorded", 200


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