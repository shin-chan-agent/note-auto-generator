from utils.gemini_client import call_gemini
from config import GEMINI_MODEL_REWRITE

from user_config import (
    ARTICLE_MIN_LENGTH,
    ARTICLE_MAX_LENGTH,
)


def rewrite_article(
    client,
    article,
    knowledge,
    improvements,
):
    prompt = f"""
以下のnote記事を改善してください。

【現在の記事】
{article}

【AIに関する最新情報】
{knowledge}

【改善指示】
{improvements}

【文字数ルール】
最低文字数：{ARTICLE_MIN_LENGTH}文字
最大文字数：{ARTICLE_MAX_LENGTH}文字

【リライト方針】

- 改善指示を優先して修正する
- 問題のない部分はできるだけ維持する
- AIに関する事実を捏造しない
- 最新情報を古い情報に戻さない
- タイトルを基本的に維持する
- 見出し構成を基本的に維持する
- ハッシュタグを維持する
- 記事の重要な内容を削除しない
- 不要な文章を追加しない
- 文字数調整だけを目的とした水増しをしない
- 最低文字数を下回らない
- 最大文字数を超えない
- Markdown形式を維持する
- Markdownの表は使用しない
- 「項目：説明」の形式を避け、
  項目と説明を改行して記述する
- 読みやすさ、具体性、正確性を維持する

完成した記事本文だけを出力してください。
"""

    response = call_gemini(
        client=client,
        model=GEMINI_MODEL_REWRITE,
        prompt=prompt,
    )

    return response.text