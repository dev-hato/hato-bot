FROM postgres:17.4-bullseye@sha256:a833c948400f54f875a9dd4eb5cc99fdcab5119a78adb343c59ba323b72082e0

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
