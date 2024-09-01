from flask import Flask, request, redirect
import sqlite3
import os

app = Flask(__name__)
DATABASE = '/data/urls.db'

# Initialize the SQLite database
def init_db():
    """Create the database and the urls table if it doesn't exist."""
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
    """Generate a hash-based short URL identifier for a given original URL."""
    return str(hash(original_url) % 10000)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle URL shortening requests."""
    if request.method == 'POST':
        original_url = request.form['url']
        short_url = generate_short_url(original_url)

        # Ensure unique short URL
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
            conn.commit()
        except sqlite3.IntegrityError:
            # Handle the case where the short URL already exists
            cursor.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
            existing_url = cursor.fetchone()
            if existing_url and existing_url[0] == original_url:
                # If the short URL already exists for the same original URL, reuse it
                pass
            else:
                # Collision: generate a new short URL and insert again
                short_url = generate_short_url(original_url + str(os.urandom(16)))  # Slightly modify input to get a different hash
                cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
                conn.commit()

        conn.close()

        # Get the full URL, including the domain name and protocol
        full_short_url = request.url_root + short_url

        return f"Short URL is: <a href='{full_short_url}'>{full_short_url}</a>"
    
    return '''
        <form method="post">
            <label for="url">Enter URL:</label>
            <input type="text" id="url" name="url" required>
            <button type="submit">Shorten</button>
        </form>
    '''

@app.route('/<short_url>')
def redirect_to_original(short_url):
    """Redirect to the original URL based on the short URL identifier."""
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