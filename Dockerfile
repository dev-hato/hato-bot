FROM python:3.8.2

ENV PIPENV_VENV_IN_PROJECT=1

WORKDIR /usr/src/app
COPY . .

RUN (curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -) && \
    echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main" >> /etc/apt/sources.list.d/pgdg.list && \
    apt update && \
    apt install -y postgresql-11 && \
    pip install pipenv==2020.6.2 --no-cache-dir && \
    pipenv install

CMD ["sh", "./entrypoint.sh"]
