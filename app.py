from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
import random
import string

app = Flask(__name__)

# Database setup
conn = sqlite3.connect('urls.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS url_shortener (
        id INTEGER PRIMARY KEY,
        original_url TEXT NOT NULL,
        short_url TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    return short_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        if not original_url.startswith(('http://', 'https://')):
            flash('URL must start with http:// or https://')
            return redirect(url_for('index'))

        # Check if the URL is already in the database
        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()
        cursor.execute("SELECT short_url FROM url_shortener WHERE original_url=?", (original_url,))
        existing_short_url = cursor.fetchone()

        if existing_short_url:
            conn.close()
            return render_template('index.html', short_url=existing_short_url[0])

        short_url = generate_short_url()

        cursor.execute("INSERT INTO url_shortener (original_url, short_url) VALUES (?, ?)",
                       (original_url, short_url))
        conn.commit()
        conn.close()
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_url>')
def redirect_to_original(short_url):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM url_shortener WHERE short_url=?", (short_url,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        flash('Short URL not found')
        return redirect(url_for('index'))


@app.route('/retrieve', methods=['GET'])
def retrieve_original():
    short_url = request.args.get('short_url')

    if short_url:
        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()
        cursor.execute("SELECT original_url FROM url_shortener WHERE short_url=?", (short_url,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return render_template('index.html', retrieved_url=result[0])
        else:
            flash('Short URL not found')
            return render_template('index.html')
    else:
        return render_template('index.html')


    


if __name__ == '__main__':
    app.run(debug=True)
