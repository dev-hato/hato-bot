# 鳩bot

- Slackで動くbotです。
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

2. (お好みで) virtualenvを作成します。

```
pip3 install virtualenv
virtualenv --no-site-packages hato
source ./hato/bin/activate
```

3. `.env` ファイルを作成し、SlackのAPI Tokenを記述します。
```
SLACKBOT_API_TOKEN=xoxb_xxxxxxxxx
```

4. `python ./run.py` します。
