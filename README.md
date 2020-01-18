# 鳩bot

Slackで動くbotです。

![](https://github.com/nakkaa/hato-age-bot/blob/images/hato1.png)

## できること

- Bot宛で空のメンションを飛ばすと「鳩は唐揚げ」と真理を返してくれます。
- Botに「天気 <地名>」とメンションすると、天気予報を教えてくれます。
![](https://github.com/nakkaa/hato-age-bot/blob/images/hato2.png)
- Botに「>< 文字列」とメンションすると文字列を「突然の死」吹き出しで整形してくれます。

## 必要なもの
- Python3が動く環境

## 初期設定
1. `.env` を作成し、SLackのAPI Tokenを記述します。
    ```
    SLACKBOT_API_TOKEN=hogehoge
    ```

2. `python3 ./run.py` します。
