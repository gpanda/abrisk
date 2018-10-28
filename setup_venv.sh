#!/bin/sh
# make python3-dev (or python-dev for Python 2), libxml2-dev libxslt1-dev
# zlib1g-dev are installed

. ./venv.incl
mkdir -p "$VENV"

pip install virtualenv
virtualenv $VENV
. $VENV/bin/activate
pip install requests requests_cache lxml
pip install future coverage pylint caniusepython3 tox
