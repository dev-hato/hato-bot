#!/usr/bin/env bash

# 環境ファイルを使ってenvにsetしている
# 参考URL: https://bit.ly/2KJhjqk
venv_path=$(pipenv --venv)
echo "${venv_path}"
echo "venv_path=${venv_path}" >>"${GITHUB_ENV}"
