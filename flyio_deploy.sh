#!/usr/bin/env bash
set -x

# この時点では必要な環境変数がセットされていないため、起動に失敗する (コマンドが異常終了する)
fly launch --copy-config --vm-memory=256mb -y

set -e
POSTGRES_APP_NAME="$(yq '.app' fly.toml)-db"
fly postgres create --name="$POSTGRES_APP_NAME" --region="$(yq '.primary_region' fly.toml)" --initial-cluster-size=1 \
	--vm-size="$(yq '.vm.[0].size' fly.toml)" --volume-size=1
fly postgres attach "$POSTGRES_APP_NAME"
sleep 60
grep -v DATABASE_URL .env | fly secrets import
sleep 60

# shellcheck disable=SC2046
fly machine start $(fly machine list --json | yq '.[].id' | tr "\n" ' ')
