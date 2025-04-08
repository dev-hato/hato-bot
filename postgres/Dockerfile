FROM postgres:15.12-bullseye@sha256:2ef61135a3bfe9fb3b9ba72f8c5b0afd79b70238f1f08fc040d438f3bffc08b3

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
