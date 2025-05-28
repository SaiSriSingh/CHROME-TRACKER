from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'database.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/track', methods=['POST'])
def track():
    data = request.get_json()
    user = data.get('user', 'default')
    site = data.get('site')
    duration = int(data.get('duration', 0))
    date = str(datetime.now().date())

    db = load_data()
    if user not in db:
        db[user] = {}
    if date not in db[user]:
        db[user][date] = {}
    if site not in db[user][date]:
        db[user][date][site] = 0
    db[user][date][site] += duration
    save_data(db)
    return jsonify({'status': 'success'})

@app.route('/api/report/<user>')
def report(user):
    db = load_data()
    today = str(datetime.now().date())
    user_data = db.get(user, {}).get(today, {})
    
    productive_sites = ['chatgpt.com', 'github.com', 'stackoverflow.com']
    productive_time = sum(time for site, time in user_data.items() if site in productive_sites)
    total_time = sum(user_data.values())
    productivity = (productive_time / total_time * 100) if total_time else 0

    return jsonify({
        'date': today,
        'productive_time': productive_time,
        'total_time': total_time,
        'productivity': round(productivity, 2),
        'sites': user_data
    })

if __name__ == '__main__':
    app.run(debug=True)
