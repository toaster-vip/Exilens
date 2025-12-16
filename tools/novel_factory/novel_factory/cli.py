from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    import pyperclip  # type: ignore
except Exception:  # pragma: no cover - optional dep
    pyperclip = None

from .config import (
    DEFAULT_CHAPTER_WORDS,
    DEFAULT_TARGET_WORDS,
    DEFAULT_THREADS_LIMIT,
    CHAR_DIR,
    GLOBAL_SUMMARY,
    ensure_dirs,
    chapter_folder,
)
from .continuity import Continuity
from .exporter import export_docx, export_txt
from .pack_parser import PackValidationError, parse_pack
from .prompt_builder import build_prompt, plan_from_pack, load_text


HEADER_TEXT_MARK = "===CHAPTER_TEXT==="
PACK_MARK = "===NEXT_CHAPTER_PACK==="


def cmd_init(args: argparse.Namespace) -> None:
    ensure_dirs()
    cont = Continuity()
    cont.update_project(args.project, args.topic, args.target_words, args.chapter_words, args.threads)
    if not GLOBAL_SUMMARY.exists():
        GLOBAL_SUMMARY.write_text(f"# Global Summary\n\nTopic: {args.topic}\n\n", encoding="utf-8")

    prompt = build_prompt(
        chapter_no=1,
        chapter_word_target=args.chapter_words,
        threads_limit=args.threads,
        plan={"goal": "Set the stage", "conflict": "", "beats": [], "pov_suggestions": [], "hook": ""},
        last_summary="",
        open_loops="",
        continuity=cont,
    )
    folder = chapter_folder(1)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "prompt_next.md").write_text(prompt, encoding="utf-8")
    print(prompt)


def cmd_next(args: argparse.Namespace) -> None:
    ensure_dirs()
    cont = Continuity()
    chapter_no = args.chapter or cont.data.get("progress", {}).get("current_chapter", 1)
    last_folder = chapter_folder(chapter_no - 1)
    last_summary_path = last_folder / "summary.json"
    last_summary = ""
    if last_summary_path.exists():
        try:
            with last_summary_path.open("r", encoding="utf-8") as f:
                pack = json.load(f)
            last_summary = pack.get("chapter_summary", "")
            plan = plan_from_pack(pack)
        except Exception:
            plan = {}
    else:
        plan = {}
    if not last_summary and last_folder.exists():
        last_summary = load_text(last_folder / "output.md")
    open_loops_data = cont.data.get("open_loops", [])
    open_loops = "\n".join(f"- {l.get('id')}: {l.get('description')}" for l in open_loops_data)
    prompt = build_prompt(
        chapter_no=chapter_no,
        chapter_word_target=cont.data.get("project", {}).get("chapter_words", DEFAULT_CHAPTER_WORDS),
        threads_limit=cont.data.get("project", {}).get("threads", DEFAULT_THREADS_LIMIT),
        plan=plan,
        last_summary=last_summary,
        open_loops=open_loops,
        continuity=cont,
    )
    folder = chapter_folder(chapter_no)
    folder.mkdir(parents=True, exist_ok=True)
    out_path = folder / "prompt_next.md"
    out_path.write_text(prompt, encoding="utf-8")
    if args.copy and pyperclip:
        pyperclip.copy(prompt)
    print(prompt)


def _split_output(text: str) -> tuple[str, str]:
    if HEADER_TEXT_MARK not in text or PACK_MARK not in text:
        raise ValueError("Input must contain both markers")
    prose_part = text.split(PACK_MARK)[0].replace(HEADER_TEXT_MARK, "").strip()
    pack_part = text.split(PACK_MARK, 1)[1].strip()
    return prose_part, pack_part


def _ingest_content(source: argparse.Namespace) -> str:
    if source.from_file:
        return Path(source.from_file).read_text(encoding="utf-8")
    if source.from_clipboard and pyperclip:
        return pyperclip.paste()
    raise SystemExit("Provide --from-file or --from-clipboard (pyperclip required)")


