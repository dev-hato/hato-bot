# バージョン情報に表示する commit hash を埋め込む
FROM debian:bullseye-slim AS commit-hash
COPY . /
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM python:3.10.5-slim-bullseye

WORKDIR /usr/src/app

COPY Pipfile Pipfile

# 必要なパッケージ
# * git: Pythonライブラリのインストールの際に必要
# * curl: ヘルスチェックの際に必要
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    pip install pipenv==2022.6.7 --no-cache-dir && \
    pipenv install --system --skip-lock && \
    pip uninstall -y pipenv virtualenv && \
    apt-get remove -y git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists ~/.cache /tmp && \
    chmod u-s /bin/su && \
    chmod g-s /bin/su && \
    chmod u-s /bin/mount && \
    chmod g-s /bin/mount && \
    chmod u-s /usr/bin/wall && \
    chmod g-s /usr/bin/wall && \
    chmod u-s /usr/bin/expiry && \
    chmod g-s /usr/bin/expiry && \
    chmod u-s /sbin/unix_chkpwd && \
    chmod g-s /sbin/unix_chkpwd && \
    chmod u-s /usr/bin/chage && \
    chmod g-s /usr/bin/chage && \
    chmod u-s /usr/bin/passwd && \
    chmod g-s /usr/bin/passwd && \
    chmod u-s /usr/bin/chfn && \
    chmod g-s /usr/bin/chfn && \
    chmod u-s /bin/umount && \
    chmod g-s /bin/umount && \
    chmod u-s /usr/bin/chsh && \
    chmod g-s /usr/bin/chsh && \
    chmod u-s /usr/bin/newgrp && \
    chmod g-s /usr/bin/newgrp && \
    chmod u-s /usr/bin/gpasswd && \
    chmod g-s /usr/bin/gpasswd && \
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
