"""
Module to contain all the project's Flask server plumbing.
"""

from flask import Flask
from flask import render_template, session

from bitshift import *

app = Flask(__name__)
app.config.from_object("bitshift.config")

app_env = app.jinja_env
app_env.line_statement_prefix = "="
app_env.globals.update(assets = assets)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
