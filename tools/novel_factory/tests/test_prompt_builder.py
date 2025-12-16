from __future__ import annotations

from novel_factory.prompt_builder import render_editor_brief


def test_editor_brief_deterministic_same_seed():
    plan = {
        "goal": "拿到钥匙",
        "conflict": "两方互不信任",
        "beats": ["见面", "试探", "摊牌"],
        "pov_suggestions": ["第三人称近距离"],
        "hook": "他到底带没带东西？",
    }

    a = render_editor_brief(
        chapter_no=12,
        chapter_word_target=2200,
        threads_limit=3,
        plan=plan,
        last_summary="上章：谈崩了",
        open_loops="钥匙去向不明",
        seed=999,
    )

    b = render_editor_brief(
        chapter_no=12,
        chapter_word_target=2200,
        threads_limit=3,
        plan=plan,
        last_summary="上章：谈崩了",
        open_loops="钥匙去向不明",
        seed=999,
    )

    assert a == b


def test_editor_brief_changes_with_seed():
    plan = {
        "goal": "",
        "conflict": "",
        "beats": [],
        "pov_suggestions": [],
        "hook": "",
    }

    a = render_editor_brief(
        chapter_no=1,
        chapter_word_target=2000,
        threads_limit=2,
        plan=plan,
        last_summary="",
        open_loops="",
        seed=1,
    )

    b = render_editor_brief(
        chapter_no=1,
        chapter_word_target=2000,
        threads_limit=2,
        plan=plan,
        last_summary="",
        open_loops="",
        seed=2,
    )

    assert a != b
    assert "素材卡" in a
    assert "素材卡" in b

