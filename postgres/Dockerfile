FROM postgres:17.5-bullseye@sha256:1e86f394cf1cb6238e38d76f98804886978a371f67ff326b3b3370b3d6584ace

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
