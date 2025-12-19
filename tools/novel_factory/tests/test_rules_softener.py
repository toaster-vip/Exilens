from __future__ import annotations

from novel_factory.rules_softener import soften_style_rules


def test_soften_cn_directives():
    raw = "必须这样做。禁止那样做。不得使用XX。应该保持一致。"
    out = soften_style_rules(raw, add_preface=False)
    assert "必须" not in out
    assert "禁止" not in out
    assert "不得" not in out
    assert ("尽量" in out) or ("尽量避免" in out)


def test_soften_exam_tone_words():
    raw = "# Style Rules (Hard Constraints)\nYou MUST do X. Do NOT do Y. OUTPUT FORMAT (STRICT)\n"
    out = soften_style_rules(raw, add_preface=False)
    assert "Hard Constraints" not in out
    assert "MUST" not in out
    assert "Do NOT" not in out
    assert "STRICT" not in out
    assert "Guidelines" in out or "Required" in out or "should" in out


def test_preface_optional():
    raw = "Some rules here."
    out1 = soften_style_rules(raw, add_preface=True)
    out2 = soften_style_rules(raw, add_preface=False)
    assert "【写作倾向提示】" in out1
    assert "【写作倾向提示】" not in out2
