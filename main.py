import bottle
import psycopg2
import os

app = bottle.Bottle()

if os.environ.get("APP_LOCATION") == "heroku":
	DATABASE_URL = os.environ.get("DATABASE_URL")
	conn = psycopg2.connect(DATABASE_URL, sslmode="require")
	conn.autocommit = True
	temp_db = conn.cursor()
	temp_db.execute("CREATE DATABASE fanfictions")
else:
	conn = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="localhost", port="5432")

db_check = conn.cursor()
db_check.execute("CREATE TABLE IF NOT EXISTS fanfictions (id SERIAL PRIMARY KEY, url TEXT, title TEXT, author TEXT, rating TEXT, warnings TEXT, universe TEXT, summary TEXT, notes TEXT)")
conn.commit()
conn.close()

@app.route("/")
@app.route("/home")
def home():
	return bottle.template("home.html")

@app.route("/submit")
def submit():
	return bottle.template("submit.html", message="")

@app.route("/submit", method="POST")
def submit_handler():
	entry_data = {}

	entry_data["url"] = bottle.request.forms.get("url")
	entry_data["title"] = bottle.request.forms.get("title")
	entry_data["author"] = bottle.request.forms.get("author")
	entry_data["rating"] = bottle.request.forms.get("rating")
	entry_data["warnings"] = bottle.request.forms.get("warnings")
	entry_data["universe"] = bottle.request.forms.get("universe")
	entry_data["summary"] = bottle.request.forms.get("summary")
	entry_data["notes"] = bottle.request.forms.get("notes")

	for i in entry_data.keys():
		if entry_data[i] is "":
			entry_data[i] = "N/A"
		if "'" in entry_data[i]:
			entry_data[i] = entry_data[i].replace("'", "")

	if (not "archiveofourown.org" in entry_data["url"]) or (entry_data["title"] == "N/A") or (entry_data["author"] == "N/A")  or (entry_data["summary"] == "N/A"):
		return bottle.template("submit.html", message="unfilled")

	con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="localhost", port="5432")
	db = con.cursor()
	db.execute(f"INSERT INTO fanfictions (url, title, author, rating, warnings, universe, summary, notes) VALUES ('{entry_data['url']}', '{entry_data['title']}', '{entry_data['author']}', '{entry_data['rating']}', '{entry_data['warnings']}', '{entry_data['universe']}', '{entry_data['summary']}', '{entry_data['notes']}')")
	con.commit()
	con.close()

	return bottle.template("submit.html", message="success")

@app.route("/database")
def database():
	con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="localhost", port="5432")
	db = con.cursor()

	db.execute("SELECT * FROM fanfictions")
	result = db.fetchall()
	con.close()

	return bottle.template("database.html", rows=result)

@app.route("/remove/<entry_id>")
def remove(entry_id):
	con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="localhost", port="5432")
	db = con.cursor()
	db.execute(f"DELETE FROM fanfictions WHERE id={entry_id}")
	con.commit()
	con.close()

	return bottle.template("remove.html", id=entry_id)

if os.environ.get("APP_LOCATION") == "heroku":
	bottle.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
	bottle.run(app, host="localhost", port=8080, debug=True)