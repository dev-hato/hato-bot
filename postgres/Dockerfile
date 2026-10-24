FROM postgres:17.5-bullseye@sha256:724a6dfcc90fb6b2eb7caa062c7c852fe60fc30727896a044f4d478f423f183f

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

# postgres:17.5-bullseye の postgres ユーザー (UID 999)
USER 999

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
