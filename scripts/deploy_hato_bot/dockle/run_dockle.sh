#!/usr/bin/env bash

for image_name in $(docker compose images | awk 'OFS=":" {print $2,$3}' | tail -n +2); do
  cmd="dockle --exit-code 1 "

  if [[ "${image_name}" =~ "postgres" ]]; then
    cmd+="-ak key "
  fi

  cmd+="${image_name}"
  echo "> ${cmd}"
  eval "${cmd}"
done
