from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft7Validator

from .config import PACK_SCHEMA_PATH


class PackValidationError(ValueError):
    pass


def load_schema(schema_path: Path = PACK_SCHEMA_PATH) -> Dict[str, Any]:
    # allow BOM in repo-provided schema
    with schema_path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


SCHEMA = load_schema()
VALIDATOR = Draft7Validator(SCHEMA)


def validate_pack(data: Dict[str, Any]) -> None:
    required = [
        "chapter_no",
        "chapter_word_target",
        "chapter_summary",
        "timeline_updates",
        "character_updates",
        "org_updates",
        "new_facts",
        "open_loops",
        "resolved_loops",
        "next_chapter_plan",
        "foreshadowing_tasks",
        "risk_flags",
        "style_selfcheck",
    ]
    missing = [key for key in required if key not in data]
    if missing:
        raise PackValidationError(f"Missing required fields: {', '.join(sorted(missing))}")

    errors = sorted(VALIDATOR.iter_errors(data), key=lambda e: e.path)
    if errors:
        parts = []
        for err in errors:
            loc = "->".join(str(p) for p in err.path) or "root"
            parts.append(f"{loc}: {err.message}")
        raise PackValidationError("; ".join(parts))


def parse_pack(raw: str | bytes | Path | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(raw, dict):
        data = raw
    elif isinstance(raw, (str, bytes)):
        data = json.loads(raw)
    else:
        with Path(raw).open("r", encoding="utf-8") as f:
            data = json.load(f)
    validate_pack(data)
    return data
