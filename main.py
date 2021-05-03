import bottle
import psycopg2
import os
import requests
from bs4 import BeautifulSoup

app = bottle.Bottle()

if os.environ.get("APP_LOCATION") == "heroku":
	DATABASE_URL = os.environ.get("DATABASE_URL")
	conn = psycopg2.connect(DATABASE_URL, sslmode="require")
else:
	conn = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	DATABASE_URL = ""
	
	db_check = conn.cursor()
	db_check.execute("CREATE TABLE IF NOT EXISTS fanfictions (id SERIAL PRIMARY KEY, url TEXT, title TEXT, author TEXT, rating TEXT, warnings TEXT, universe TEXT, summary TEXT, notes TEXT, completion TEXT)")
	conn.commit()
	conn.close()

@app.route("/")
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

	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	db = con.cursor()
	db.execute(f"INSERT INTO fanfictions (url, title, author, rating, warnings, universe, summary, notes, completion) VALUES ('{entry_data['url']}', '{entry_data['title']}', '{entry_data['author']}', '{entry_data['rating']}', '{entry_data['warnings']}', '{entry_data['universe']}', '{entry_data['summary']}', '{entry_data['notes']}', 'Unknown')")
	con.commit()
	con.close()

	return bottle.template("submit.html", message="success")

@app.route("/database")
def database():
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	db = con.cursor()
	db.execute("SELECT * FROM fanfictions ORDER BY id")
	result = db.fetchall()
	db.execute("SELECT * FROM fanfictions WHERE completion='Complete'")
	complete = db.fetchall()
	db.execute("SELECT * FROM fanfictions WHERE completion='Incomplete'")
	incomplete = db.fetchall()
	con.close()

	return bottle.template("database.html", rows=result, complete=complete, incomplete=incomplete)

@app.route("/remove/<entry_id>")
def remove(entry_id):
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	db = con.cursor()
	db.execute(f"DELETE FROM fanfictions WHERE id={entry_id}")
	con.commit()
	con.close()

	return bottle.template("remove.html", id=entry_id)

@app.route("/update")
def render_update():
	return bottle.template("update.html")

@app.route("/update", method="POST")
def update():
	data = {}

	data["id"] = bottle.request.forms.get("id")
	data["column"] = bottle.request.forms.get("column")
	data["value"] = bottle.request.forms.get("value")

	if "'" in data["value"]:
		data["value"] = data["value"].replace("'", "")

	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	db = con.cursor()
	db.execute(f"UPDATE fanfictions SET {data['column']}='{data['value']}' WHERE id={data['id']}")
	con.commit()
	con.close()

	return bottle.redirect("/")

@app.route("/completion")
def update_completions():
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	db = con.cursor()
	db.execute("SELECT * FROM fanfictions ORDER BY id")
	result = db.fetchall()

	headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

	def check_completion_status(url):
		req = requests.get(url, headers=headers).text
		soup = BeautifulSoup(req, "html.parser")

		chps = soup.find_all("dd", class_="chapters")[0].text
		chapters = chps.split("/")[0]
		out_of = chps.split("/")[1]

		if out_of == "?" or int(chapters) != int(out_of):
			return "Incomplete"
		else:
			return "Complete"

	for entry in result:
		completion_status = check_completion_status(entry[1])
		db = con.cursor()
		db.execute(f"UPDATE fanfictions SET completion='{completion_status}' WHERE id={entry[0]}")

	con.commit()
	con.close()

	return bottle.redirect("/database")

@app.route("/images/<filename:re:.*\.(png|jpg|ico)>")
def image(filename):
	return bottle.static_file(filename, root="images/")

if os.environ.get("APP_LOCATION") == "heroku":
	bottle.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
	bottle.run(app, host="0.0.0.0", port=8080, debug=True)