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