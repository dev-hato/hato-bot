FROM alpine AS commit-hash
COPY .git .
RUN apk add -U git
RUN echo "GIT_COMMIT_HASH=$(git rev-parse HEAD)" >> .env

FROM python:3.8.5-alpine

ENV WORKON_HOME=/usr/src/venv

WORKDIR /usr/src/app

COPY Pipfile Pipfile
COPY Pipfile.lock-3.8 Pipfile.lock

# 実行時に必要なパッケージ (グループ名: .used-packages)
# * postgresql-libs: psycopg2を使用する際に必要
#
# Pythonライブラリのインストール時に必要なパッケージ (グループ名: .build-deps, Pythonライブラリインストール後にアンインストール)
# * jpeg-dev, zlib-dev: Pillowのインストールの際に必要
# * gcc, musl-dev, postgresql-dev: psycopg2のインストールの際に必要
RUN apk add --no-cache -t .used-packages postgresql-libs=12.4-r0 && \
    apk add --no-cache -t .build-deps jpeg-dev=9d-r0 zlib-dev=1.2.11-r3 gcc=9.3.0-r2 musl-dev=1.1.24-r9 postgresql-dev=12.4-r0 git=2.26.2-r0 && \
    pip install pipenv==2020.6.2 --no-cache-dir && \
    pipenv install --system && \
    apk --purge del .build-deps

COPY --from=commit-hash .env .
COPY *.py library plugins .

CMD ["python", "entrypoint.py"]
