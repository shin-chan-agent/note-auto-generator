import hashlib
import json
import random
from pathlib import Path

from user_config import THEMES, ANGLES

from utils.gemini_client import call_gemini
from utils.json_parser import parse_json_response
from utils.logger import (
    log_info,
    log_warning,
    log_error,
)
from config import GEMINI_MODEL_EVALUATION


COMBINATION_HISTORY_FILE = Path("main_system/combination_history.json")


def _config_hash():
    """テーマ・切り口設定の変更を検出するためのハッシュを作成する。"""

    data = {
        "themes": THEMES,
        "angles": ANGLES,
    }

    text = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
    )

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_all_combinations():
    """テーマ×切り口の全組み合わせを作成する。"""

    combinations = []

    for theme in THEMES:
        for angle in ANGLES:
            combinations.append({
                "theme": theme,
                "angle": angle,
            })

    return combinations


def _load_history():
    """組み合わせ履歴を読み込む。"""

    if not COMBINATION_HISTORY_FILE.exists():
        return None

    try:
        with open(
            COMBINATION_HISTORY_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except Exception as e:
        log_warning(
            f"組み合わせ履歴の読み込みに失敗しました: {e}"
        )
        return None


def _save_history(data):
    """組み合わせ履歴を保存する。"""

    COMBINATION_HISTORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        COMBINATION_HISTORY_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def _build_compatibility_prompt(combinations):
    """テーマ×切り口の適合性判定用プロンプト。"""

    combination_text = "\n".join(
        f"{i + 1}. テーマ：{item['theme']} / 切り口：{item['angle']}"
        for i, item in enumerate(combinations)
    )

    return f"""
あなたはnote記事の企画編集者です。

以下のテーマ×切り口の組み合わせについて、
それぞれが独立した1本のnote記事として成立するか判定してください。

【判定基準】

- テーマと切り口の内容が自然に組み合わせられる
- テーマの内容と切り口が矛盾しない
- 読者にとって具体的な記事内容を作れる
- 内容を無理に広げなくても1本の記事として成立する
- AI関連のnote記事として十分な情報量を持たせられる

不適切な組み合わせはNGにしてください。

必ずJSONのみで出力してください。

形式：

{{
  "results": [
    {{
      "theme": "テーマ",
      "angle": "切り口",
      "valid": true
    }},
    {{
      "theme": "テーマ",
      "angle": "切り口",
      "valid": false
    }}
  ]
}}

【対象】

{combination_text}
"""


def _check_compatibility(client, combinations):
    """AIによってテーマ×切り口の適合性を判定する。"""

    if not combinations:
        return []

    prompt = _build_compatibility_prompt(combinations)

    try:
        response = call_gemini(
            client=client,
            model=GEMINI_MODEL_EVALUATION,
            prompt=prompt,
        )

        data = parse_json_response(response.text)

        results = data.get("results", [])

        valid = []

        for item in results:
            if item.get("valid") is True:
                theme = item.get("theme")
                angle = item.get("angle")

                if not theme or not angle:
                    continue

                valid.append({
                    "theme": theme,
                    "angle": angle,
                })

        return valid

    except Exception as e:
        log_error(
            f"テーマ×切り口の適合性判定に失敗しました: {e}"
        )
        raise


def _is_same_combination(a, b):
    return (
        a.get("theme") == b.get("theme")
        and a.get("angle") == b.get("angle")
    )


def get_valid_combinations(client):
    """
    有効なテーマ×切り口を取得する。

    user_config.pyのテーマ・切り口が変更されていた場合は、
    AIによる適合性判定をやり直す。
    """

    current_hash = _config_hash()
    all_combinations = get_all_combinations()
    history = _load_history()

    # 設定変更なし・有効組み合わせが存在する場合
    if (
        history
        and history.get("config_hash") == current_hash
        and history.get("valid_combinations")
    ):
        return history["valid_combinations"]

    log_info(
        "テーマ・切り口設定が変更されたため、"
        "適合性を再判定します。"
    )

    valid_combinations = _check_compatibility(
        client,
        all_combinations,
    )

    if not valid_combinations:
        raise RuntimeError(
            "有効なテーマ×切り口の組み合わせがありません。"
            "user_config.pyを確認してください。"
        )

    data = {
        "config_hash": current_hash,
        "valid_combinations": valid_combinations,
        "used_combinations": [],
    }

    _save_history(data)

    log_info(
        f"有効な組み合わせを{len(valid_combinations)}件登録しました。"
    )

    return valid_combinations


def get_theme_and_angle(client):
    """
    未使用の有効なテーマ×切り口を1つ取得する。

    全組み合わせを使用したら新しいサイクルを開始する。
    """

    current_hash = _config_hash()
    valid_combinations = get_valid_combinations(client)
    history = _load_history()

    # 念のため設定変更時は履歴を初期化
    if not history or history.get("config_hash") != current_hash:
        history = {
            "config_hash": current_hash,
            "valid_combinations": valid_combinations,
            "used_combinations": [],
        }

    used = history.get("used_combinations", [])

    unused = [
        combination
        for combination in valid_combinations
        if not any(
            _is_same_combination(combination, item)
            for item in used
        )
    ]

    # 全組み合わせを使用済み
    if not unused:
        log_info(
            "すべての有効な組み合わせを使用しました。"
            "新しいサイクルを開始します。"
        )

        used = []
        unused = valid_combinations.copy()

    selected = random.choice(unused)

    history["used_combinations"] = used

    _save_history(history)

    return selected["theme"], selected["angle"]


def mark_combination_completed(theme, angle):
    """
    記事生成が正常に完了した組み合わせを使用済みにする。
    """

    history = _load_history()

    if not history:
        return

    combination = {
        "theme": theme,
        "angle": angle,
    }

    used = history.get("used_combinations", [])

    if not any(
        _is_same_combination(combination, item)
        for item in used
    ):
        used.append(combination)

    history["used_combinations"] = used

    _save_history(history)

    log_info(
        f"組み合わせを使用済みにしました: "
        f"{theme} / {angle}"
    )