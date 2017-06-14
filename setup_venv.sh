#!/bin/sh
pip install virtualenv
virtualenv .venv
. .venv/bin/activate
pip install requests
pip install futures
