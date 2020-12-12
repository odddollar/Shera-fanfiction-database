import bottle

app = bottle.Bottle()

@app.route("/")
@app.route("/home")
def home():
	return bottle.template("home.html")

@app.route("/submit")
def submit():
	return bottle.template("submit.html")

@app.route("/database")
def database():
	return bottle.template("database.html")

bottle.run(app, debug=True)