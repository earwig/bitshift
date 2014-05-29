import json
from os import path

with open(path.join(path.dirname(__file__), "languages.json")) as lang_json:
    LANGS = [lang for lang in json.load(lang_json)["languages"]]
