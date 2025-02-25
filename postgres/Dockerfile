FROM postgres:15.12-bullseye@sha256:dc830f20b2b954362edb12435823fee829fcb9eacd6f557fa5fb5a35a8cddfcc

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
