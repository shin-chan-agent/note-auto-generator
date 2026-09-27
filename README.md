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

---

## 必要なもの

- GitHubアカウント
- Gemini APIキー
- SMTP対応のメールアカウント

---

## 1. リポジトリを用意する

このシステムを自分のGitHubリポジトリにアップロードします。

---

## 2. user_config.pyを設定する

購入後に主に変更するのは "user_config.py" です。

記事の方向性、テーマ、切り口、AIサービス、文字数、品質基準などを設定できます。

### NOTE_CONCEPT

作成するnote記事全体のコンセプトを設定します。

NOTE_CONCEPT = """
AIを活用した仕事効率化やAIツールの実践的な使い方を、
初心者にも分かりやすく解説するnote
"""

自分が作りたいnoteの方向性に合わせて変更してください。

---

### THEMES

記事のテーマを設定します。

THEMES = [
    "AIツール活用",
    "AI×仕事効率化",
    "AI副業",
    "AI×SNS",
]

複数のテーマを設定できます。

---

### ANGLES

記事の切り口を設定します。

ANGLES = [
    "始め方",
    "初心者向けの使い方",
    "ツールの選び方",
    "活用アイデア",
    "失敗しやすいポイント",
]

テーマと切り口を組み合わせて記事企画を作成します。

すべての組み合わせをそのまま使用するのではなく、AIが記事として成立するかを判定し、不適切な組み合わせを除外します。

---

### AI_SERVICES

記事作成時に扱うAIサービスを設定します。

AI_SERVICES = [
    "ChatGPT",
    "Gemini",
    "Claude",
]

AIサービスの名称だけを設定してください。

サービスの最新情報はシステムが取得し、AI知識DBで管理します。

---

## 3. 記事の文字数を設定する

以下の3項目で記事の文字数を設定します。

ARTICLE_MIN_LENGTH = 8000
ARTICLE_TARGET_LENGTH = 10000
ARTICLE_MAX_LENGTH = 12000

### ARTICLE_MIN_LENGTH

記事として許容する最低文字数です。

この文字数を下回った記事は採用されず、再生成されます。

### ARTICLE_TARGET_LENGTH

AIが目標とする文字数です。

必ずこの文字数になるわけではありませんが、記事生成時の目安として使用されます。

### ARTICLE_MAX_LENGTH

記事として許容する最大文字数です。

この文字数を超えた記事は採用されず、再生成されます。

---

## 4. 品質設定を行う

MIN_SCORE = 90
MIN_SEO_SCORE = 90
MAX_REWRITE = 3
MAX_RETRY = 3

### MIN_SCORE

記事の品質スコアの合格基準です。

100点満点で評価され、設定した点数以上を目標とします。

例：

MIN_SCORE = 90

90点以上を品質基準とします。

---

### MIN_SEO_SCORE

SEOスコアの合格基準です。

例：

MIN_SEO_SCORE = 90

90点以上をSEO基準とします。

---

### MAX_REWRITE

品質基準を満たさなかった場合に行う自動リライトの最大回数です。

MAX_REWRITE = 3

3回まで自動リライトを行います。

---

### MAX_RETRY

Gemini APIなどでエラーが発生した場合の再試行回数です。

MAX_RETRY = 3

---

## 5. GitHub Secretsを設定する

GitHubリポジトリの

"Settings → Secrets and variables → Actions"

から設定します。

---

## 6. Gemini APIを設定する

以下のSecretを登録します。

GEMINI_API_KEY

### GEMINI_API_KEY

Google AI Studioなどで取得したGemini APIキーを入力します。

このAPIキーを使用して記事生成、品質評価、リライト、最新情報の取得などを行います。

APIキーは "user_config.py" やPythonファイルに直接記載しないでください。

---

## 7. メール設定を行う

以下の6項目をGitHub Secretsに登録します。

SMTP_SERVER
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SENDER_EMAIL
RECIPIENT_EMAIL

### SMTP_SERVER

メール送信用SMTPサーバーのアドレスです。

例：

smtp.example.com

利用するメールサービスのSMTPサーバーを設定してください。

---

### SMTP_PORT

SMTP通信に使用するポート番号です。

利用するメールサービスの指定に合わせて設定してください。

例：

587

---

### SMTP_USER

SMTP認証に使用するユーザー名です。

メールサービスによってはメールアドレスを設定します。

---

### SMTP_PASSWORD

SMTP認証に使用するパスワードです。

メールサービスによっては専用のアプリパスワードを使用します。

---

### SENDER_EMAIL

生成完了メールやエラー通知メールの送信元メールアドレスです。

---

### RECIPIENT_EMAIL

生成完了メールやエラー通知メールの受信先メールアドレスです。

送信先と送信元を同じメールアドレスにすることもできます。

---

## 8. GitHub Actionsを実行する

GitHubの

"Actions → Note AI Agent"

から手動実行できます。

また、設定されたスケジュールによって自動実行されます。

---

## 9. 生成された記事

生成された記事は以下に保存されます。

generated/
└─ 年/
   └─ 月/
      └─ YYYYMMDD_HHMMSS/
         └─ article.md

完成した記事は設定したメールアドレスにも送信されます。

---

## 10. AI知識DB

AIサービスの情報は、

utils/ai_knowledge.json

で管理されます。

初期状態では空になっています。

記事生成に必要なAIサービスの情報を取得し、最新情報を確認しながら知識DBを更新します。

---

## 11. テーマ・切り口の管理

テーマと切り口の組み合わせは自動的に管理されます。

main_system/combination_history.json

AIが記事として成立しない組み合わせを除外し、有効な組み合わせを使用します。

同じ組み合わせが連続して使用されないように履歴を管理します。

すべての有効な組み合わせを使用すると、新しいサイクルが開始されます。

---

## 12. 記事履歴

過去に生成した記事の情報は、

main_system/article_history.json

に保存されます。

過去記事との重複を避けるために使用されます。

---

## 13. 無料での運用について

このシステムは、外部の有料サービスへの加入なしで構築・運用できる構成になっています。

ただし、Gemini APIやGitHub Actionsなどの無料枠・利用条件は変更される場合があります。

実際の利用時は、各サービスの最新の利用条件を確認してください。

---

## トラブルシューティング

### 記事が生成されない

GitHub Actionsの実行ログを確認してください。

以下を確認してください。

- "GEMINI_API_KEY"
- Gemini APIの利用状況
- GitHub Secretsの設定
- "user_config.py" の設定

---

### メールが届かない

以下を確認してください。

- "SMTP_SERVER"
- "SMTP_PORT"
- "SMTP_USER"
- "SMTP_PASSWORD"
- "SENDER_EMAIL"
- "RECIPIENT_EMAIL"

SMTPサービス側で認証方式やアプリパスワードが必要な場合があります。

---

### 記事生成が繰り返し失敗する

GitHub Actionsのログからエラー内容を確認してください。

品質スコアやSEOスコアが基準を満たさない場合は、自動リライトが行われます。

Gemini APIの利用上限に達した場合は、利用可能になるまで記事生成を完了できない場合があります。