FROM postgres:17.5-bullseye@sha256:aad4b68b765c27ca1ca37a2e703f557a88b894437a3aabfa35065fa52b945e9c

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
