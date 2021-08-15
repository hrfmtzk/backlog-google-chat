![CDK application test](https://github.com/hrfmtzk/backlog-google-chat/actions/workflows/cdk_app_test.yml/badge.svg?branch=main) [![codecov](https://codecov.io/gh/hrfmtzk/backlog-google-chat/branch/main/graph/badge.svg?token=HWW91ARAM3)](https://codecov.io/gh/hrfmtzk/backlog-google-chat)

# Backlog - Google Chat 通知連携

[Backlog](https://backlog.com) の通知を Google Chat に通知します。

## 1. デプロイ

通知連携アプリケーションを作成します。

### 1.1. 事前準備

`.env` もしくは環境変数を定義し設定を行います。

- **BACKLOG_BASE_URL**
  - Backlog スペースのベース URL (例: `https://example.backlog.com`)
  - 必須 - yes
- **DOMAIN_NAME**
  - カスタムドメインを利用する場合の利用ドメイン名 (例: `notification.example.com`)
  - API Gateway のカスタムドメインに設定されます
  - 必須 - no (カスタムドメイン利用時は yes)
- **CERTIFICATE_ARN**
  - カスタムドメインを利用する場合の ACM 証明書 ARN
  - API Gateway のカスタムドメインに設定されます
  - 必須 - no (カスタムドメイン利用時は yes)
- **HOSTED_ZONE_ID**
  - Route53 対象ドメインのホストゾーン ID
  - 同一アカウントで対象ドメインを管理している場合に指定することでレコードを作成できます
  - 必須 - no
- **ZONE_NAME**
  - Route53 対象ドメインのゾーン名
  - 同一アカウントで対象ドメインを管理している場合に指定することでレコードを作成できます
  - 必須 - no
- **LOG_LEVEL**
  - Lambda Function のログ出力レベル
  - 必須 - no
- **SENTRY_DSN**
  - Sentry 通知用 DSN
  - 必須 - no

### 1.2. AWS へのデプロイ

CDK でデプロイを行います。

```
$ cdk deploy
```

作成された API の URL を控えます。

- カスタムドメインを指定しなかった場合
  - 例: `https://xxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod`
- カスタムドメインを指定した場合
  - `https://{DOMAIN_NAME}`
  - 例: `https://notification.example.com`

## 2. 連携設定

### 2.1. Google Chat Webhook URL の取得

Google Chat の通知先に利用したいチャットルームで Webhook URL を取得します。

例: `https://chat.googleapis.com/v1/spaces/AAAAxxxxxxx/messages?key=xxxxxxxx&token=xxxxxxxx`

### 2.2 Backlog への通知設定

通知を設定したいプロジェクトにおいて `プロジェクト設定 > インテグレーション > Webhook` とたどり、以下のように設定します。

- **Webhook 名** - 任意の値
- **説明** - 任意の値
- **WebHook URL** - `{1.2. で控えた URL}/{2.1. で取得した URL の v1 以降}`
  - 例: `https://xxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prod/v1/spaces/AAAAxxxxxxx/messages?key=xxxxxxxx&token=xxxxxxxx`
  - 例: `https://notification.example.com/v1/spaces/AAAAxxxxxxx/messages?key=xxxxxxxx&token=xxxxxxxx`
