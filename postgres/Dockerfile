FROM postgres:15.12-bullseye@sha256:8c18361c146038dcc61af430490cbc3991867e775e312fe22c107d3ffb2af53a

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
