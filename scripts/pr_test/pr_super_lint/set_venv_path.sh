#!/usr/bin/env bash

# 環境ファイルを使ってenvにsetしている
# 参考URL: https://bit.ly/2KJhjqk
venv_path=$(pipenv --venv)
echo "${venv_path}"
VENV_PATH="${venv_path}"

# https://github.com/github/super-linter/issues/157#issuecomment-648850330
# -v "/home/runner/work/_temp/_github_workflow":"/github/workflow"
# ここに cp -r することで、super-linterのなかに.venvを配置できる
# また、元ディレクトリにも残っているので、キャッシュが作られる
cp -r "${VENV_PATH}" "${DEST_PATH}"
