from __future__ import annotations

from novel_factory.rules_softener import soften_style_rules


def test_soften_replaces_hard_words():
    raw = "必须这样做。禁止那样做。不得使用XX。应该保持一致。"
    out = soften_style_rules(raw)
    assert "必须" not in out
    assert "禁止" not in out
    assert "不得" not in out
    assert "尽量" in out or "尽量避免" in out
    assert "【写作倾向提示】" in out
