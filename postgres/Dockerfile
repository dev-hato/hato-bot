FROM postgres:15.12-bullseye@sha256:75f417a37e7dc124c9b8e99bba316cf84d976254e31d968ed91396c2409be009

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
