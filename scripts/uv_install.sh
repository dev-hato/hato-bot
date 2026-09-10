#!/usr/bin/env bash
set -e

uv --version
uv python install
uv sync --dev
