FROM postgres:15.8-bullseye@sha256:e78dfc1f39abc52cfb22c21fa101fa0f95b0bdae5928bdee5b034092295059a6

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
