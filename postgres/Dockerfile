FROM postgres:15.8-bullseye@sha256:c0b05052d521bd988c71dd6b170929ba80363f1fe8d06670d2647788bc2de200

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
