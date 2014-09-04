#!/usr/bin/env python

from json import loads
from sys import argv
from urllib import urlencode
from urllib2 import urlopen

def get_function(name):
    params = {"q": "lang:python and func:def:%s" % name}
    request = urlopen("http://bitshift.it/search.json?" + urlencode(params))
    res = loads(request.read())["results"]
    if res:
        print "%s: %s" % (name, res[0]["url"])
    else:
        print "%s not found." % name

if __name__ == "__main__":
    if len(argv) == 2:
        get_function(argv[1])
