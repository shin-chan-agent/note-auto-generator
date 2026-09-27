from datetime import datetime
from zoneinfo import ZoneInfo

from google import genai

from user_config import AI_SERVICES

from config import (
    GEMINI_MODEL_ARTICLE,
)

from theme_manager import (
    get_theme_and_angle,
    mark_combination_completed,
)

from article_history import (
    get_past_articles_text,
    save_article,
)

from article.prompt import get_article_prompt
from article.generator import (
    generate_article,
    extract_title,
)

from utils.knowledge_manager import (
    get_article_knowledge,
)

from utils.latest_info import (
    fetch_latest_info,
)

from utils.email_sender import (
    send_email,
)

from utils.content_saver import (
    save_generated_contents,
)

from utils.logger import (
    log_info,
    log_warning,
    log_error,
)

from utils.gemini_client import (
    GeminiDailyQuotaExceeded,
)


def get_current_date():
    """日本時間の現在日付を取得する。"""

    return datetime.now(
        ZoneInfo("Asia/Tokyo")
    ).strftime("%Y年%m月%d日")


def build_completion_email(
    title,
    theme,
    angle,
    article,
    score,
    seo_score,
):
    """完成記事のメール本文を作成する。"""

    article_html = (
        article
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

    return f"""
<html>
<body>

<h2>note記事の生成が完了しました</h2>

<p><strong>タイトル</strong><br>
{title}</p>

<p><strong>テーマ</strong><br>
{theme}</p>

<p><strong>切り口</strong><br>
{angle}</p>

<p><strong>文字数</strong><br>
{len(article):,}文字</p>

<p><strong>品質スコア</strong><br>
{score}</p>

<p><strong>SEOスコア</strong><br>
{seo_score}</p>

<hr>

<h3>完成記事</h3>

<div>
{article_html}
</div>

</body>
</html>
"""


def build_error_email(error):
    """エラー通知メールを作成する。"""

    return f"""
<html>
<body>

<h2>note記事生成でエラーが発生しました</h2>

<p>自動生成処理を完了できませんでした。</p>

<h3>エラー内容</h3>

<pre>{str(error)}</pre>

</body>
</html>
"""


def main():

    try:

        log_info("Note AI Agentを開始します。")

        # ========================================
        # Gemini API
        # ========================================

        client = genai.Client()

        current_date = get_current_date()

        log_info(
            f"生成日: {current_date}"
        )

        # ========================================
        # Theme × Angle
        # ========================================

        theme, angle = get_theme_and_angle(client)

        log_info(
            f"今回のテーマ: {theme}"
        )

        log_info(
            f"今回の切り口: {angle}"
        )

        # ========================================
        # AI knowledge DB
        # ========================================

        log_info(
            "AIサービスの最新情報を確認します。"
        )

        fetch_latest_info(
            client,
            AI_SERVICES,
        )

        knowledge = get_article_knowledge(
            AI_SERVICES
        )

        # ========================================
        # Article history
        # ========================================

        past_articles_text = get_past_articles_text(
            limit=20
        )

        # ========================================
        # Article prompt
        # ========================================

        prompt = get_article_prompt(
            theme=theme,
            angle=angle,
            knowledge=knowledge,
            past_articles_text=past_articles_text,
            current_date=current_date,
        )

        # ========================================
        # Article generation
        # ========================================

        log_info(
            "記事生成を開始します。"
        )

        result = generate_article(
            client=client,
            prompt=prompt,
            knowledge=knowledge,
        )

        article = result["article"]
        evaluation = result["evaluation"]
        score = result["score"]
        seo_score = result["seo_score"]
        duplicate = result["duplicate"]
        latest = result["latest"]

        title = extract_title(article)

        # ========================================
        # Final validation
        # ========================================

        if not article:
            raise RuntimeError(
                "記事本文が空です。"
            )

        if not title:
            raise RuntimeError(
                "記事タイトルを取得できませんでした。"
            )

        if duplicate != "OK":
            raise RuntimeError(
                "重複チェックを通過できませんでした。"
            )

        if latest != "OK":
            raise RuntimeError(
                "最新情報チェックを通過できませんでした。"
            )

        log_info(
            f"記事生成完了: {len(article):,}文字"
        )

        log_info(
            f"品質スコア: {score}"
        )

        log_info(
            f"SEOスコア: {seo_score}"
        )

        # ========================================
        # Combination history
        # ========================================

        mark_combination_completed(
            theme,
            angle,
        )

        # ========================================
        # Article history
        # ========================================

        save_article(
            title=title,
            theme=theme,
            angle=angle,
            article=article,
        )

        # ========================================
        # Save generated article
        # ========================================

        save_dir = save_generated_contents(
            article
        )

        log_info(
            f"記事を保存しました: {save_dir}"
        )

        # ========================================
        # Completion email
        # ========================================

        email_body = build_completion_email(
            title=title,
            theme=theme,
            angle=angle,
            article=article,
            score=score,
            seo_score=seo_score,
        )

        send_email(
            subject=f"【Note AI Agent】記事生成完了：{title}",
            body=email_body,
        )

        log_info(
            "完成通知メールを送信しました。"
        )

        log_info(
            "Note AI Agentを正常終了しました。"
        )


    except GeminiDailyQuotaExceeded as e:

        log_error(
            f"Gemini APIの無料枠上限に達しました: {e}"
        )

        try:
            send_email(
                subject="【Note AI Agent】Gemini API利用上限",
                body=build_error_email(e),
            )
        except Exception as email_error:
            log_error(
                f"エラー通知メールの送信にも失敗しました: "
                f"{email_error}"
            )

        raise


    except Exception as e:

        log_error(
            f"Note AI Agentでエラーが発生しました: {e}"
        )

        try:
            send_email(
                subject="【Note AI Agent】記事生成エラー",
                body=build_error_email(e),
            )
        except Exception as email_error:
            log_error(
                f"エラー通知メールの送信にも失敗しました: "
                f"{email_error}"
            )

        raise


if __name__ == "__main__":
    main()