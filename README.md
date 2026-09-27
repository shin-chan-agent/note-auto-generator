# Note AI Agent

Gemini APIとGitHub Actionsを使って、AI関連のnote記事を自動生成するシステムです。


## 主な機能

- AI関連note記事の自動生成
- テーマ×切り口の自動選択
- AIによるテーマ×切り口の適合性判定
- AIサービスの最新情報チェック
- AI知識DBによる情報管理
- 過去記事との重複チェック
- 品質・SEO評価
- 自動リライト
- 完成記事の保存
- 完成・エラー時のメール通知
- GitHub Actionsによる自動実行


## 必要なもの

- GitHubアカウント
- Gemini APIキー
- メール送信用のSMTPアカウント


## 1. リポジトリを用意する

このシステムを自分のGitHubリポジトリにアップロードします。


## 2. user_config.pyを設定する

基本的なカスタマイズは `user_config.py` で行います。

それ以外のファイルの設定値は変更しないでください。
エラーとなっても責任を負いかねます。


### NOTE_CONCEPT

作成するnote記事の方向性を設定します。


### THEMES

記事のテーマを設定します。


### ANGLES

記事の切り口を設定します。


### AI_SERVICES

記事で扱うAIサービスを設定します。

例：

```python
AI_SERVICES = [
    "ChatGPT",
    "Gemini",
    "Claude",
]
```

### 文字数

- ARTICLE_MIN_LENGTH = 8000
- ARTICLE_TARGET_LENGTH = 10000
- ARTICLE_MAX_LENGTH = 12000


### 品質設定

- MIN_SCORE = 90
- MIN_SEO_SCORE = 90
- MAX_REWRITE = 3
- MAX_RETRY = 3


## 3. GitHub Secretsを設定する

GitHubリポジトリの

```python
Settings → Secrets and variables → Actions
```

から、以下を登録します。


### Gemini

- GEMINI_API_KEY


### メール

- SMTP_SERVER
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SENDER_EMAIL
- RECIPIENT_EMAIL


## 4. GitHub Actionsを実行する

GitHubの

```python
Actions → Note AI Agent
```

から手動実行できます。

また、設定されたスケジュールにより自動実行されます。


## 5. 生成された記事
生成された記事は以下に保存されます。

```python
generated/
└─ 年/
   └─ 月/
      └─ YYYYMMDD_HHMMSS/
         └─ article.md
```

完成した記事は設定したメールアドレスにも送信されます。


## 6. AI知識DB

AIサービスの情報は、

```python
utils/ai_knowledge.json
```

で管理されます。

初期状態では空になっています。

システムが必要に応じてAIサービスの最新情報を取得し、知識DBを更新します。


## 7. テーマ・切り口の管理

テーマと切り口の組み合わせは自動的に管理されます。

```python
main_system/combination_history.json
```

AIが記事として成立しない組み合わせを除外し、有効な組み合わせを順番に使用します。

すべての組み合わせを使用すると、新しいサイクルが開始されます。


## 8. 記事履歴

過去に生成した記事の情報は、

```python
main_system/article_history.json
```

に保存されます。

過去記事との重複を避けるために使用されます。


## 9. 無料での運用について

このシステムは、外部の有料サービスへの加入なしで構築・運用できる構成になっています。

ただし、Gemini APIやGitHub Actionsなどの無料枠・利用条件は変更される場合があります。

利用時は各サービスの最新の利用条件を確認してください。


## トラブルシューティング

### 記事が生成されない

GitHub Actionsの実行ログを確認してください。

特に以下を確認します。

- GEMINI_API_KEY
- Gemini APIの利用状況
- GitHub Secretsの設定
- SMTP設定


### メールが届かない

以下を確認してください。

- SMTP_SERVER
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SENDER_EMAIL
- RECIPIENT_EMAI


### 記事生成が繰り返し失敗する

GitHub Actionsのログからエラー内容を確認してください。

品質スコアやSEOスコアが基準を満たさない場合は、自動リライトが行われます。