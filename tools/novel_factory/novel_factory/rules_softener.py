from __future__ import annotations

import re


# Chinese directive softening (kept conservative)
_CN_REPLACEMENTS = [
    ("必须要", "尽量"),
    ("一定要", "尽量"),
    ("务必", "尽量"),
    ("必须", "尽量"),
    ("不得", "尽量避免"),
    ("严禁", "尽量避免"),
    ("禁止", "尽量避免"),
    ("不可", "尽量避免"),
    ("需要", "建议"),
    ("应当", "建议"),
    ("应该", "建议"),
]


# English / template-exam tone softening
_EN_REPLACEMENTS = [
    ("Hard Constraints", "Guidelines"),
    ("HARD STYLE CONSTRAINTS", "STYLE GUIDELINES"),
    ("STRICT", "Required"),
    ("Do NOT", "Avoid"),
    ("MUST", "should"),
    ("must-follow", "must-follow"),  # keep as-is (factual canon), but allow later changes if desired
]


def _strip_bom(text: str) -> str:
    # Remove UTF-8 BOM if present (common on Windows)
    return text.lstrip("\ufeff")


def soften_style_rules(text: str, *, add_preface: bool = True) -> str:
    """
    Softens 'AI-sounding' directives into editor-like guidance.
    - Strips UTF BOM.
    - Softens common CN directives.
    - Softens common EN exam-tone words (MUST/STRICT/Hard Constraints).
    - Optional preface insertion (disable if template already includes it).
    """
    if not text or not text.strip():
        return text

    softened = _strip_bom(text).replace("\r\n", "\n")

    # CN replacements
    for src, dst in _CN_REPLACEMENTS:
        softened = softened.replace(src, dst)

    # EN replacements (case-sensitive on purpose to avoid overreach)
    for src, dst in _EN_REPLACEMENTS:
        softened = softened.replace(src, dst)

    # Extra: soften "Within the first ~300 words" / "Middle:" / "Late:" exam beats
    softened = re.sub(r"Within the first\s*~?\s*\d+\s*words\s*:", "Early in the chapter:", softened)
    softened = re.sub(r"^\\s*-?\\s*Middle\\s*:\\s*", "- As the chapter develops: ", softened, flags=re.MULTILINE)
    softened = re.sub(r"^\\s*-?\\s*Late\\s*:\\s*", "- Toward the end: ", softened, flags=re.MULTILINE)

    # Preface (only if requested and not already present anywhere)
    preface = (
        "【写作倾向提示】下面的规则用于帮助统一气质与避免跑偏，"
        "是编辑建议而不是硬性KPI。若与剧情/人物当下状态冲突，以剧情自然为先。\n\n"
    )

    if add_preface and "【写作倾向提示】" not in softened:
        softened = preface + softened

    return softened

