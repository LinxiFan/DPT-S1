#!/bin/bash
pandoc --from=markdown --to=rst --output=README.rst README.md
rm -rf dist/
python setup.py sdist bdist_wheel
twine upload dist/*
