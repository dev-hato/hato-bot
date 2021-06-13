# バージョン情報に表示する commit hash を埋め込む
FROM alpine:3.13.5 AS commit-hash
COPY . /
RUN apk add --no-cache -U git
RUN sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM python:3.9.5-alpine3.12

WORKDIR /usr/src/app

COPY Pipfile Pipfile

# 実行時に必要なパッケージ (グループ名: .used-packages)
# * postgresql-libs: psycopg2を使用する際に必要
# * libjpeg-turbo: Pillowを使用する際に必要
#
# Pythonライブラリのインストール時に必要なパッケージ (グループ名: .build-deps, Pythonライブラリインストール後にアンインストール)
# * jpeg-dev, zlib-dev: Pillowのインストールの際に必要
# * gcc, musl-dev, postgresql-dev: psycopg2のインストールの際に必要
# * git: Pythonライブラリのインストールの際に必要
RUN apk add --no-cache -t .used-packages postgresql-libs libjpeg-turbo && \
    apk add --no-cache -t .build-deps jpeg-dev zlib-dev gcc musl-dev postgresql-dev git && \
    pip install pipenv==2020.8.13 --no-cache-dir && \
    pipenv install --system --skip-lock && \
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
