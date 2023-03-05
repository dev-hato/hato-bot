#!/usr/bin/env bash

cp .env.example .env
export TAG_NAME="${HEAD_REF//\//-}"
dockle_version="$(cat .dockle-version)"
curl -L -o dockle.deb "https://github.com/goodwithtech/dockle/releases/download/v${dockle_version}/dockle_${dockle_version}_Linux-64bit.deb"
sudo dpkg -i dockle.deb
docker compose pull
docker compose up -d

for image_name in $(docker compose images | awk 'OFS=":" {print $2,$3}' | tail -n +2); do
  cmd="dockle --exit-code 1 "

  if [[ "${image_name}" =~ "postgres" ]]; then
    cmd+="-ak key "
  elif [[ "${image_name}" =~ "hato-bot" ]]; then
    cmd+="-i CIS-DI-0006 "
  fi

  cmd+="${image_name}"
  echo "> ${cmd}"
  eval "${cmd}"
done
