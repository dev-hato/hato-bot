FROM postgres:17.5-bullseye@sha256:9f36e8c941802d381204caa52d94a030bc40f06788fc9bbbf33de2770d51865a

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
