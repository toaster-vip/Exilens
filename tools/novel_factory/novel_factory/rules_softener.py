from __future__ import annotations

import re


_REPLACEMENTS = [
    # 强命令 -> 编辑建议
    (r"必须", "尽量"),
    (r"务必", "尽量"),
    (r"一定要", "尽量"),
    (r"不得", "尽量避免"),
    (r"严禁", "尽量避免"),
    (r"禁止", "尽量避免"),
    (r"不可", "尽量避免"),
    (r"必须要", "尽量"),
    (r"需要", "建议"),
    (r"应当", "建议"),
    (r"应该", "建议"),
]


def soften_style_rules(text: str) -> str:
    """
    Softens 'AI-sounding' hard constraints into editor-like preferences.
    This is intentionally conservative: it does not rewrite the whole document,
    only common directive words.
    """
    if not text.strip():
        return text

    softened = text

    # Normalize some common bullet markers to keep formatting stable
    softened = softened.replace("\r\n", "\n")

    for pattern, repl in _REPLACEMENTS:
        softened = re.sub(pattern, repl, softened)

    # Add a short preface to set expectations (preference, not KPI)
    preface = (
        "【写作倾向提示】下面的规则用于帮助统一气质与避免跑偏，"
        "是编辑建议而不是硬性KPI。若与剧情/人物当下状态冲突，以剧情自然为先。\n\n"
    )

    # Avoid duplicating if already present
    if "【写作倾向提示】" not in softened:
        softened = preface + softened

    return softened

