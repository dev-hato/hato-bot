# バージョン情報に表示する commit hash を埋め込む
FROM debian:bullseye-slim AS commit-hash
COPY . /
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM python:3.10.4-slim-bullseye

WORKDIR /usr/src/app

COPY Pipfile Pipfile

# 必要なパッケージ
# * git: Pythonライブラリのインストールの際に必要
# * curl: ヘルスチェックの際に必要
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    pip install pipenv==2022.5.2 --no-cache-dir && \
    pipenv install --system --skip-lock && \
    pip uninstall -y pipenv virtualenv && \
    apt-get remove -y git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* ~/.cache tmp/* \
    && for f in /bin/su /bin/mount /usr/bin/wall /usr/bin/expiry /sbin/unix_chkpwd /usr/bin/chage \
             /usr/bin/passwd /usr/bin/chfn /bin/umount /usr/bin/chsh /usr/bin/newgrp /usr/bin/gpasswd; do \
      chmod u-s "${f}"; \
      chmod u-g "${f}"; \
    done \
    && useradd -l -m -s /bin/bash -N -u "1000" "nonroot"
USER nonroot

COPY *.py ./
COPY library library
COPY plugins plugins
COPY postgres/docker-entrypoint-initdb.d postgres/docker-entrypoint-initdb.d
COPY --from=commit-hash slackbot_settings.py slackbot_settings.py

ENV GIT_PYTHON_REFRESH=quiet
HEALTHCHECK CMD curl -s -S -o /dev/null http://localhost:3000/status || exit 1
CMD ["python", "entrypoint.py"]
