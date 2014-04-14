"""
Module to contain definitions of all Flask variables required by the app module.
"""

DEBUG = True
SECRET_KEY = "\x89\x87\x9a9\xab{\xda\xfe.28\xb4\x18\x01\x95]]\xd2\xeaen\xe0Ot"

LANG_PYTHON = 0
LANG_C = 1
LANG_JAVA = 2

PYG_IDS = {
    "Python": LANG_PYTHON,
    "C": LANG_C,
    "JAVA": LANG_JAVA
}
