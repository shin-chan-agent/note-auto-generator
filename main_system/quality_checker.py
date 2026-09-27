from utils.gemini_client import call_gemini
from main_system.config import GEMINI_MODEL_EVALUATION


def quality_check(
    client,
    article,
    theme,
    angle,
    knowledge,
    past_articles_text,
):
    prompt = f"""
あなたはnote記事の品質評価者です。

以下の記事を厳格に評価してください。

【テーマ】
{theme}

【切り口】
{angle}

【記事】
{article}

【AI知識】
{knowledge}

【過去記事】
{past_articles_text}

以下の5項目を各20点、合計100点で評価してください。

1. 読みやすさ
2. 独自性・重複回避
3. 初心者への分かりやすさ
4. 具体性・実用性
5. 論理性・構成

さらに以下を確認してください。

- テーマが記事全体の中心になっているか
- 切り口が記事全体に反映されているか
- 読者が実際に行動できる内容になっているか
- AIに関する情報が最新の知識と矛盾していないか
- 過去記事と大きく重複していないか
- note記事として読みやすいか
- タイトルが内容を正確に表しているか
- SEOを意識したタイトルになっているか
- 導入文にテーマに関連する重要語が自然に含まれているか
- 見出し構成が検索・読者双方に分かりやすいか

必ず以下の形式だけで出力してください。

SCORE:◯◯
SEO:◯◯
DUPLICATE: OK または NG
LATEST: OK または NG

改善点

【必須】
・改善点

【推奨】
・改善点

すべて問題がない場合は、

【必須】
改善点なし

【推奨】
改善点なし

としてください。
"""

    response = call_gemini(
        client=client,
        model=GEMINI_MODEL_EVALUATION,
        contents=prompt,
    )

    return response.text