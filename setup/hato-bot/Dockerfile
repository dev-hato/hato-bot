FROM python:3

WORKDIR /usr/src/app
COPY . .

RUN pip install pipenv --no-cache-dir && \
    pipenv install --system --deploy && \
    pip uninstall -y pipenv virtualenv-clone viertualenv

CMD ["sh", "./setup/hato-bot/entrypoint.sh"]
