import bottle
import sqlite3

app = bottle.Bottle()
db = sqlite3.connect("fanfictions.db")
db.execute("CREATE TABLE IF NOT EXISTS fanfictions (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, title TEXT, author TEXT, rating TEXT, warnings TEXT, summary TEXT, notes TEXT)")
db.commit()

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
	entry_data["summary"] = bottle.request.forms.get("summary")
	entry_data["notes"] = bottle.request.forms.get("notes")

	for i in entry_data.keys():
		if entry_data[i] is "":
			entry_data[i] = "N/A"
		if "'" in entry_data[i]:
			entry_data[i] = entry_data[i].replace("'", "")

	db = sqlite3.connect("fanfictions.db")
	db.execute(f"INSERT INTO fanfictions (url, title, author, rating, warnings, summary, notes) VALUES ('{entry_data['url']}', '{entry_data['title']}', '{entry_data['author']}', '{entry_data['rating']}', '{entry_data['warnings']}', '{entry_data['summary']}', '{entry_data['notes']}')")
	db.commit()

	return bottle.template("submit.html", message="Submitted!")

@app.route("/database")
def database():
	con = sqlite3.connect("fanfictions.db")
	db = con.cursor()

	db.execute("SELECT * FROM fanfictions")
	result = db.fetchall()
	db.close()

	return bottle.template("database.html", rows=result)

bottle.run(app, debug=True)