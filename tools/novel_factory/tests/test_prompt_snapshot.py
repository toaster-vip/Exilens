from __future__ import annotations

from pathlib import Path

from novel_factory.prompt_snapshot import save_prompt_snapshot


def test_save_prompt_snapshot_writes_file(tmp_path: Path):
    p = save_prompt_snapshot(prompt="hello", chapter_no=12, seed=34, out_dir=tmp_path)
    assert p.exists()
    assert p.read_text(encoding="utf-8") == "hello"
    assert "ch0012_seed000034" in p.name
