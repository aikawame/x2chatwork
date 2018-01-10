# X2ChatWork

X2ChatWorkは、各種サービスのWebhookを受信してChatWorkへ通知するためのAPIです。

## 特徴

- ChatWorkでSlackのIncoming Webhooksのような仕組みが実現できます。
- 標準で幾つかのサービスのWebhookに対応しています。
  - GitHub（Pull requestとIssueのopen/close/reopen）
  - Backlog（課題とWikiの作成/更新）
  - Scrapbox
- Slackの[Attachment structure](https://api.slack.com/docs/message-attachments)を受信できます。
- テンプレートを増やすことでその他のサービスにも対応可能です。
- テンプレートは多言語対応可能です。
- APIはAWS Lambda（Python）上で動作します。
- フレームワークには[Chalice](https://github.com/aws/chalice)を採用しています。

## 使用開始

### 下準備

- Python 3およびpipを予めインストールしておいてください。
- LambdaへのデプロイのためにAWS CLIを使えるように予め設定しておいてください。

### 設定ファイルの編集

設定ファイルは[/chalicelib/config](/chalicelib/config)以下に設置します。
予め設置してある[prod.json.sample](/chalicelib/config/prod.json.sample)を`prod.json`に変更してください。
JSONファイルの構造は以下のようになっています。

```
{
  "(APIのパス)": {
    "service": "(サービス名)",
    "locale": "(ロケール名)",
    "api_token": "(ChatWorkのAPIトークン)",
    "room_id": (ChatWorkの通知先),
    "base_url": "(ベースURL: Backlogのみ必要)"
  }
}
```

- APIのURLは、`https://(ランダム文字列).execute-api.(AWSリージョン).amazonaws.com/prod/(APIのパス)`となります。
- サービス名には標準で以下を指定できます。
  - github
  - backlog
  - scrapbox
  - common: SlackのAttachment structure
- ベースURLはBacklogの場合のみ、`https://(アカウント名).backlog.com/`を指定する必要があります。

### デプロイ

次のコマンドを実行して、AWS Lambdaへデプロイします。

```
pip install -r requirements.txt
chalice deploy --stage prod
```

次のようなメッセージが表示されればデプロイ成功です。

```
Creating lambda function: x2chatwork-prod
Initiating first time deployment.
Deploying to API Gateway stage: prod
https://abcde12345.execute-api.ap-northeast-1.amazonaws.com/prod/
```

なお、途中で次のようなメッセージが表示される場合がありますが、現状は無視して問題無いようです。

```
Could not install dependencies:
MarkupSafe==1.0
You will have to build these yourself and vendor them in
the chalice vendor folder.
```

### エラーログの確認

APIの実行時にエラーが発生した場合、レスポンスは全て500 Internal Server Errorとなり、内容はCloudWatchに出力されます。

### 削除

次のコマンドを実行して、AWS Lambdaから削除できます。
確認のダイアログが表示されますが、`y`を回答してください。

```
chalice delete --stage prod
```

## 開発

### 開発環境の利用

[/chalicelib/config](/chalicelib/config)以下に`dev.json`を設置することで、開発環境を利用できます。
デプロイ時には、次のコマンドを実行してください。

```
chalice deploy --stage dev
```

また、次のコマンドを実行することで、ローカル上でAPIを試すことができます。

```
chalice local
```

### テンプレートの追加

テンプレートを追加する場合は、[/chalicelib/templates/ja](/chalicelib/templates/ja)以下に設置します。
ファイル名が設定ファイルのサービス名に対応します。
日本語以外のテンプレートを追加する場合は、対応したロケールのディレクトリーを作成してください。

テンプレートにはJinja2フォーマットを使用します。
テンプレート中で、各種サービスから送信されるJSONデータは`json`変数に格納されています。
また、`replace`フィルターで正規表現を使用した文字列置換を行えます。これはScrapboxのテンプレートで実際に使用しています。

テンプレートを追加された際には、是非ともPull requestを頂ければ幸いです。
