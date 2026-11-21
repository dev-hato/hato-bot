# sudden-deathへのCI同期

hato-botの`develop`を共通CIの配布元とし、sudden-deathの同期処理が生成PRを作ります。生成PRへの手動修正ではなく、配布元の設定か同期処理を修正してください。

## 配布元の責任

[.github/ci-sync.json](../.github/ci-sync.json)を同期契約として管理します。`schemaVersion: 1`では次を定義します。

- `files`: 共通CIが必要とする設定ファイル。`aqua.yaml`と`aqua-checksums.json`はセットで含めます。
- `excludeWorkflows`: 配布しないworkflowのファイル名パターン。`*hato-bot.yml`はhato-bot固有の処理、`verify-lockfile.yml`は同期先で維持する検証です。

共有ファイルを追加・削除する場合は、workflowだけでなく、この契約と検証テストも更新します。ファイルのパスはリポジトリ内の相対パスに限り、ファイルとその親ディレクトリにsymlinkは使えません。

契約は次のコマンドで検証します。既存の`pr-test`でも、依存関係のインストール直後に`node --test`でテストします。通知用のAppトークンを発行する前と、sudden-deathへの通知処理の中でも検証するため、契約が壊れていれば通知しません。

```sh
node scripts/pr_copy_ci_hato_bot/pr_copy_ci/validate_ci_sync.mjs
node --test
```

## 同期先の責任

sudden-deathは契約を読み、共有workflow・scripts・設定を一度に同期します。`*sudden-death.yml`と名前に`sudden_death`を含むscriptsは同期先が所有します。`package.json`のscriptsも同期先のものを維持します。`package.json`とlockfileの同期、Python・uvのバージョン指定の反映は、既存の同期処理が担当します。

`actions.lock`は配布元のものをコピーせず、同期先のworkflowから公式CLIで再生成・検証します。契約や共有ファイルの欠落、生成や検証の失敗があれば、途中の結果をPRに公開しません。

CodeQLのworkflowも共通CIとして配布します。同期先はAdvanced Setupを採用し、GitHubの設定でDefault Setupを無効にする必要があります。このGitHub設定はファイル同期の対象ではなく、各リポジトリの管理者が管理します。

通知は特定のsource SHAの指定ではなく、最新の`develop`を再同期する依頼です。同期先は取得したコミットを記録し、そのコミットのファイルだけを使って生成します。

## 導入順

1. hato-botに同期契約と検証を導入します。
2. sudden-deathの同期処理を、契約を読む実装へ更新します。
3. 通常の同期で作られた生成PRを確認します。

配布元を先に更新することで、同期先が存在しない契約を読もうとして失敗する期間を避けます。導入作業で既存の生成PRを直接編集したり、検証のために通知を送ったりする必要はありません。
