FROM postgres:17.5-bullseye@sha256:6b985e8e135120720c8586590e6bcff69209d4b0bb4ff587381ad7948ce54132

RUN find / -type f -perm /u+s -ignore_readdir_race -exec chmod u-s {} \; && \
    find / -type f -perm /g+s -ignore_readdir_race -exec chmod g-s {} \;

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
