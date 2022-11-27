#!/usr/bin/env bash

pipenv run autopep8 --exit-code --in-place --recursive .
pipenv run black --config .python-black .
pipenv run isort --sp .isort.cfg .
