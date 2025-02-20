#!/usr/bin/env bash

uv_version=$(grep ghcr.io/astral-sh/uv: Dockerfile | sed -e 's!FROM ghcr.io/astral-sh/uv:\([0-9.]*\)-.*!\1!g')
sed -i -e "s/required-version = .*/required-version = \"$uv_version\"/g" pyproject.toml
