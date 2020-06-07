#!/bin/sh

# PostgreSQL起動待機
RETRIES=10
until psql $DATABASE_URL -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for postgres server, $((RETRIES-=1)) remaining attempts..."
  sleep 1
done

pipenv run python create_env.py

pipenv run python run.py
