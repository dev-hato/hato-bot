#!/usr/bin/env bash
set -e

# 環境ファイルを使ってenvにsetしている
# 参考URL: https://bit.ly/2KJhjqk
VENV_PATH=".venv"

# https://github.com/github/super-linter/issues/157#issuecomment-648850330
# -v "/home/runner/work/_temp/_github_workflow":"/github/workflow"
# ここに cp -r することで、super-linterのなかに.venvを配置できる
# また、元ディレクトリにも残っているので、キャッシュが作られる
cp -r "${VENV_PATH}" "${DEST_PATH}"
