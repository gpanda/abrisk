#!/bin/sh
. ./venv.incl
mkdir -p "$VENV"

sudo pip install virtualenv
virtualenv $VENV
. $VENV/bin/activate
pip install requests requests_cache lxml
pip install future coverage pylint caniusepython3 tox
