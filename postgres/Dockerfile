FROM postgres:14.3-bullseye

RUN find / -type f -perm /u+s -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
