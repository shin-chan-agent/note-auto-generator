import re
import time

from main_system.quality_checker import quality_check
from main_system.rewrite import rewrite_article

from utils.gemini_client import (
    call_gemini,
    GeminiDailyQuotaExceeded,
)
from utils.evaluation_parser import parse_evaluation
from utils.logger import (
    log_info,
    log_warning,
    log_error,
)

from main_system.config import (
    EVALUATION_RETRY_WAIT,
    GEMINI_RETRY_WAIT,
    GEMINI_MODEL_ARTICLE,
)

from user_config import (
    MIN_SCORE,
    MIN_SEO_SCORE,
    MAX_REWRITE,
    MAX_RETRY,
    ARTICLE_MIN_LENGTH,
    ARTICLE_MAX_LENGTH,
)


def extract_title(article):
    """
    記事本文から「タイトル：」のタイトルを抽出する。
    """

    match = re.search(
        r"^タイトル[:：]\s*(.+)$",
        article,
        re.MULTILINE,
    )

    if not match:
        raise ValueError(
            "記事内にタイトルが見つかりません。"
        )

    return match.group(1).strip()


def remove_before_title(article):
    """
    「タイトル：」より前にある余計な文章を削除する。
    """

    title_match = re.search(
        r"^タイトル[:：]",
        article,
        re.MULTILINE,
    )

    if not title_match:
        raise ValueError(
            "記事内にタイトルが見つかりません。"
        )

    return article[title_match.start():].strip()


def evaluate_article(
    client,
    article,
    theme,
    angle,
    past_articles_text,
    knowledge,
):
    """
    記事を評価し、スコアと判定結果を返す。
    """

    for _ in range(MAX_RETRY):

        evaluation = quality_check(
            client,
            article,
            theme,
            angle,
            knowledge,
            past_articles