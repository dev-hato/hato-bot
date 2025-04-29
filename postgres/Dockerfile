FROM postgres:17.4-bullseye@sha256:4293270a8ee437ef619c38cea73459362f87359c323637cefc0f24e58ad05b64

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
