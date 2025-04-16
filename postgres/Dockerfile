FROM postgres:17.4-bullseye@sha256:39e97713cffa1428e1d27bfffc826d3724b7cf4a33ff6db7ca52974be3394de3

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
