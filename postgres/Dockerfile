FROM postgres:15.12-bullseye@sha256:2d5a9d911e37fb23b1a437e0ebd0eeefe6cb833b5a0073d1ab6fafcfad1e17ea

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
