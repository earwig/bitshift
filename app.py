from flask import Flask

app = Flask(__name__)
app.secret_key = "\x03#\xa8\xf3!\xddHd\x11\x8dx\xd9mR\xb2\xfb\x89LH^\x05\xe7\xc6F"

if __name__ == "__main__":
    app.run(debug=True)
