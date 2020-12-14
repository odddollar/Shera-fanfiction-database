import bottle
import sqlite3

app = bottle.Bottle()
db_check = sqlite3.connect("fanfictions.db")
db_check.execute("CREATE TABLE IF NOT EXISTS fanfictions (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, title TEXT, author TEXT, rating TEXT, warnings TEXT, universe TEXT, summary TEXT, notes TEXT)")
db_check.commit()

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

	db = sqlite3.connect("fanfictions.db")
	db.execute(f"INSERT INTO fanfictions (url, title, author, rating, warnings, universe, summary, notes) VALUES ('{entry_data['url']}', '{entry_data['title']}', '{entry_data['author']}', '{entry_data['rating']}', '{entry_data['warnings']}', '{entry_data['universe']}', '{entry_data['summary']}', '{entry_data['notes']}')")
	db.commit()

	return bottle.template("submit.html", message="success")

@app.route("/database")
def database():
	con = sqlite3.connect("fanfictions.db")
	db = con.cursor()

	db.execute("SELECT * FROM fanfictions")
	result = db.fetchall()
	db.close()

	return bottle.template("database.html", rows=result)

@app.route("/remove/<entry_id>")
def remove(entry_id):
	db = sqlite3.connect("fanfictions.db")
	db.execute(f"DELETE FROM fanfictions WHERE id={entry_id}")
	db.commit()

	return bottle.template("remove.html", id=entry_id)

bottle.run(app, debug=True)