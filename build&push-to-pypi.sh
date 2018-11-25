#!/usr/bin/env bash

python setup.py sdist bdist_wheel
python -m twine upload dist/*
rm -r build/ dist/ prestige_irc.egg-info/
