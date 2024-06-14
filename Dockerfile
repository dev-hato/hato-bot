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
    apt-get install -y --no-install-recommends git gcc libc6-dev libopencv-dev libgl1-mesa-dev libglib2.0-0 curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    pip install git+https://github.com/pypa/pipenv.git@66eef03cccc0901e830561ea45e97307adac95fa --no-cache-dir && \
    if [ "${ENV}" = 'dev' ]; then \
      pipenv install --system --skip-lock --dev; \
    else \
      pipenv install --system --skip-lock; \
    fi && \
    npm install && \
    pip uninstall -y pipenv virtualenv && \
    apt-get remove -y git gcc libc6-dev gnupg && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists ~/.cache /tmp /root/.npm /usr/src/app/node_modules/re2/.github/actions/*/Dockerfile && \
    find / -type f -perm /u+s -ignore_readdir_race -not -path '/sys/devices/virtual/powercap/*' -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -not -path '/sys/devices/virtual/powercap/*' -exec chmod g-s {} \; && \
    useradd -l -m -s /bin/bash -N -u "1000" "nonroot" && \
    chown -R nonroot /usr/src/app
USER nonroot

# Matplotlib用のフォントキャッシュ生成
RUN python -c 'import matplotlib.pyplot'

COPY *.py ./
COPY library library
COPY plugins plugins
COPY postgres/docker-entrypoint-initdb.d postgres/docker-entrypoint-initdb.d
COPY .textlintrc .textlintrc
COPY commands.txt commands.txt
COPY --from=commit-hash slackbot_settings.py slackbot_settings.py

ENV GIT_PYTHON_REFRESH=quiet
ENV NODE_OPTIONS="--max-old-space-size=512"
CMD ["python", "entrypoint.py"]
