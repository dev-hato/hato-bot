# バージョン情報に表示する commit hash を埋め込む
FROM debian:bullseye-slim AS commit-hash
COPY .git slackbot_settings.py /
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM python:3.12.4-slim-bullseye

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG ENV
ENV ENV="${ENV}"

WORKDIR /usr/src/app

COPY .npmrc .npmrc
COPY Pipfile Pipfile
COPY package.json package.json
COPY package-lock.json package-lock.json

# 必要なパッケージ
# * git, gcc, libc6-dev: Pythonライブラリのインストールの際に必要
# * curl: ヘルスチェックの際に必要
# * libopencv-dev, libgl1-mesa-dev, libglib2.0-0: OpenCV
# * gnupg: Node.jsのインストールの際に必要
# * nodejs: textlintを使用する際に必要
RUN apt-get update && \
    apt-get install -y --no-install-recommends git gcc libc6-dev && \
    pip install pipenv==2024.0.1 --no-cache-dir && \
    if [ "${ENV}" = 'dev' ]; then \
      pipenv install --system --skip-lock --dev || for d in /tmp/pipenv-*-requirements/; \
      do \
          for f in ${d}/pipenv-*-reqs.txt; \
          do \
              cat $f; \
          done; \
      done; \
    else \
      pipenv install --system --skip-lock || for d in /tmp/pipenv-*-requirements/; \
      do \
          for f in ${d}/pipenv-*-reqs.txt; \
          do \
              cat $f; \
          done; \
      done; \
    fi
