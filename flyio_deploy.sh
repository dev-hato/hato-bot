#!/usr/bin/env bash
set -xe -o pipefail

APP_NAME=$(yq '.app' fly.toml)
fly apps create --name="$APP_NAME"
grep -v DATABASE_URL .env | fly secrets import
POSTGRES_APP_NAME="${APP_NAME}-db"
fly postgres create --name="$POSTGRES_APP_NAME" --region="$(yq '.primary_region' fly.toml)" --initial-cluster-size=1 \
	--vm-size="$(yq '.vm.[0].size' fly.toml)" --volume-size=1
fly postgres attach "$POSTGRES_APP_NAME"
fly deploy
