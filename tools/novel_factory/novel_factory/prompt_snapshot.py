from __future__ import annotations

import os
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "tools" / "novel_factory").exists() or (parent / "prompts").exists():
            return parent
    return Path.cwd().resolve()


def default_snapshots_dir() -> Path:
    override = os.getenv("NOVEL_FACTORY_PROMPT_DIR", "").strip()
    if override:
        return Path(override)
    root = _find_repo_root(Path(__file__))
    return root / "outputs" / "prompts"


def _next_available_path(base: Path) -> Path:
    if not base.exists():
        return base
    stem, suffix = base.stem, base.suffix
    for i in range(2, 1000):
        cand = base.with_name(f"{stem}_v{i}{suffix}")
        if not cand.exists():
            return cand
    return base.with_name(f"{stem}_v{os.getpid()}{suffix}")


def save_prompt_snapshot(*, prompt: str, chapter_no: int, seed: int, out_dir: Path | None = None) -> Path:
    out = out_dir or default_snapshots_dir()
    out.mkdir(parents=True, exist_ok=True)
    name = f"ch{chapter_no:04d}_seed{seed:06d}.prompt.md"
    path = _next_available_path(out / name)
    path.write_text(prompt, encoding="utf-8")
    return path
