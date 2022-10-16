# バージョン情報に表示する commit hash を埋め込む
FROM debian:bullseye-slim AS commit-hash
COPY . /
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM python:3.10.7-slim-bullseye

ARG ENV
ENV ENV="${ENV}"

WORKDIR /usr/src/app

COPY Pipfile Pipfile

# 必要なパッケージ
# * git: Pythonライブラリのインストールの際に必要
# * curl: ヘルスチェックの際に必要
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    pip install pipenv==2022.10.12 --no-cache-dir && \
    if [ "${ENV}" = 'dev' ]; then \
      pipenv install --system --skip-lock --dev; \
    else \
      pipenv install --system --skip-lock; \
    fi && \
    pip uninstall -y pipenv virtualenv && \
    apt-get remove -y git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists ~/.cache /tmp && \
    find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \; && \
    useradd -l -m -s /bin/bash -N -u "1000" "nonroot"
USER nonroot

COPY *.py ./
COPY library library
COPY plugins plugins
COPY postgres/docker-entrypoint-initdb.d postgres/docker-entrypoint-initdb.d
COPY --from=commit-hash slackbot_settings.py slackbot_settings.py

ENV GIT_PYTHON_REFRESH=quiet
HEALTHCHECK --interval=5s --retries=20 CMD ["curl", "-s", "-S", "-o", "/dev/null", "http://localhost:3000/status"]
CMD ["python", "entrypoint.py"]
