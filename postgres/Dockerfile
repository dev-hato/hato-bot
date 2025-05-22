FROM postgres:17.5-bullseye@sha256:c0f0deb00d1ed368b1ba98ce1e4982961e86fb9d8c2b02a0d5bbb4cb6cd5319f

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
