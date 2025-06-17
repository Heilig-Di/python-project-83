from flask import Flask, render_template, request, flash, redirect, url_for
import os
import psycopg2
import validators
import requests
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup

load_dotenv()
app = Flask(__name__, template_folder="../templates")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls", methods=["POST"])
def add_url():
    url = request.form.get("url", "").strip()

    if not url or not validators.url(url):
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422

    if len(url) > 255:
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422

    normalized_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id from urls WHERE name = %s;", (normalized_url,))
            url_record = cur.fetchone()

            if url_record:
                flash("Страница уже существует", "success")
                return redirect(url_for("show_url", id=url_record[0]))
            else:
                cur.execute(
                    "INSERT INTO urls (name, created_at) VALUES (%s, CURRENT_DATE) RETURNING id, created_at;",
                    (normalized_url,),
                )
                new_record = cur.fetchone()
                conn.commit()
                flash("Страница успешно добавлена", "success")
                return redirect(url_for("show_url", id=new_record[0]))


@app.route("/urls")
def list_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                        SELECT
                            u.id,
                            u.name,
                            MAX(uc.created_at),
                            (SELECT status_code
                            FROM url_checks
                            WHERE url_id=u.id
                            ORDER BY created_at DESC
                            LIMIT 1) as last_status
                        FROM urls as u
                        LEFT JOIN url_checks as uc ON u.id=uc.url_id
                        GROUP BY u.id
                        ORDER BY u.id DESC;''')

            urls = cur.fetchall()
            conn.commit()
    return render_template("urls/index.html", urls=urls)


@app.route("/urls/<int:id>")
def show_url(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s;", (id,))
            url = cur.fetchone()

            cur.execute("""
                        SELECT *
                        FROM url_checks
                        WHERE url_id = %s;
                        """, (id,))
            checks = cur.fetchall()
            conn.commit()
    return render_template("urls/show.html", url=url, checks=checks)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM urls WHERE id = %s;", (id,))
            url_record = cur.fetchone()

            if not url_record:
                flash("Страница не найдена", "danger")
                return redirect(url_for('list_urls'))

            url = url_record[0]

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        status_code = response.status_code
        soup = BeautifulSoup(response.text, 'lxml')

        h1 = (soup.find('h1')).get_text(strip=True) if soup.find('h1') else None
        title = (soup.find('title')).get_text(strip=True) if soup.find('title') else None

        meta = soup.find('meta', attrs={"name": "description"})
        description = meta['content'].strip() if meta and meta.get('content') else None

    except requests.exceptions.HTTPError:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for("show_url", id=id))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO url_checks (url_id, status_code, h1, title, description)
                        VALUES (%s, %s, %s, %s, %s);
                        """, (id, status_code, h1, title, description))

    flash('Страница успешно проверена', 'success')
    conn.commit()
    return redirect(url_for("show_url", id=id))
