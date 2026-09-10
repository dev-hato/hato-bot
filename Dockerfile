FROM ghcr.io/astral-sh/uv:0.12.7-python3.14-trixie-slim@sha256:0e664b12a6be9cd16be1015ec5cc3feebdeb42078ab587389707afbdfab8b10f AS base

# バージョン情報に表示する commit hash を埋め込む
FROM base AS commit-hash
COPY .git slackbot_settings.py /
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && sed -i "s/^\(GIT_COMMIT_HASH = \).*\$/\1'$(git rev-parse HEAD)'/" slackbot_settings.py

FROM base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG ENV
ENV ENV="${ENV}"

WORKDIR /usr/src/app

COPY .npmrc .npmrc
COPY package.json package.json
COPY package-lock.json package-lock.json

# 必要なパッケージ
# * git: Pythonライブラリのインストールの際に必要
# * curl: ヘルスチェックの際に必要
# * libopencv-dev, libgl1-mesa-dev, libglib2.0-0: OpenCV
# * gnupg: Node.jsのインストールの際に必要
# * build-essential: numpyのインストールの際に必要
#                    TODO: numpyをPython 3.14に対応したバージョンへアップデートしたら削除
# * nodejs: textlintを使用する際に必要
RUN apt-get update && \
    apt-get install -y --no-install-recommends git libopencv-dev libgl1-mesa-dev libglib2.0-0 curl gnupg build-essential && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_24.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    npm ci && \
    apt-get remove -y gnupg && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists ~/.cache /tmp/* /root/.npm /usr/src/app/node_modules/re2/.github/actions/*/Dockerfile && \
    find / -type f -perm /u+s -ignore_readdir_race -not -path '/sys/devices/virtual/powercap/*' -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -not -path '/sys/devices/virtual/powercap/*' -exec chmod g-s {} \; && \
    useradd -l -m -s /bin/bash -N -u "1000" "nonroot" && \
    chown -R nonroot /usr/src/app

USER nonroot

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN if [ "${ENV}" = 'dev' ]; then \
      uv sync --frozen --dev; \
    else \
      uv sync --frozen; \
    fi && \
    rm -rf ~/.cache

USER root

RUN apt-get remove -y git build-essential && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists ~/.cache /tmp/*

USER nonroot

# Matplotlib用のフォントキャッシュ生成
RUN echo 'import matplotlib.pyplot' | uv run - && \
    rm -rf /tmp/*

COPY *.py ./
COPY library library
COPY plugins plugins
COPY postgres/docker-entrypoint-initdb.d postgres/docker-entrypoint-initdb.d
COPY .textlintrc .textlintrc
COPY commands.txt commands.txt
COPY --from=commit-hash slackbot_settings.py slackbot_settings.py

ENV GIT_PYTHON_REFRESH=quiet
ENV NODE_OPTIONS="--max-old-space-size=512"
CMD ["uv", "run", "entrypoint.py"]
