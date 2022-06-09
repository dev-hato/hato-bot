FROM postgres:14.3-bullseye

RUN chmod u-s /bin/su && \
    chmod g-s /bin/su && \
    chmod u-s /usr/bin/expiry && \
    chmod g-s /usr/bin/expiry && \
    chmod u-s /usr/bin/wall && \
    chmod g-s /usr/bin/wall && \
    chmod u-s /bin/mount && \
    chmod g-s /bin/mount && \
    chmod u-s /usr/bin/gpasswd && \
    chmod g-s /usr/bin/gpasswd && \
    chmod u-s /usr/bin/chfn && \
    chmod g-s /usr/bin/chfn && \
    chmod u-s /usr/bin/newgrp && \
    chmod g-s /usr/bin/newgrp && \
    chmod u-s /bin/umount && \
    chmod g-s /bin/umount && \
    chmod u-s /usr/bin/passwd && \
    chmod g-s /usr/bin/passwd && \
    chmod u-s /sbin/unix_chkpwd && \
    chmod g-s /sbin/unix_chkpwd && \
    chmod u-s /usr/bin/chsh && \
    chmod g-s /usr/bin/chsh && \
    chmod u-s /usr/bin/chage && \
    chmod g-s /usr/bin/chage

USER postgres

HEALTHCHECK --interval=5s --retries=20 CMD ["pg_isready"]