def cmd_ingest(args: argparse.Namespace) -> None:
    ensure_dirs()
    cont = Continuity()
    raw = _ingest_content(args)
    prose, pack_raw = _split_output(raw)
    try:
        pack = parse_pack(pack_raw)
    except PackValidationError as e:
        raise SystemExit(f"Schema validation failed: {e}")

    folder = chapter_folder(args.chapter)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "output.md").write_text(f"{HEADER_TEXT_MARK}\n{prose}\n\n{PACK_MARK}\n{pack_raw}\n", encoding="utf-8")
    (folder / "summary.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    upsert_global_summary(args.chapter, pack.get("chapter_summary", ""))

    # character updates (A-tier only)
    for update in pack.get("character_updates", []):
        name = update.get("name")
        if not name:
            continue
        card_path = CHAR_DIR / "A" / f"{name}.md"
        card_path.parent.mkdir(parents=True, exist_ok=True)
        if (CHAR_DIR / "S" / f"{name}.md").exists():
            # never overwrite S-tier
            continue

        base = card_path.read_text(encoding="utf-8") if card_path.exists() else f"# {name}\n"
        delta = []
        if update.get("status_delta"):
            delta.append(f"Status: {update['status_delta']}")
        if update.get("secrets_gained"):
            delta.append("Secrets: " + "; ".join(update["secrets_gained"]))
        if update.get("relationships_delta"):
            delta.append("Relations: " + "; ".join(update["relationships_delta"]))

        content = base
        if delta:
            if not content.endswith("\n"):
                content += "\n"
            content += "\n".join(delta) + "\n"

        if (not card_path.exists()) or delta:
            card_path.write_text(content, encoding="utf-8")

    # continuity updates
    cont.merge_pack(pack)
    cont.register_completion(args.chapter, word_count=len(prose.split()))

    # generate next prompt
    next_plan = plan_from_pack(pack)
    open_loops_text = "\n".join(f"- {l.get('id')}: {l.get('description')}" for l in cont.data.get("open_loops", []))
    prompt = build_prompt(
        chapter_no=args.chapter + 1,
        chapter_word_target=cont.data.get("project", {}).get("chapter_words", DEFAULT_CHAPTER_WORDS),
        threads_limit=cont.data.get("project", {}).get("threads", DEFAULT_THREADS_LIMIT),
        plan=next_plan,
        last_summary=prose,
        open_loops=open_loops_text,
        continuity=cont,
    )
    next_folder = chapter_folder(args.chapter + 1)
    next_folder.mkdir(parents=True, exist_ok=True)
    (next_folder / "prompt_next.md").write_text(prompt, encoding="utf-8")
    print(f"Ingested chapter {args.chapter} and generated next prompt.")


def cmd_export(args: argparse.Namespace) -> None:
    if args.docx:
        export_docx()
    if args.txt or not args.docx:
        export_txt()
    print("Export complete")


def cmd_status(_: argparse.Namespace) -> None:
    cont = Continuity()
    prog = cont.data.get("progress", {})
    open_loops = cont.data.get("open_loops", [])
    print(f"Current chapter: {prog.get('current_chapter', 0)}")
    print(f"Completed: {len(prog.get('completed_chapters', []))}")
    print(f"Estimated words: {prog.get('estimated_total_words', 0)}")
    print(f"Open loops: {len(open_loops)}")
    print(f"Phase: {prog.get('phase', '')}")


def upsert_global_summary(chapter_no: int, summary_line: str, path: Path = GLOBAL_SUMMARY) -> None:
    """Insert or replace a chapter summary block, keeping file idempotent."""
    summary_line = summary_line.strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        content = path.read_text(encoding="utf-8")
    else:
        content = "# Global Summary\n"
    # drop existing block for this chapter
    pattern = re.compile(rf"\n## Chapter {chapter_no}.*?(?=\n## Chapter |\Z)", re.S)
    content = re.sub(pattern, "", content).rstrip()
    content = content + f"\n\n## Chapter {chapter_no}\n{summary_line}\n"
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Novel factory CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize project continuity")
    p_init.add_argument("--project", required=True)
    p_init.add_argument("--topic", required=True)
    p_init.add_argument("--target-words", type=int, default=DEFAULT_TARGET_WORDS)
    p_init.add_argument("--chapter-words", type=int, default=DEFAULT_CHAPTER_WORDS)
    p_init.add_argument("--threads", type=int, default=DEFAULT_THREADS_LIMIT)
    p_init.set_defaults(func=cmd_init)

    p_next = sub.add_parser("next", help="Generate next prompt")
    p_next.add_argument("--chapter", type=int)
    p_next.add_argument("--copy", action="store_true")
    p_next.set_defaults(func=cmd_next)

    p_ingest = sub.add_parser("ingest", help="Ingest ChatGPT output")
    p_ingest.add_argument("--chapter", type=int, required=True)
    source = p_ingest.add_mutually_exclusive_group(required=True)
    source.add_argument("--from-file")
    source.add_argument("--from-clipboard", action="store_true")
    p_ingest.set_defaults(func=cmd_ingest)

    p_export = sub.add_parser("export", help="Export chapters")
    p_export.add_argument("--docx", action="store_true")
    p_export.add_argument("--txt", action="store_true")
    p_export.set_defaults(func=cmd_export)

    p_status = sub.add_parser("status", help="Show status")
    p_status.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except PackValidationError as e:
        parser.error(str(e))
    except Exception as e:  # pragma: no cover
        raise


if __name__ == "__main__":
    main()
