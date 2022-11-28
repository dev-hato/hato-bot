#!/usr/bin/env bash

docker compose up -d --wait

# Dockerコンテナに疎通できるかテストする
curl http://localhost:3000/status
