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

【AI知識】
{knowledge}

【改善指示】
{improvements}

【文字数】
最低：{ARTICLE_MIN_LENGTH}文字
最大：{ARTICLE_MAX_LENGTH}文字

【ルール】

- 指摘された問題を優先して修正する
- 問題のない部分はできるだけ変更しない
- AI知識の内容を変更・捏造しない
- 古い情報へ戻さない
- タイトルを維持する
- 見出し構成を基本的に維持する
- ハッシュタグを維持する
- 記事の内容を不必要に削除しない
- 不必要な水増しをしない
- Markdown形式を維持する
- Markdownの表は使用しない
- 項目と説明を「：」で1行にまとめない
- 読みやすさと具体性を維持する

完成した記事本文だけを出力してください。
"""

    response = call_gemini(
        client=client,
        model=GEMINI_MODEL_REWRITE,
        prompt=prompt,
    )

    return response.text