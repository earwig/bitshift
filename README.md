bitshift
========

bitshift is a semantic search engine for source code developed by Benjamin
Attal, Ben Kurtovic, and Severyn Kozak.

Branches
--------

- `master`: working, tested, version-numbered code - no direct commits; should
  only accept merges from `develop` when ready to release
- `develop`: integration branch with unreleased but mostly functional code -
  direct commits allowed but should be minor
- `feature/*`: individual components of the project with untested, likely
  horribly broken code - branch off from and merge into `develop` when done

Style
-----
bitshift uses [SASS][SASS] for styling; compile the stylesheets to CSS with
`sass --watch static/sass/:static/css`.

Documentation
-------------

To build documentation, run `make html` from the `docs` subdirectory. You can
then browse from `docs/build/html/index.html`.

To automatically update the API documentation structure (necessary when adding
new modules or packages, but *not* when adding functions or changing
docstrings), run `sphinx-apidoc -fo docs/source/api bitshift` from the project
root. Note that this will revert any custom changes made to the files in
`docs/source/api`, so you might want to update them by hand instead.

[SASS]: http://sass-lang.com/guide

Releasing
---------

- Update `__version__` in `bitshift/__init__.py`, `version` in `setup.py`, and
  `version` and `release` in `docs/conf.py`.
