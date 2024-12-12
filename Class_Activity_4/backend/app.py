from flask import Flask, render_template, request, redirect
import sqlite3
from asgiref.wsgi import WsgiToAsgi  # ASGI wrapper for WSGI apps

app = Flask(__name__)

# Database initialization function
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        return redirect('/')

# Convert the Flask app to ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
