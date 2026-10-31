#!/usr/bin/env bash
set -e

cp .env.example .env
uv run python -m unittest
