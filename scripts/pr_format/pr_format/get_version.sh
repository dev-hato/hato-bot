#!/usr/bin/env bash

echo "PYTHON_VERSION=$(cat .python-version)" >> "${GITHUB_ENV}"
sed -i -e "s/python_version = \".*\"/python_version = \"$(sed -e 's/\([0-9]*\.[0-9]*\).*/\1/g' .python-version)\"/g" Pipfile
