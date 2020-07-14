FROM python:3.8.2

WORKDIR /usr/src/app
COPY . .

RUN pip install pipenv --no-cache-dir && \
    pipenv install

CMD ["sh", "./setup/hato-bot/entrypoint.sh"]
