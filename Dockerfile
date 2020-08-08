FROM python:3.8.2-alpine

ENV WORKON_HOME=/usr/src/venv

WORKDIR /usr/src/app
COPY Pipfile .

RUN apk add --no-cache git bash postgresql-libs jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install pipenv==2020.6.2 --no-cache-dir && \
    pipenv install && \
    apk --purge del .build-deps git

CMD ["bash", "./entrypoint.sh"]
