FROM postgres:17.5-bullseye@sha256:4ad4c19c51d0b0a58da84b7399ab6e402a6512a44a6541232f56df9ef3d41f8d

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
