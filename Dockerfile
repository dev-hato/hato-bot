# バージョン情報に表示する commit hash を埋め込む
FROM debian:buster-slim AS commit-hash
COPY . /
RUN apt-get update \
    && apt-get install -y  --no-install-recommends git \
    && sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM python:3.9.10-slim-buster

WORKDIR /usr/src/app

COPY Pipfile Pipfile

# Pythonライブラリのインストール時に必要なパッケージ (Pythonライブラリインストール後にアンインストール)
# * git: Pythonライブラリのインストールの際に必要
RUN apt-get update && \
    apt-get install -y  --no-install-recommends git && \
    pip install pipenv==2022.1.8 --no-cache-dir && \
    pipenv install --system --skip-lock && \
    pip uninstall -y pipenv virtualenv && \
    apt-get remove -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* ~/.cache

COPY *.py ./
COPY library library
COPY plugins plugins
COPY setup setup
COPY --from=commit-hash slackbot_settings.py slackbot_settings.py

ENV GIT_PYTHON_REFRESH=quiet
CMD ["python", "entrypoint.py"]
