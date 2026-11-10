#!/usr/bin/env bash

export FLASK_APP=wsgi:app
flask db init
flask db migrate -m "init products"
sed -i "s/sa.text('(CURRENT_TIMESTAMP)')/sa.func.now()/" migrations/versions/*.py
flask db upgrade

flask run
