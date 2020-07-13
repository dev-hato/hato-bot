# 鳩bot - 愛嬌のあるSlack Bot

![badge](https://github.com/nakkaa/hato-bot/workflows/pr-test/badge.svg)
  
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

鳩botではこんなことができます。

- 全国の天気予報 ... `天気 東京` で東京の天気予報を表示します。
- 東京近郊の雨雲情報 ... `amesh` で東京の雨雲情報を画像で表示します。
- 最新の地震情報 ... `eq` で最新の地震情報を3件表示します。
- パワーワードの登録、表示 ... `text` で登録したパワーワードを表示します。
- 突然の死吹き出しで整形 ... `>< 文字列` で文字列を「突然の死」吹き出しで整形します。

![hato](https://github.com/nakkaa/hato-age-bot/blob/images/hato1.png)

## 鳩botを動かす

鳩botを動かす方法は主に2種類あります。  
簡単でおすすめなHerokuで動かす方法と自分のPC上で動かす方法です。  
前者については、
[Herokuで動かす手順](https://github.com/nakkaa/hato-bot/wiki/Heroku%E3%81%A7%E5%8B%95%E3%81%8B%E3%81%99%E6%89%8B%E9%A0%86)
を参照してください。  
ここでは後者の自分のPC上で動かす方法を説明します。

### 必要なもの

以下が必要です。

- Git、Python3、Pipenv、Docker(またはPostgreSQL)が動作するPC
- Slack API Token ([Slack API Tokenの取得方法](https://github.com/nakkaa/hato-bot/wiki/Slack-API-Token%E3%81%AE%E5%8F%96%E5%BE%97%E6%96%B9%E6%B3%95))
- Yahoo APIのトークン([Yahoo API Tokenの取得方法](https://github.com/nakkaa/hato-bot/wiki/Yahoo-API-Token%E3%81%AE%E5%8F%96%E5%BE%97%E6%96%B9%E6%B3%95))

### 初期設定

1. このリポジトリをcloneします。

    ```sh
    git clone git@github.com:nakkaa/hato-bot.git
    cd hato-bot
    ```

2. [Pipenv](https://pipenv-ja.readthedocs.io/ja/translate-ja/)で仮想環境を作成します。

    ```sh
    pipenv install
    ```

3. `.env` ファイルを作成し  Slack API Token、PostgreSQLの認証情報、Yahoo API Tokenを記述します。

    ```env
    SLACKBOT_API_TOKEN=xoxb_xxxxxxxxx
    DATABASE_URL=postgres://postgres:password@postgres:5432/
    YAHOO_API_TOKEN=xxxxxxxxx
    ```

4. docker-composeで全てを起動します。

    ```sh
    cd ./setup
    docker-compose up -d
    cd ..
    ```

5. コードの変更は再起動で適用できます

    ```sh
    cd ./setup
    docker-compose restart
    ```

## 補足

- コードをformatする場合は `pipenv run autopep8 --in-place --recursive .` を実行します。

## クレジット

Botで利用しているサービスのクレジットを記載します。

- [Web Services by Yahoo! JAPAN](https://developer.yahoo.co.jp/about)
