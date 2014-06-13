"""
Module to contain all the project's Flask server plumbing.
"""

import datetime
import flask

from json import dumps
from flask import Flask, make_response, render_template, request
from bitshift import assets
from bitshift.database import Database
from bitshift.languages import LANGS
from bitshift.query import parse_query, QueryParseException

app = Flask(__name__)
app.config.from_object("bitshift.config")
app.jinja_env.globals.update(year=datetime.datetime.now().year)

app_env = app.jinja_env
app_env.line_statement_prefix = "="
app_env.globals.update(assets=assets)

database = Database()

@app.route("/")
def index():
    return render_template("index.html", autocomplete_languages=LANGS)

@app.route("/search.json")
def search():
    def reply(json):
        resp = make_response(dumps(json))
        resp.mimetype = "application/json"
        return resp

    query, page = request.args.get("q"), request.args.get("p", 1)
    if not query:
        return reply({"error": "No query given"})
    try:
        tree = parse_query(query)
    except QueryParseException as exc:
        return reply({"error": exc.args[0]})
    try:
        page = int(page)
    except ValueError:
        return reply({"error": u"Invalid page number: %s" % page})
    count, codelets = database.search(tree, page)
    results = [clt.serialize() for clt in codelets]
    return reply({"count": count, "results": results})

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/developers")
def developers():
    return render_template("developers.html")

@app.route("/robots.txt")
@app.route("/sitemap.xml")
@app.route("/favicon.ico")
def static_from_root():
    return flask.send_from_directory(app.static_folder, request.path[1:])

if __name__ == "__main__":
    app.run(debug=True)
