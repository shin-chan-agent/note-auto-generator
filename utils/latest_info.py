from datetime import datetime
from zoneinfo import ZoneInfo

from google.genai import types

from utils.logger import (
    log_info,
    log_error,
)

from main_system.config import GEMINI_MODEL_LATEST

from utils.gemini_client import call_gemini

from utils.json_parser import parse_json

from utils.knowledge_manager import (
    merge_service,
    needs_update,
    needs_retry,
    mark_update_failed,
)


def create_prompt(service_name):
    """
    サービス名から公式情報を検索するためのプロンプト。
    """

    return f"""
あなたはAIサービスの公式情報を整理する専門家です。

Google Searchを利用し、
「{service_name}」の現在の最新情報を取得してください。

【最重要ルール】

・まずサービス名から公式サイトを特定してください。
・公式サイトを最優先してください。
・公式ドキュメントを優先してください。
・公式料金ページ、公式ヘルプ、公式ブログなども確認してください。
・公式情報が存在する場合、第三者サイトを主要な根拠として使用しないでください。
・公式情報で確認できない内容を推測しないでください。
・URLを推測して作成しないでください。
・検索結果のURLを実際に確認してください。

【取得対象】

・利用可能なモデル
　無料・有料を問わず主要モデルを列挙してください。
　API専用モデルも含めてください。

・料金プラン
・API料金
・主要機能
・制限事項
・注意事項

【情報の条件】

・現在提供中の情報を取得してください。
・公開予定、提供予定、開発予定の情報は含めないでください。
・非推奨だが利用可能なものは "deprecated"
・提供終了・新規利用不可のものは "discontinued"
・現在利用可能なものは "available"

statusが判断できない場合は推測せず、
"available"を使用してください。

【出力】

JSONのみ返してください。
Markdown、コードブロック、説明、コメントは禁止です。

以下の構造を厳密に守ってください。

{{
  "name": "",
  "status": "available",
  "last_verified": "",
  "updated_at": "",
  "sources": [
    {{
      "name": "",
      "url": "",
      "verified_at": ""
    }}
  ],
  "models": [
    {{
      "id": "",
      "name": "",
      "aliases": [],
      "status": "available",
      "effective_date": "",
      "last_updated": "",
      "description": "",
      "modalities": [],
      "api_available": true
    }}
  ],
  "plans": [
    {{
      "id": "",
      "name": "",
      "aliases": [],
      "status": "available",
      "effective_date": "",
      "last_updated": "",
      "billing": "",
      "description": "",
      "pricing": [
        {{
          "name": "",
          "unit": "",
          "price": "",
          "currency": ""
        }}
      ]
    }}
  ],
  "features": [
    {{
      "id": "",
      "name": "",
      "aliases": [],
      "status": "available",
      "effective_date": "",
      "last_updated": "",
      "description": "",
      "category": ""
    }}
  ],
  "limitations": [
    {{
      "id": "",
      "name": "",
      "status": "available",
      "last_updated": "",
      "description": "",
      "category": ""
    }}
  ],
  "notes": [
    {{
      "id": "",
      "title": "",
      "category": "",
      "status": "available",
      "description": "",
      "last_updated": ""
    }}
  ]
}}
"""


def validate_service_data(
    service_data,
    service_id,
):
    if not isinstance(
        service_data,
        dict,
    ):
        log_error(
            f"最新情報JSONがdictではありません: {service_id}"
        )
        return False

    required_fields = [
        "name",
        "models",
        "plans",
        "features",
        "limitations",
        "notes",
    ]

    for field in required_fields:

        if field not in service_data:
            log_error(
                f"最新情報JSONに必須項目がありません: "
                f"{service_id} / {field}"
            )
            return False

    for field in [
        "models",
        "plans",
        "features",
        "limitations",
        "notes",
    ]:

        if not isinstance(
            service_data[field],
            list,
        ):
            log_error(
                f"最新情報JSONの{field}が"
                f"リストではありません: {service_id}"
            )
            return False

    if not isinstance(
        service_data.get("sources", []),
        list,
    ):
        log_error(
            f"最新情報JSONのsourcesが"
            f"リストではありません: {service_id}"
        )
        return False

    return True


def fetch_service_info(
    client,
    service_id,
):
    """
    サービス名だけを使って最新情報を取得する。
    """

    prompt = create_prompt(service_id)

    response = call_gemini(
        client,
        model=GEMINI_MODEL_LATEST,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]
        ),
    )

    if not response.text:
        raise Exception(
            f"Gemini response is empty: {service_id}"
        )

    with open(
        "gemini_response.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(response.text)

    try:
        service_data = parse_json(
            response.text
        )

    except Exception as e:
        log_error(
            f"JSON解析失敗: {service_id}"
        )
        log_error(str(e))
        return None

    if not validate_service_data(
        service_data,
        service_id,
    ):
        return None

    # サービス名を設定
    service_data["name"] = (
        service_data.get("name")
        or service_id
    )

    # sources 最大5件
    service_data["sources"] = (
        service_data.get(
            "sources",
            [],
        )[:5]
    )

    # description 最大200文字
    for section in [
        "models",
        "features",
        "limitations",
        "notes",
    ]:
        for item in service_data.get(
            section,
            [],
        ):
            description = item.get(
                "description"
            )

            if isinstance(
                description,
                str,
            ):
                item["description"] = (
                    description[:200]
                )

    # aliases 最大3件
    for section in [
        "models",
        "plans",
        "features",
    ]:
        for item in service_data.get(
            section,
            [],
        ):
            aliases = item.get(
                "aliases"
            )

            if isinstance(
                aliases,
                list,
            ):
                item["aliases"] = aliases[:3]

    now = datetime.now(
        ZoneInfo("Asia/Tokyo")
    ).date().isoformat()

    service_data["updated_at"] = now
    service_data["last_verified"] = now
    service_data["update_failed"] = False

    log_info(
        f"取得サービス: {service_id}"
    )

    return service_data


def fetch_latest_info(
    client,
    services,
):
    """
    指定サービスの最新情報を取得し、
    AI知識DBへ反映する。
    """

    for service_id in services:

        if (
            not needs_update(service_id)
            and not needs_retry(service_id)
        ):
            log_info(
                f"{service_id} は更新不要のためスキップ"
            )
            continue

        log_info(
            f"{service_id} の最新情報を取得します"
        )

        try:
            service_data = fetch_service_info(
                client,
                service_id,
            )

        except Exception as e:

            log_error(
                f"{service_id} の最新情報取得失敗"
            )
            log_error(str(e))

            mark_update_failed(
                service_id
            )
            continue

        if service_data is None:

            mark_update_failed(
                service_id
            )
            continue

        merge_service(
            service_id,
            service_data,
        )

        log_info(
            f"{service_id} のAI知識DBへの反映が完了しました"
        )