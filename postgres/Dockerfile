FROM postgres:14.3-bullseye

RUN for f in /bin/su /usr/bin/expiry /usr/bin/wall /bin/mount /usr/bin/gpasswd /usr/bin/chfn  \
             /usr/bin/newgrp /bin/umount /usr/bin/passwd /sbin/unix_chkpwd /usr/bin/chsh /usr/bin/chage; do \
      chmod u-s "${f}"; \
      chmod u-g "${f}"; \
    done

USER postgres
