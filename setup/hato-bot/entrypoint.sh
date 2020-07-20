#!/bin/sh

# PostgreSQLの起動を待機する
RETRIES=10
until psql $DATABASE_URL -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES-=1)) remaining attempts..."
  sleep 1
done

# pip install pipenv==2020.6.2 --no-cache-dir && pipenv install

pipenv run python create_env.py

pipenv run python run.py
