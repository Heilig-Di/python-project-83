from flask import Flask, render_template, request, flash, redirect, url_for
import os
import psycopg2
import validators
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form.get('url')

    if not validators.url(url):
        flash('Некорректный URL', 'danger')
        return render_template("index.html"), 422

    if len(url) > 255:
        flash('Некорректный URL', 'danger')
        return render_template("index.html"), 422

    normalized_url = f'{urlparse(url).scheme}://{urlparse(url).netloc}'
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id from urls WHERE name = %s;',
                (normalized_url,)
            )
        flash('Страница уже существует', 'success')

        cur.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;',
            (normalized_url, datetime.now())
        )
        url_id = cur.fetchone()[0]
        conn.commit()
        flash('Страница успешно добавлена', 'success')

    return redirect(url_for('show_url', id=url_id))


@app.route('/urls')
def list_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM urls ORDER BY created_at DESC;')

        urls = cur.fetchall()
    return render_template('urls/index.html', urls=urls)


@app.route('/urls/<int:id>')
def show_url(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM urls WHERE id = %s;', (id,))
    return render_template('urls/show.html', url=cur.fetchone())
