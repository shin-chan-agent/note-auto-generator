from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path("generated")


def save_generated_contents(article):
    """
    生成した記事をGitHubリポジトリへ保存する。

    保存先：
    generated/YYYY/MM/YYYYMMDD_HHMMSS/

    Returns:
        Path: 保存したフォルダ
    """

    now = datetime.now(
        ZoneInfo("Asia/Tokyo")
    )

    save_dir = (
        BASE_DIR
        / now.strftime("%Y")
        / now.strftime("%m")
        / now.strftime("%Y%m%d_%H%M%S")
    )

    save_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    file_path = save_dir / "article.md"

    file_path.write_text(
        article,
        encoding="utf-8",
    )

    return save_dir