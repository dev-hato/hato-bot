FROM postgres:15.11-bullseye@sha256:c8a0c919df63355915452953d78e102cce6203a5e967bf1afaa45afa395dfd57

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
