from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .config import (
    BIBLE_PATH,
    CHAR_DIR,
    GLOBAL_SUMMARY,
    STYLE_RULES_PATH,
    TEMPLATE_PATH,
)
from .continuity import minify_bible, minify_continuity, Continuity


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def gather_characters(tier_dir: Path) -> str:
    if not tier_dir.exists():
        return ""
    docs = []
    for path in sorted(tier_dir.glob("*.md")):
        docs.append(f"## {path.stem}\n" + load_text(path))
    return "\n\n".join(docs)


def build_prompt(
    chapter_no: int,
    chapter_word_target: int,
    threads_limit: int,
    plan: Dict[str, Any],
    last_summary: str,
    open_loops: str,
    continuity: Continuity,
) -> str:
    template = load_text(TEMPLATE_PATH)
    style_rules = load_text(STYLE_RULES_PATH)
    bible = load_json(BIBLE_PATH)
    bible_mini = minify_bible(bible)
    continuity_mini = minify_continuity(continuity.data)
    global_summary = load_text(GLOBAL_SUMMARY)
    characters_s = gather_characters(CHAR_DIR / "S")
    characters_a = gather_characters(CHAR_DIR / "A")

    prompt = (
        template.replace("{{STYLE_RULES}}", style_rules)
        .replace("{{BIBLE_MINI}}", bible_mini)
        .replace("{{GLOBAL_SUMMARY}}", global_summary or "(empty)")
        .replace("{{CONTINUITY_MINI}}", continuity_mini)
        .replace("{{CHARACTERS_S_MINI}}", characters_s or "(see S-tier cards)")
        .replace("{{CHARACTERS_A_MINI}}", characters_a or "(A-tier cards will be created on demand)")
        .replace("{{LAST_CHAPTER_SUMMARY}}", last_summary or "No previous chapter.")
        .replace("{{OPEN_LOOPS}}", open_loops or "None")
        .replace("{{CHAPTER_NO}}", str(chapter_no))
        .replace("{{CHAPTER_WORD_TARGET}}", str(chapter_word_target))
        .replace("{{THREADS_LIMIT}}", str(threads_limit))
        .replace("{{SCENE_GOAL}}", plan.get("goal", ""))
        .replace("{{PRIMARY_CONFLICT}}", plan.get("conflict", ""))
        .replace("{{BEATS}}", "\n".join("- " + b for b in plan.get("beats", [])))
        .replace("{{POV_SUGGESTIONS}}", ", ".join(plan.get("pov_suggestions", [])))
        .replace("{{HOOK_QUESTION}}", plan.get("hook", ""))
    )
    return prompt


def plan_from_pack(pack: Dict[str, Any]) -> Dict[str, Any]:
    nxt = pack.get("next_chapter_plan", {})
    return {
        "goal": nxt.get("goal", ""),
        "conflict": nxt.get("conflict", ""),
        "beats": nxt.get("beats", []),
        "pov_suggestions": nxt.get("pov_suggestions", []),
        "hook": nxt.get("hook", ""),
    }
