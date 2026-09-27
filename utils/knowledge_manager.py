from pathlib import Path
import json

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from main_system.config import (
    KNOWLEDGE_UPDATE_INTERVAL_DAYS,
    MAX_KNOWLEDGE_AGE_DAYS,
    MISSING_LIMIT,
)


KNOWLEDGE_FILE = Path(__file__).parent / "ai_knowledge.json"

LIST_FIELDS = [
    "models",
    "plans",
    "features",
    "limitations",
    "notes",
]

TOKYO_TZ = ZoneInfo("Asia/Tokyo")


def parse_datetime(date_text):
    if not date_text:
        return None

    try:
        dt = datetime.fromisoformat(str(date_text))
    except (TypeError, ValueError):
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TOKYO_TZ)

    return dt


def create_default_knowledge():
    return {
        "version": 1,
        "services": {},
    }


def load_knowledge():
    if not KNOWLEDGE_FILE.exists():
        data = create_default_knowledge()
        save_knowledge(data)
        return data

    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    if "services" not in data:
        data["services"] = {}

    return data


def get_article_knowledge(service_ids):
    data = load_knowledge()

    result = {}

    for service_id in service_ids:
        service = data["services"].get(service_id)

        if not service:
            continue

        result[service_id] = {
            "name": service.get("name"),
            "updated_at": service.get("updated_at"),

            "models": [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "status": item.get("status"),
                    "description": item.get(
                        "description",
                        "",
                    )[:80],
                }
                for item in filter_active_items(
                    service.get("models", [])
                )
            ],

            "plans": [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "status": item.get("status"),
                    "description": item.get(
                        "description",
                        "",
                    )[:80],
                    "pricing": item.get(
                        "pricing",
                        [],
                    ),
                }
                for item in filter_active_items(
                    service.get("plans", [])
                )
            ],

            "features": [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "status": item.get("status"),
                    "description": item.get(
                        "description",
                        "",
                    )[:80],
                }
                for item in filter_active_items(
                    service.get("features", [])
                )
            ],

            "limitations": [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "status": item.get("status"),
                    "description": item.get(
                        "description",
                        "",
                    )[:80],
                }
                for item in filter_active_items(
                    service.get("limitations", [])
                )
            ],

            "notes": [
                {
                    "title": item.get("title"),
                    "status": item.get("status"),
                    "description": item.get(
                        "description",
                        "",
                    )[:80],
                }
                for item in filter_active_items(
                    service.get("notes", [])
                )
            ],
        }

    return result


def save_knowledge(data):
    with open(
        KNOWLEDGE_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4,
        )


def needs_update(service_id):
    data = load_knowledge()

    service = data["services"].get(service_id)

    if not service:
        return True

    if service.get("update_failed", False):
        return True

    updated_at = service.get("updated_at")

    if not updated_at:
        return True

    updated_time = parse_datetime(updated_at)

    if updated_time is None:
        return True

    now = datetime.now(timezone.utc)

    elapsed_days = (
        now - updated_time
    ).total_seconds() / 86400

    return elapsed_days >= KNOWLEDGE_UPDATE_INTERVAL_DAYS


def needs_retry(service_id):
    data = load_knowledge()

    service = data["services"].get(service_id)

    if not service:
        return True

    return service.get(
        "update_failed",
        False,
    )


def is_knowledge_too_old(service_id):
    data = load_knowledge()

    service = data["services"].get(service_id)

    if not service:
        return True

    last_verified = service.get("last_verified")

    if not last_verified:
        return True

    verified_time = parse_datetime(last_verified)

    if verified_time is None:
        return True

    now = datetime.now(timezone.utc)

    elapsed_days = (
        now - verified_time
    ).total_seconds() / 86400

    return elapsed_days >= MAX_KNOWLEDGE_AGE_DAYS


