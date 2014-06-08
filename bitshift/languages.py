from os import path

import yaml

__all__ = ["LANGS", "LANGS_ALL"]

def _load_langs():
    filename = path.join(path.dirname(__file__), "languages.yml")
    with open(filename) as fp:
        data = yaml.load(fp)["languages"]
        langs = [it.keys()[0] if isinstance(it, dict) else it for it in data]
        all_langs = {}
        for i, lang in enumerate(data):
            if isinstance(lang, dict):
                for val in lang.values()[0]:
                    all_langs[val] = i
            else:
                all_langs[lang] = i
    return langs, all_langs

LANGS, LANGS_ALL = _load_langs()
