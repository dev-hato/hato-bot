FROM python:3.8.2

ENV WORKON_HOME=/usr/src/venv

WORKDIR /usr/src/app
COPY Pipfile .

RUN pip install pipenv==2020.6.2 --no-cache-dir && \
    pipenv install

CMD ["bash", "./entrypoint.sh"]