def get_background_update_service(
    configured_services,
    exclude_services=None,
):
    """
    user_config.pyに設定されたサービスの中から、
    更新が必要で最も古いサービスを1件返す。
    """

    if exclude_services is None:
        exclude_services = []

    data = load_knowledge()

    candidates = []

    for service_id in configured_services:

        if service_id in exclude_services:
            continue

        service = data["services"].get(service_id)

        if not service:
            return service_id

        if not needs_update(service_id):
            continue

        updated_at = service.get("updated_at")

        if not updated_at:
            return service_id

        updated_time = parse_datetime(updated_at)

        if updated_time is None:
            return service_id

        candidates.append(
            (
                updated_time,
                service_id,
            )
        )

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])

    return candidates[0][1]


def mark_update_failed(service_id):
    data = load_knowledge()

    service = data["services"].get(service_id)

    if service is None:
        return

    service["update_failed"] = True

    save_knowledge(data)


def get_service(service_id):
    data = load_knowledge()

    return data["services"].get(service_id)


def get_services(service_ids):
    data = load_knowledge()

    services = {
        service_id: data["services"][service_id]
        for service_id in service_ids
        if service_id in data["services"]
    }

    for service in services.values():

        for field in LIST_FIELDS:

            if field in service:
                service[field] = filter_active_items(
                    service[field]
                )

    return services


def filter_active_items(items):
    return [
        item
        for item in items
        if item.get(
            "status",
            "available",
        )
        not in [
            "deprecated",
            "discontinued",
        ]
    ]


def update_service(
    service_id,
    service_data,
):
    data = load_knowledge()

    data["services"][service_id] = service_data

    save_knowledge(data)


def merge_service(
    service_id,
    service_data,
):
    data = load_knowledge()

    if service_id not in data["services"]:

        service_data.setdefault(
            "update_failed",
            False,
        )

        for section in LIST_FIELDS:
            for item in service_data.get(
                section,
                [],
            ):
                item.setdefault(
                    "missing_count",
                    0,
                )

        data["services"][service_id] = service_data

        save_knowledge(data)

        return data["services"][service_id]

    current = data["services"][service_id]

    for key, value in service_data.items():

        if key in LIST_FIELDS:

            current[key] = merge_list_items(
                current.get(key, []),
                value,
            )

        elif isinstance(value, dict):

            if key not in current:
                current[key] = value
            else:
                current[key].update(value)

        else:
            current[key] = value

    for section in LIST_FIELDS:

        mark_missing_items(
            current.get(section, []),
            service_data.get(section, []),
        )

    current["update_failed"] = False

    save_knowledge(data)

    return current


def mark_missing_items(
    old_items,
    new_items,
):
    new_map = {
        item["id"]: item
        for item in new_items
        if "id" in item
    }

    for old_item in old_items:

        item_id = old_item.get("id")

        if not item_id:
            continue

        if item_id in new_map:

            old_item["missing_count"] = 0

            new_item = new_map[item_id]

            if "status" in new_item:
                old_item["status"] = new_item["status"]

        else:

            old_item["missing_count"] = (
                old_item.get(
                    "missing_count",
                    0,
                ) + 1
            )

            if (
                old_item["missing_count"]
                >= MISSING_LIMIT
            ):
                old_item["status"] = "discontinued"


def merge_list_items(
    current_list,
    new_list,
):
    if not new_list:
        return current_list

    current_map = {
        item["id"]: item
        for item in current_list
        if "id" in item
    }

    for new_item in new_list:

        item_id = new_item.get("id")

        if not item_id:
            continue

        if item_id in current_map:

            current_map[item_id].update(new_item)

            current_map[item_id]["missing_count"] = 0

        else:

            new_item.setdefault(
                "missing_count",
                0,
            )

            current_list.append(new_item)

    return current_list


def merge_list_by_id(
    old_list,
    new_list,
):
    merged = {
        item["id"]: item
        for item in old_list
        if "id" in item
    }

    for item in new_list:

        if "id" not in item:
            continue

        merged[item["id"]] = item

    return list(merged.values())