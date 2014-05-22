import json

with open("bitshift/resources/languages.json") as lang_json:
    LANGS = [lang.encode("ascii","ignore") for lang in
            json.load(lang_json)["languages"]]
