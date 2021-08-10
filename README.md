# 鳩bot - 愛嬌のあるSlack Bot

![badge](https://github.com/dev-hato/hato-bot/workflows/pr-test/badge.svg)
  
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

鳩botでは主に以下のことができます。

- 雨雲情報 ... `amesh [text]` で指定した地名・住所[text]の雨雲情報を画像で表示します。
- 最新の地震情報 ... `eq` で最新の地震情報を3件表示します。
- パワーワードの登録、表示 ... `text` で登録したパワーワードを表示します。
- 突然の死吹き出しで整形 ... `>< [text]` で文字列[text]を「突然の死」吹き出しで整形します。

![hato](./doc/img/hato-bot-run-1.png)

## 鳩botを動かす

鳩botを動かす方法は主に2種類あります。  
簡単でおすすめなHerokuで動かす方法と自分のPC上で動かす方法です。

### 必要なもの

鳩botを使うには以下が必要です。

- Herokuアカウント(またはDockerが動作するPC)
- Slack API Token ([Slack API Tokenの取得手順](./doc/01_Get_Slack_API_Token.md))
- Yahoo API Token ([Yahoo API Tokenの取得手順](./doc/02_Get_Yahoo_API_Token.md))

### Herokuで動かす

すぐに鳩botを動かしたい場合はHerokuを使うと簡単です。

1. Slack API TokenとYahoo API Tokenを取得する。
1. [Herokuへデプロイする。](./doc/03_Deploy_to_Heroku.md)
1. [Slack Event URLを設定する。](./doc/04_Setting_to_Event_URL.md)

### 自分のPC上で動かす

自分のPCで動かすこともできます。

1. 事前にSlack API TokenとYahoo API Tokenを取得します。

1. このリポジトリをcloneします。

    安定版を使う場合は `-b master` を指定します。最新の開発版を使う場合は指定不要です。

    ```sh
    git clone -b master https://github.com/dev-hato/hato-bot.git
    cd hato-bot
    ```

    または [Release](https://github.com/dev-hato/hato-bot/releases/latest) から最新の安定版をダウンロードして解凍します。

1. [Pipenv](https://pipenv-ja.readthedocs.io/ja/translate-ja/)で仮想環境を作成します。

    ```sh
    pipenv install
    ```

1. `.env` ファイルを作成し  Slack API Token、PostgreSQLの認証情報、Yahoo API Tokenなどを記述します。

    `.env.example` をコピーして使うとよいでしょう

1. docker-composeで鳩botとPostgreSQLを起動します。

    ```sh
    cd ./setup
    docker-compose up -d
    cd ..
    ```

1. コードの変更はdocker-composeの再起動で適用できます。

    ```sh
    cd ./setup
    docker-compose restart
    ```

#### コマンドの実行方法

- 鳩botに対しコマンドを実行したいときは `post_command.py` を使うと便利です。

    ```sh
    pipenv run python post_command.py --channel {投稿先のチャンネルのchannel id} \
                                      --user {自分のuser_id} \
                                      "{hato-botのコマンド}"
    ```

- または[ngrok](https://ngrok.com/)を使うこともできます。

    ```sh
    ./ngrok http 3000
    ```

#### コミットする前に行うこと
誤ってクレデンシャルをコミットしないよう、以下のhookを設定します。

1. 以下のスクリプトを `.git/hooks/pre-commit` として保存します。
    ```sh
    #!/bin/bash
    source `dirname ${0}`/_local-hook-exec
    declare scriptDir=$(cd $(dirname $0);pwd)
    declare parentDir="$(dirname "${scriptDir}")"
    declare FILES=$(git diff --cached --name-only --diff-filter=ACMR | sed 's| |\\ |g')
    [ -z "$FILES" ] && exit 0
    echo "  ▶ Check credentials by secretlint"
    yarn install
    # Secretlint all selected files
    echo "$FILES" | xargs yarn secretlint --maskSecrets
    RET=$?
    if [ $RET -eq 0 ] ;then
        exit 0
    else
        exit 1
    fi
    EOF
    ```
1. `.git/hooks/pre-commit` に実行権限を付与します。
    ```sh
    chmod +x .git/hooks/pre-commit
    ```

#### 補足

- コードを整形する場合は `pipenv run autopep8 --in-place --recursive .` を実行します。

## 鳩botコマンド一覧

- 鳩botで使用可能なコマンドは次の通りです。

    ```text
    amesh ... 東京のameshを表示する。
    amesh [text] ... 指定した地名・住所・郵便番号[text]のameshを表示する。
    amesh [緯度 (float)] [経度 (float)] ... 指定した座標([緯度 (float)], [経度 (float)])のameshを表示する。
    標高 ... 東京の標高を表示する。
    標高 [text] ... 指定した地名・住所・郵便番号[text]の標高を表示する。
    標高 [緯度 (float)] [経度 (float)] ... 指定した座標([緯度 (float)], [経度 (float)])の標高を表示する。
    eq ... 最新の地震情報を3件表示する。
    text list ... パワーワード一覧を表示する。
    text random ... パワーワードをひとつ、ランダムで表示する。
    text show [int] ... 指定した番号[int]のパワーワードを表示する。
    text add [text] ... パワーワードに[text]を登録する。
    text delete [int] ... 指定した番号[int]のパワーワードを削除する。
    >< [text] ... 文字列[text]を吹き出しで表示する。
    にゃーん ... 「よしよし」と返す。
    version ... バージョン情報を表示する。
    ```

## バージョンアップによる変更点

- バージョンアップによる変更点については[CHANGELOG](./CHANGELOG.md) を参照してください。

## バグ報告や機能の要望について

- バグ報告や機能追加の要望がある場合は [Issues](https://github.com/dev-hato/hato-bot/issues) の
     `New Issue` から報告をお願いします。

- プルリクエストも大歓迎です。

## クレジット

Botで利用しているサービスのクレジットを記載します。

- [Web Services by Yahoo! JAPAN](https://developer.yahoo.co.jp/sitemap/)
