### Hexlet tests and linter status:
[![Actions Status](https://github.com/Heilig-Di/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Heilig-Di/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/e81bccb635287fce5741/maintainability)](https://codeclimate.com/github/Heilig-Di/python-project-83/maintainability)
# Привет!

### ***Это анализатор страниц***

Сайт анализирует указанные страницы на SEO-пригодность. Приложение позволяет проверять http-ответы, заголовки и мета-описания. А также хранит список проверок всех проанализированных URL.

Ссылка на приложение: [тык](https://python-project-83-mfjy.onrender.com/)

Получается? Отлично! :+1:

## ♦ Использование
Чтобы установить проект, клонируйте репозиторий:
```
git clone https://github.com/Heilig-Di/python-project-83.git
```
Для установки зависимостей запустите:
```
uv run flask --debug --app page_analyzer:app run
```
Инициализируйте базу данных:
```
psql -f database.sql
```
Запустите приложение:
```
uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
```
Для удаления проекта запустите:
```
rm -rf python-project-83
```
---
### **♦ Стек**
* Python
* Flask
* PostgreSQL
* Psycopg2
* BeautifulSoup4
* Requests

---

##### Готово

![Вы великолепны](//https://kartinkof.club/uploads/posts/2022-03/1648380246_5-kartinkof-club-p-mem-ti-potryasayushchii-5.jpg/200x100)

