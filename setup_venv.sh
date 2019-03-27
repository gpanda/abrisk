#!/bin/sh
# make python3-dev (or python-dev for Python 2), libxml2-dev libxslt1-dev
# zlib1g-dev are installed

. ./venv.incl
mkdir -p "$VENV"

pip3 install virtualenv
virtualenv $VENV
. $VENV/bin/activate
pip3 install requests requests_cache lxml
pip3 install future coverage pylint caniusepython3 tox
