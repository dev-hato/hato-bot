FROM postgres:17.5-bullseye@sha256:0f1dcc56d97d22a458ee1f36ddaf5a52a846fcaea8b195b7c125d482a926bbb0

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
