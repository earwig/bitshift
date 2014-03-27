from flask import Flask
from flask import render_template

app = Flask(__name__)

env = app.jinja_env
app.jinja_env.line_statement_prefix = "="

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
