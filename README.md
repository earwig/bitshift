bitshift
========

bitshift is a semantic search engine for source code.

Documentation
-------------

To build documentation, run `make html` from the `docs` subdirectory. You can
then browse from `docs/build/html/index.html`.

To automatically update the API documentation structure (necessary when adding
new modules or packages, but *not* when adding functions or changing
docstrings), run `sphinx-apidoc -fo docs/source/api bitshift` from the project
root. Note that this will revert any custom changes made to the files in
`docs/source/api`, so you might want to update them by hand instead.
