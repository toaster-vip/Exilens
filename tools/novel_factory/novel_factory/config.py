from __future__ import annotations

from pathlib import Path

# Repository root: tools/novel_factory/novel_factory -> repo
REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = REPO_ROOT / "prompts"
BIBLE_PATH = REPO_ROOT / "bible" / "bible.seed.json"
CHAR_DIR = REPO_ROOT / "characters"
TIMELINE_PATH = REPO_ROOT / "timeline" / "continuity.json"
NOTES_DIR = REPO_ROOT / "notes"
GLOBAL_SUMMARY = NOTES_DIR / "global_summary.md"
CHAPTERS_DIR = REPO_ROOT / "chapters"
EXPORTS_DIR = REPO_ROOT / "exports"

PACK_SCHEMA_PATH = PROMPTS_DIR / "pack.schema.json"
TEMPLATE_PATH = PROMPTS_DIR / "chapter_prompt.md"
STYLE_RULES_PATH = PROMPTS_DIR / "style_rules.md"

DEFAULT_THREADS_LIMIT = 3
DEFAULT_CHAPTER_WORDS = 2500
DEFAULT_TARGET_WORDS = 1_000_000


def chapter_folder(chapter_no: int) -> Path:
    return CHAPTERS_DIR / f"{chapter_no:04d}"


def ensure_dirs():
    CHAPTERS_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)
    NOTES_DIR.mkdir(exist_ok=True)
