FROM postgres:17.5-bullseye@sha256:f55b60b8b630b8b8b104a6dcd346d82adfce73c7db0bec94bff7f4ce8b528089

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
