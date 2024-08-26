from flask import Flask, request, redirect
import sqlite3
import os

app = Flask(__name__)
DATABASE = '/data/urls.db'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_url TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Function to generate a short URL identifier
def generate_short_url(original_url):
    return str(hash(original_url) % 10000)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = generate_short_url(original_url)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
        conn.commit()
        conn.close()

        return f"Short URL is: <a href='/{short_url}'>/{short_url}</a>"
    
    return '''
        <form method="post">
            <label for="url">Enter URL:</label>
            <input type="text" id="url" name="url" required>
            <button type="submit">Shorten</button>
        </form>
    '''

@app.route('/<short_url>')
def redirect_to_original(short_url):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return redirect(row[0])
    else:
        return "URL not found!", 404

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5000)
