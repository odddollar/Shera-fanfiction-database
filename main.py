import bottle

app = bottle.Bottle()

@app.route("/")
def home():
	with open("pages/home.html") as home_html:
		return "".join(home_html.readlines())

bottle.run(app)