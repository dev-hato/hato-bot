# Slack API Tokenを取得する

1. [Slack API: Applications | Slack](https://api.slack.com/apps) を開きます。

1. `Create New App` をクリックします。

1. `App Name` に `hato` と入力し、 `Development Slack Workspace` にBotを動かすSlack Workspaceを選択します。

   その後 `Create App` をクリックします。

1. 左側にある `OAuth & Permissions` をクリックします。

1. `Bot Token Scopes` で次の権限を付与します。

   - app_mentions:read
   - chat:write
   - files:write
   - users:read

1. `User Token Scopes` で次の権限を付与します。

   - chat:write

1. ページ上部にある `Install App to Workspace` をクリックします。

1. `Bot User OAuth Access Token` の値をメモします。

1. 左側にある `Basic Information` をクリックし、遷移後のページにある `Signing Secret` の値をメモします。
   (マスクされているので `show` を押して生の値を確認します)
