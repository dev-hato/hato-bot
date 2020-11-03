# バージョン情報に表示する commit hash を埋め込む
FROM alpine:3.12 AS commit-hash
COPY . .
RUN apk add --no-cache -U git=2.26.2-r0
RUN sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM python:3.8.6-alpine3.12

WORKDIR /usr/src/app

COPY Pipfile Pipfile
COPY Pipfile.lock-3.8 Pipfile.lock

# 実行時に必要なパッケージ (グループ名: .used-packages)
# * postgresql-libs: psycopg2を使用する際に必要
#
# Pythonライブラリのインストール時に必要なパッケージ (グループ名: .build-deps, Pythonライブラリインストール後にアンインストール)
# * jpeg-dev, zlib-dev: Pillowのインストールの際に必要
# * gcc, musl-dev, postgresql-dev: psycopg2のインストールの際に必要
# * git: Pythonライブラリのインストールの際に必要
RUN apk add --no-cache -t .used-packages postgresql-libs=12.4-r0 && \
    apk add --no-cache -t .build-deps jpeg-dev=9d-r0 zlib-dev=1.2.11-r3 gcc=9.3.0-r2 musl-dev=1.1.24-r9 postgresql-dev=12.4-r0 git=2.26.2-r0 && \
    pip install pipenv==2020.8.13 --no-cache-dir && \
    pipenv install --system && \
    pip uninstall -y pipenv virtualenv && \
    apk --purge del .build-deps && \
    rm -rf ~/.cache

COPY *.py ./
COPY library library
COPY plugins plugins
COPY setup setup
COPY --from=commit-hash slackbot_settings.py slackbot_settings.py

ENV GIT_PYTHON_REFRESH=quiet
CMD ["python", "entrypoint.py"]
