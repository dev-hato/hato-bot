FROM postgres:15.8-bullseye@sha256:d9ed7a8a6eab3291e094c11b5541a05ad441e853aafedc4103e7dd577f8ffa7f

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
