#!/usr/bin/env bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask db upgrade
flask run --host=0.0.0.0 --debugger
