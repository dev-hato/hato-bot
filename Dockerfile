FROM python:3.8.2-alpine

ENV WORKON_HOME=/usr/src/venv

WORKDIR /usr/src/app
COPY Pipfile .

RUN apk add --no-cache --virtual=.used-packages bash=5.0.11-r1 postgresql-libs=12.2-r0 && \
    apk add --no-cache --virtual=.build-deps jpeg-dev=8-r6 zlib-dev=1.2.11-r3 git=2.24.3-r0 gcc musl-dev=1.1.24-r2 postgresql-dev=12.2-r0 && \
    pip install pipenv=2020.6.2 --no-cache-dir && \
    pipenv install && \
    rm Pipfile && \
    apk --purge del .build-deps

CMD ["bash", "./entrypoint.sh"]
