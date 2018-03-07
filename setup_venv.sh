#!/bin/sh
pip install virtualenv
virtualenv --python="/usr/local/Cellar/python@2/2.7.14_1/bin/python2.7" .venv
. .venv/bin/activate
pip install requests
pip install future coverage pylint caniusepython3 tox
