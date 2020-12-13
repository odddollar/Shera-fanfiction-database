import bottle
import sqlite3

app = bottle.Bottle()

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

	return bottle.template("submit.html", message="message")

@app.route("/database")
def database():
	con = sqlite3.connect("fanfictions.db")
	db = con.cursor()

	db.execute("SELECT * FROM fanfictions")
	result = db.fetchall()
	db.close()

	return bottle.template("database.html", rows=result)

bottle.run(app, debug=True)