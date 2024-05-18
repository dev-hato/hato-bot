#!/usr/bin/env bash
set -x

# この時点では必要な環境変数がセットされていないため、起動に失敗する (コマンドが異常終了する)
fly launch --copy-config --vm-memory=256mb -y
grep -v DATABASE_URL .env | fly secrets import

set -e
POSTGRES_APP_NAME="$(yq '.app' fly.toml)-db"
fly postgres create --name="$POSTGRES_APP_NAME" --region=nrt --initial-cluster-size=1 --vm-size=shared-cpu-1x --volume-size=1
fly postgres attach "$POSTGRES_APP_NAME"

# shellcheck disable=SC2046
fly machine start $(fly machine list --json | yq '.[].id' | tr "\n" ' ')
