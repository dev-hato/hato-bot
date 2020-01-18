# 鳩bot

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- 愛嬌のあるSlack用botです。
- `天気 <地名>` で天気予報を教えてくれます。
- `amesh` で東京近郊の雨雲情報を教えてくれます。
- `>< 文字列` で文字列を「突然の死」吹き出しで整形してくれます。

![](https://github.com/nakkaa/hato-age-bot/blob/images/hato1.png)

## 必要なもの
- Python3が動作する環境。

## 初期設定

1. このリポジトリをcloneします。
    ```
    git clone git@github.com:nakkaa/hato-bot.git
    cd hato-bot
    ```

2. [Poetry](https://github.com/python-poetry/poetry)を使って仮想環境を作成します。
    ```
    poetry install
    ```

3. `.env` ファイルを作成し、SlackのAPI Tokenを記述します。
    ```
    SLACKBOT_API_TOKEN=xoxb_xxxxxxxxx
    ```

4. `poetry run python ./run.py` します。
