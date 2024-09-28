#!/usr/bin/env bash

cp .env.example .env
pipenv run python -m unittest
