FROM python:3.8.2-alpine

ENV WORKON_HOME=/usr/src/venv

WORKDIR /usr/src/app
COPY Pipfile .

RUN apk add --no-cache bash postgresql-libs && \
    apk add --no-cache --virtual=.build-deps jpeg-dev zlib-dev git gcc musl-dev postgresql-dev && \
    pip install pipenv==2020.6.2 --no-cache-dir && \
    pipenv install && \
    rm Pipfile && \
    apk --purge del .build-deps

CMD ["bash", "./entrypoint.sh"]
