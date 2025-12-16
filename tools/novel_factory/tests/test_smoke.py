import argparse

from novel_factory import cli, continuity


def test_init_creates_prompt(tmp_path, monkeypatch):
    # redirect filesystem touch points to tmp_path
    def temp_ensure():
        for d in [tmp_path / "chapters", tmp_path / "exports", tmp_path / "notes"]:
            d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(cli, "ensure_dirs", temp_ensure)
    monkeypatch.setattr(cli, "chapter_folder", lambda n: tmp_path / "chapters" / f"{n:04d}")
    monkeypatch.setattr(cli, "GLOBAL_SUMMARY", tmp_path / "notes" / "global_summary.md")
    monkeypatch.setattr(cli, "Continuity", lambda: continuity.Continuity(path=tmp_path / "timeline" / "continuity.json"))

    args = argparse.Namespace(project="demo", topic="t", target_words=1000, chapter_words=10, threads=1)
    cli.cmd_init(args)

    prompt_path = tmp_path / "chapters" / "0001" / "prompt_next.md"
    assert prompt_path.exists()
    content = prompt_path.read_text(encoding="utf-8")
    assert "Chapter No: 1" in content


def test_upsert_global_summary_idempotent(tmp_path):
    path = tmp_path / "global_summary.md"
    cli.upsert_global_summary(1, "first", path)
    cli.upsert_global_summary(1, "second", path)
    text = path.read_text(encoding="utf-8")
    assert text.count("## Chapter 1") == 1
    assert "second" in text
    assert "first" not in text


def test_ingest_creates_a_tier_card(tmp_path, monkeypatch):
    chapter_base = tmp_path / "chapters"
    char_dir = tmp_path / "characters"
    notes_dir = tmp_path / "notes"
    timeline_dir = tmp_path / "timeline"

    def temp_ensure():
        for d in [chapter_base, char_dir, notes_dir]:
            d.mkdir(parents=True, exist_ok=True)

    class FakeCont:
        def __init__(self):
            self.data = {
                "project": {"chapter_words": 10, "threads": 1},
                "open_loops": [],
                "progress": {"current_chapter": 1, "completed_chapters": []},
            }

        def merge_pack(self, pack):
            self.merged = pack

        def register_completion(self, chapter_no, word_count):
            self.registered = (chapter_no, word_count)

    pack = {
        "chapter_no": 1,
        "chapter_word_target": 10,
        "chapter_summary": "summary",
        "timeline_updates": [],
        "character_updates": [{"name": "Tester", "status_delta": "new"}],
        "org_updates": [],
        "new_facts": [],
        "open_loops": [],
        "resolved_loops": [],
        "next_chapter_plan": {"goal": "g", "conflict": "c", "beats": ["b1"], "pov_suggestions": [], "hook": "h"},
        "foreshadowing_tasks": [],
        "risk_flags": [],
        "style_selfcheck": {"ai_tells": [], "concrete_details_used": [], "dialogue_ratio_hint": ""},
    }

    monkeypatch.setattr(cli, "ensure_dirs", temp_ensure)
    monkeypatch.setattr(cli, "chapter_folder", lambda n: chapter_base / f"{n:04d}")
    monkeypatch.setattr(cli, "GLOBAL_SUMMARY", notes_dir / "global_summary.md")
    monkeypatch.setattr(cli, "CHAR_DIR", char_dir)
    monkeypatch.setattr(cli, "Continuity", lambda: FakeCont())
    monkeypatch.setattr(cli, "parse_pack", lambda raw: pack)
    monkeypatch.setattr(cli, "_ingest_content", lambda args: f"{cli.HEADER_TEXT_MARK}\nstory\n{cli.PACK_MARK}\n{{}}")

    args = argparse.Namespace(chapter=1, from_file=None, from_clipboard=False)
    cli.cmd_ingest(args)

    card = char_dir / "A" / "Tester.md"
    assert card.exists()
    assert "Status: new" in card.read_text(encoding="utf-8")


def test_ingest_creates_stub_when_no_delta(tmp_path, monkeypatch):
    chapter_base = tmp_path / "chapters"
    char_dir = tmp_path / "characters"
    notes_dir = tmp_path / "notes"

    def temp_ensure():
        for d in [chapter_base, char_dir, notes_dir]:
            d.mkdir(parents=True, exist_ok=True)

    class FakeCont:
        def __init__(self):
            self.data = {
                "project": {"chapter_words": 10, "threads": 1},
                "open_loops": [],
                "progress": {"current_chapter": 1, "completed_chapters": []},
            }

        def merge_pack(self, pack):
            self.merged = pack

        def register_completion(self, chapter_no, word_count):
            self.registered = (chapter_no, word_count)

    pack = {
        "chapter_no": 1,
        "chapter_word_target": 10,
        "chapter_summary": "summary",
        "timeline_updates": [],
        "character_updates": [{"name": "Ghost"}],
        "org_updates": [],
        "new_facts": [],
        "open_loops": [],
        "resolved_loops": [],
        "next_chapter_plan": {"goal": "g", "conflict": "c", "beats": ["b1"], "pov_suggestions": [], "hook": "h"},
        "foreshadowing_tasks": [],
        "risk_flags": [],
        "style_selfcheck": {"ai_tells": [], "concrete_details_used": [], "dialogue_ratio_hint": ""},
    }

    monkeypatch.setattr(cli, "ensure_dirs", temp_ensure)
    monkeypatch.setattr(cli, "chapter_folder", lambda n: chapter_base / f"{n:04d}")
    monkeypatch.setattr(cli, "GLOBAL_SUMMARY", notes_dir / "global_summary.md")
    monkeypatch.setattr(cli, "CHAR_DIR", char_dir)
    monkeypatch.setattr(cli, "Continuity", lambda: FakeCont())
    monkeypatch.setattr(cli, "parse_pack", lambda raw: pack)
    monkeypatch.setattr(cli, "_ingest_content", lambda args: f"{cli.HEADER_TEXT_MARK}\nstory\n{cli.PACK_MARK}\n{{}}")

    args = argparse.Namespace(chapter=1, from_file=None, from_clipboard=False)
    cli.cmd_ingest(args)

    card = char_dir / "A" / "Ghost.md"
    assert card.exists()
    assert card.read_text(encoding="utf-8").startswith("# Ghost")