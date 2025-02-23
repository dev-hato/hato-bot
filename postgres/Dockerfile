FROM postgres:15.12-bullseye@sha256:fca5b5b71715e51f6fac4856c1c4624402047935593d433e99d117a6bb623406

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
