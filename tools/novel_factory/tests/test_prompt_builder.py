from pathlib import Path

from novel_factory.prompt_builder import build_prompt
from novel_factory.continuity import Continuity


def test_prompt_contains_markers(tmp_path):
    cont = Continuity(path=tmp_path / "continuity.json")
    prompt = build_prompt(
        chapter_no=1,
        chapter_word_target=1500,
        threads_limit=2,
        plan={"goal": "test", "conflict": "c", "beats": ["b1"], "pov_suggestions": ["pov"], "hook": "?"},
        last_summary="None",
        open_loops="- L1",
        continuity=cont,
    )
    assert "===CHAPTER_TEXT===" in prompt
    assert "===NEXT_CHAPTER_PACK===" in prompt