# 鳩bot

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- 愛嬌のあるSlack用botです。
- `天気 <地名>` で天気予報を教えてくれます。
- `amesh` で東京近郊の雨雲情報を教えてくれます。
- `>< 文字列` で文字列を「突然の死」吹き出しで整形してくれます。

![](https://github.com/nakkaa/hato-age-bot/blob/images/hato1.png)

## 必要なもの
鳩botを動かすためには以下が必要です。
- Python3
- PostgreSQL(Dockerで導入可)

## 初期設定

1. このリポジトリをcloneします。
    ```
    git clone git@github.com:nakkaa/hato-bot.git
    cd hato-bot
    ```

2. [Pipenv](https://pipenv-ja.readthedocs.io/ja/translate-ja/)で仮想環境を作成します。
    ```
    pipenv install
    ```

3. `.env` ファイルを作成し、SlackのAPI TokenとPostgreSQLの認証情報、(雨雲情報を取得する場合は)Yahoo APIのトークンを記述します。
    ```
    SLACKBOT_API_TOKEN=xoxb_xxxxxxxxx
    DATABASE_URL=postgres://postgres:password@localhost:5432/
    YAHOO_API_TOKEN=xxxxxxxxx
    ```
4. PostgreSQLを起動します。(Dockerの場合は以下のコマンドを実行します。)

    ```
    cd ./setup
    docker-compose up -d
    cd ..
    ```

5. `pipenv run python ./create_env.py` を実行しPostgreSQLにテーブルを作成します。

6. `pipenv run python ./run.py` を実行します。
