#!/usr/bin/env bash

pip install -r requirements.txt
pipenv --version
pipenv install --dev
cp .env.example .env
pipenv run python -m unittest
