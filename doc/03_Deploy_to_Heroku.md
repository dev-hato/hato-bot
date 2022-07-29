# Herokuへデプロイする

1. ブラウザで [鳩botのリポジトリ](https://github.com/dev-hato/hato-bot/tree/master) を開きます。

    安定版を使う場合はmasterブランチを、開発版を使う場合はdevelopブランチを選択してください。

1. 紫色の `Deploy to Heroku` ボタンをクリックします。

1. Herokuの画面が開いたら次の項目を入力します。
    * `App name` : Heroku上のアプリ名です。好きな名前を入力します。(例： `example`)
    * `SLACK_API_TOKEN` : Slackの `Bot User OAuth Access Token` を入力します。
    * `SLACK_SIGNING_SECRET` : Slackの `Signing Secret` を入力します。
    * `YAHOO_API_TOKEN` : Yahooの `ClientID` を入力します。

1. 一番下にある `Deploy app` をクリックします。その後 `Deploy to Heroku` に緑色のチェックがつくまで数分待ちます。

1. `View` をクリックし表示されたHerokuのURL(例： `https://example.herokuapp.com` )をメモします。
