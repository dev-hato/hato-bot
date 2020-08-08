#!/bin/sh

set -e -o pipefail

# PostgreSQLの起動を待機する
pipenv run python wait_db.py

pipenv run python create_env.py

pipenv run python run.py
