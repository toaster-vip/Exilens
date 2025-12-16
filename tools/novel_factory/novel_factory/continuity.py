from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from .config import TIMELINE_PATH


class Continuity:
    def __init__(self, path: Path = TIMELINE_PATH):
        self.path = path
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "0.1",
            "project": {},
            "progress": {"current_chapter": 0, "completed_chapters": [], "estimated_total_words": 0, "phase": "P1_根基立名"},
            "thread_index": [],
            "open_loops": [],
            "resolved_loops": [],
            "timeline": [],
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # deterministic minify helpers
    def minify(self) -> str:
        return minify_continuity(self.data)

    def update_project(self, slug: str, topic: str, target_words: int, chapter_words: int, threads: int) -> None:
        self.data.setdefault("project", {})
        self.data["project"].update(
            {
                "slug": slug,
                "topic": topic,
                "target_words": target_words,
                "chapter_words": chapter_words,
                "threads": threads,
            }
        )
        self.data.setdefault("progress", {})
        self.data["progress"].update(
            {
                "current_chapter": 1,
                "completed_chapters": [],
                "estimated_total_words": 0,
            }
        )
        self.save()

    def register_completion(self, chapter_no: int, word_count: int) -> None:
        prog = self.data.setdefault("progress", {})
        completed: List[int] = prog.setdefault("completed_chapters", [])
        if chapter_no not in completed:
            completed.append(chapter_no)
            completed.sort()
        prog["current_chapter"] = max(chapter_no + 1, prog.get("current_chapter", 1))
        prog["estimated_total_words"] = prog.get("estimated_total_words", 0) + word_count
        self.save()

    def merge_pack(self, pack: Dict[str, Any]) -> None:
        # open loops
        open_loops = self.data.setdefault("open_loops", [])
        resolved = set(pack.get("resolved_loops", []))
        # remove resolved
        open_loops = [loop for loop in open_loops if loop.get("id") not in resolved]
        # add new ones deterministically sorted by id
        for loop in pack.get("open_loops", []):
            if loop.get("id") and all(existing.get("id") != loop["id"] for existing in open_loops):
                open_loops.append(loop)
        open_loops.sort(key=lambda l: l.get("id", ""))
        self.data["open_loops"] = open_loops

        # timeline updates
        timeline = self.data.setdefault("timeline", [])
        timeline.extend(pack.get("timeline_updates", []))
        self.data["timeline"] = timeline

        # risk flags and new facts
        if pack.get("new_facts"):
            nf = self.data.setdefault("new_facts", [])
            for fact in pack["new_facts"]:
                if fact not in nf:
                    nf.append(fact)
        if pack.get("risk_flags"):
            rf = self.data.setdefault("risk_flags", [])
            for r in pack["risk_flags"]:
                if r not in rf:
                    rf.append(r)
        self.save()


def minify_bible(bible: Dict[str, Any]) -> str:
    # deterministic slice of meta + scope + safety
    meta = bible.get("meta", {})
    parts = [
        f"Genre: {meta.get('genre', '')}",
        f"Tone: {', '.join(meta.get('tone', []))}",
        f"Positioning: {meta.get('positioning', '')}",
    ]
    safety = meta.get("content_safety", {})
    if safety:
        parts.append(
            "Safety:" + "; ".join(f"{k}:{v}" for k, v in sorted(safety.items()))
        )
    scope = bible.get("scope", {})
    if scope:
        phases = scope.get("phase_word_budget", [])[:2]
        parts.append("Phases:" + "; ".join(f"{p.get('phase')} {p.get('words')}" for p in phases))
    return "\n".join(parts).strip()


def minify_continuity(data: Dict[str, Any]) -> str:
    progress = data.get("progress", {})
    open_loops = data.get("open_loops", [])
    timeline = data.get("timeline", [])
    parts = [f"Progress: ch{progress.get('current_chapter', 0)} phase={progress.get('phase', '')}"]
    if open_loops:
        top = sorted(open_loops, key=lambda l: (l.get("priority", 5), l.get("id", "")))[:5]
        parts.append("Open loops:" + "; ".join(f"{l.get('id')}: {l.get('description')}" for l in top))
    if timeline:
        recent = timeline[-3:]
        parts.append("Recent timeline:" + "; ".join(f"{t.get('time_hint', '')}:{t.get('event', '')}" for t in recent))
    return "\n".join(parts)