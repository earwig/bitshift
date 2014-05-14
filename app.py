"""
Module to contain all the project's Flask server plumbing.
"""

from flask import Flask
from flask import render_template, session

from bitshift import assets
# from bitshift.database import Database
# from bitshift.query import parse_query

app = Flask(__name__)
app.config.from_object("bitshift.config")

app_env = app.jinja_env
app_env.line_statement_prefix = "="
app_env.globals.update(assets=assets)

# database = Database()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search/<query>")
def search(query):
    # tree = parse_query(query)
    # database.search(tree)
    pass

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/developers")
def developers():
    return render_template("developers.html")

if __name__ == "__main__":
    app.run(debug=True)
