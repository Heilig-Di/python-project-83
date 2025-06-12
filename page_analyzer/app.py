from flask import Flask, render_template, request, flash, redirect, url_for
import os
import psycopg2
import validators
import requests
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

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
    url = request.form.get("url")

    if not validators.url(url):
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422

    if len(url) > 255:
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422

    normalized_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id from urls WHERE name = %s;", (normalized_url,))
        flash("Страница уже существует", "success")

        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;",
            (normalized_url, datetime.now()),
        )
        url_id = cur.fetchone()[0]
        conn.commit()
        flash("Страница успешно добавлена", "success")

    return redirect(url_for("show_url", id=url_id))


@app.route("/urls")
def list_urls():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                        SELECT
                        u.id, u.name, uc.status_code, MAX(uc.created_at)
                        FROM urls as u
                        JOIN url_checks as uc ON u.id=uc.url_id
                        GROUP BY u.id, u.name, uc.status_code
                        ORDER BY u.id DESC;''')

        urls = cur.fetchall()
    return render_template("urls/index.html", urls=urls)


@app.route("/urls/<int:id>")
def show_url(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE id = %s;", (id,))
            url = cur.fetchone()

            cur.execute("""
                        SELECT url_id, created_at, status_code
                        FROM url_checks
                        WHERE url_id = %s;
                        """, (id,))
            checks = cur.fetchone()
    return render_template("urls/show.html", url=url, checks=checks)


@app.post("/urls/<int:id>/checks")
def check_id(id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s;", (id,))

                cur.execute(
                    """
                            INSERT INTO url_checks (url_id)
                            VALUES (%s)
                            RETURNING id;
                            """,
                    (id,),
                )
            conn.commit()
        flash("Страница успешно проверена", "success")

    except Exception as e:

        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("show_url", id=id))


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
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url', id=id))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO url_checks (url_id, status_code)
                        VALUES (%s, %s);
                        """, (id, status_code))
            conn.commit()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for("show_url", id=id))
