#!/usr/bin/env bash
set -xe -o pipefail

# shellcheck disable=SC2034
TAG_NAME=$(git symbolic-ref --short HEAD | sed -e "s:/:-:g")

DOCKER_SERVICE_NAME=hato-bot
docker compose build "$DOCKER_SERVICE_NAME"
APP_NAME=$(yq '.app' fly.toml)
fly apps create --name="$APP_NAME"
grep -v DATABASE_URL .env | fly secrets import
POSTGRES_APP_NAME="${APP_NAME}-db"
fly postgres create --name="$POSTGRES_APP_NAME" --region="$(yq '.primary_region' fly.toml)" --initial-cluster-size=1 \
	--vm-size="$(yq '.vm.[0].size' fly.toml)" --volume-size=1
fly postgres attach "$POSTGRES_APP_NAME"
docker tag "$(docker compose images "$DOCKER_SERVICE_NAME" --format json | yq '.[0].ID')" tmp-hato-bot-flyio
fly deploy --local-only
