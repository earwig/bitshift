from os import path

import yaml

with open(path.join(path.dirname(__file__), "languages.yml")) as lang_yaml:
    LANGS = [lang for lang in yaml.load(lang_yaml)["languages"]]
