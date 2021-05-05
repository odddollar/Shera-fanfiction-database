import bottle
import psycopg2
import os
import requests
from bs4 import BeautifulSoup

# create bottle app
app = bottle.Bottle()

# determine if running locally and setup database
if os.environ.get("APP_LOCATION") == "heroku":
	DATABASE_URL = os.environ.get("DATABASE_URL")
else:
	conn = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	DATABASE_URL = ""
	
	# create test table
	db_check = conn.cursor()
	db_check.execute("CREATE TABLE IF NOT EXISTS fanfictions (id SERIAL PRIMARY KEY, url TEXT, title TEXT, author TEXT, rating TEXT, warnings TEXT, universe TEXT, summary TEXT, notes TEXT, completion TEXT)")
	conn.commit()
	conn.close()

# function to check completion status of fic
def check_completion_status(url):
	headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

	# get html from page
	req = requests.get(url, headers=headers).text
	soup = BeautifulSoup(req, "html.parser")

	# search for chapter status
	chps = soup.find_all("dd", class_="chapters")[0].text
	chapters = chps.split("/")[0]
	out_of = chps.split("/")[1]

	# return complete or incomplete
	if out_of == "?" or int(chapters) != int(out_of):
		return "Incomplete"
	else:
		return "Complete"

# show home page
@app.route("/")
def home():
	return bottle.template("home.html")

# show submit page
@app.route("/submit")
def submit():
	return bottle.template("submit.html", message="")

# handle postback from submit form
@app.route("/submit", method="POST")
def submit_handler():
	entry_data = {}

	# get data from posted back form
	entry_data["url"] = bottle.request.forms.url
	entry_data["title"] = bottle.request.forms.title
	entry_data["author"] = bottle.request.forms.author
	entry_data["rating"] = bottle.request.forms.rating
	entry_data["warnings"] = bottle.request.forms.warnings
	entry_data["universe"] = bottle.request.forms.universe
	entry_data["summary"] = bottle.request.forms.summary
	entry_data["notes"] = bottle.request.forms.notes
	entry_data["completion"] = check_completion_status(entry_data["url"])

	# remove invalid characters
	for i in entry_data.keys():
		if entry_data[i] is "":
			entry_data[i] = "N/A"
		entry_data[i] = entry_data[i].replace("'", "")

	# prevent leaving fields unfilled
	if (not "archiveofourown.org" in entry_data["url"]) or (entry_data["title"] == "N/A") or (entry_data["author"] == "N/A")  or (entry_data["summary"] == "N/A"):
		return bottle.template("submit.html", message="unfilled")

	# connect to database
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	# insert data into database
	db = con.cursor()
	db.execute(f"INSERT INTO fanfictions (url, title, author, rating, warnings, universe, summary, notes, completion) VALUES ('{entry_data['url']}', '{entry_data['title']}', '{entry_data['author']}', '{entry_data['rating']}', '{entry_data['warnings']}', '{entry_data['universe']}', '{entry_data['summary']}', '{entry_data['notes']}', '{entry_data['completion']}')")
	con.commit()
	con.close()

	return bottle.template("submit.html", message="success")

# show database page
@app.route("/database")
def database():
	# connect to database
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	# get all entries, number of complete and incomplete
	db = con.cursor()
	db.execute("SELECT * FROM fanfictions ORDER BY id")
	result = db.fetchall()
	db.execute("SELECT * FROM fanfictions WHERE completion='Complete'")
	complete = db.fetchall()
	db.execute("SELECT * FROM fanfictions WHERE completion='Incomplete'")
	incomplete = db.fetchall()
	con.close()

	return bottle.template("database.html", rows=result, complete=complete, incomplete=incomplete)

# handle postback from update completion function
@app.route("/database", method="POST")
def update_completion():
	# connect to database
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	# get all database entries ordered by id
	db = con.cursor()
	db.execute("SELECT * FROM fanfictions ORDER BY id")
	result = db.fetchall()

	# iterate through records
	for record in result:
		# check completion status
		completion_status = check_completion_status(record[1])
		
		# update completion status
		db = con.cursor()
		db.execute(f"UPDATE fanfictions SET completion='{completion_status}' WHERE id={record[0]}")

	# commit to database
	con.commit()
	con.close()

	return bottle.redirect("/database")

# show update page
@app.route("/update")
def render_update():
	return bottle.template("update.html")

# handle postback from update form
@app.route("/update", method="POST")
def update():
	data = {}

	# get data from form postback
	data["id"] = bottle.request.forms.id
	data["column"] = bottle.request.forms.column
	data["value"] = bottle.request.forms.value

	# replace bad characters
	data["value"] = data["value"].replace("'", "")

	# connect to database
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	# update database with new record information
	db = con.cursor()
	db.execute(f"UPDATE fanfictions SET {data['column']}='{data['value']}' WHERE id={data['id']}")
	con.commit()
	con.close()

	# redirect back to home page
	return bottle.redirect("/")

# run remove functionality
@app.route("/remove/<entry_id>")
def remove(entry_id):
	# connect to database
	if DATABASE_URL == "":
		con = psycopg2.connect(database="fanfictions", user="postgres", password="95283", host="172.17.0.1", port="5432")
	else:
		con = psycopg2.connect(DATABASE_URL, sslmode="require")

	# remove record from database based on given ID
	db = con.cursor()
	db.execute(f"DELETE FROM fanfictions WHERE id={entry_id}")
	con.commit()
	con.close()

	return bottle.template("remove.html", id=entry_id)

# host static files (png, jpeg and ico)
@app.route("/images/<filename:re:.*\.(png|jpg|ico)>")
def image(filename):
	return bottle.static_file(filename, root="images/")

# run app locally or on heroku
if os.environ.get("APP_LOCATION") == "heroku":
	bottle.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
	bottle.run(app, host="0.0.0.0", port=8080, debug=True)
	