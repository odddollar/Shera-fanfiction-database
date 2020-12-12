import bottle

app = bottle.Bottle()

@app.route("/")
def home():
	return bottle.template("home.html")

bottle.run(app)