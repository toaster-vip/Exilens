# tools/novel_factory/novel_factory/prompt_builder.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from .config import (
    BIBLE_PATH,
    CHAR_DIR,
    GLOBAL_SUMMARY,
    STYLE_RULES_PATH,
    TEMPLATE_PATH,
)
from .continuity import Continuity, minify_bible, minify_continuity
from .rules_softener import soften_style_rules
from .style_cards import BANNED_FILLERS, EDITOR_DONTS, choose_strategy, sample_materials
from .prompt_snapshot import save_prompt_snapshot

# If you ever hit Windows encoding issues again, set this to "en".
BRIEF_LANG = "zh"  # "zh" | "en"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def gather_characters(tier_dir: Path) -> str:
    if not tier_dir.exists():
        return ""
    docs: list[str] = []
    for path in sorted(tier_dir.glob("*.md")):
        docs.append(f"## {path.stem}\n" + load_text(path))
    return "\n\n".join(docs)


def _coerce_int_seed(seed: int | None, chapter_no: int) -> int:
    # Deterministic by default: use chapter_no if seed is not provided.
    return int(seed if seed is not None else chapter_no)


def _zh(s: str, e: str) -> str:
    return s if BRIEF_LANG == "zh" else e


def render_editor_brief(
    *,
    chapter_no: int,
    chapter_word_target: int,
    threads_limit: int,
    plan: Dict[str, Any],
    last_summary: str,
    open_loops: str,
    seed: int,
) -> str:
    strat = choose_strategy(seed)
    mats = sample_materials(seed)

    beats = plan.get("beats", []) or []
    beats_lines = (
        "\n".join(f"- {b}" for b in beats)
        if beats
        else "- (beats may be organized naturally based on context)"
    )

    pov_sugs = plan.get("pov_suggestions", []) or []
    pov_line = (
        "、".join(pov_sugs)
        if pov_sugs
        else _zh("按叙事需要自行选择（保持一致即可）", "Choose as needed (keep consistent).")
    )

    donts_lines = "\n".join(f"- {d}" for d in EDITOR_DONTS)
    banned_line = "、".join(BANNED_FILLERS)

    goal = (plan.get("goal", "") or "").strip()
    conflict = (plan.get("conflict", "") or "").strip()
    hook = (plan.get("hook", "") or "").strip()

    # Keep fallbacks short and concrete (avoid AI-ish long meta text)
    goal = goal or _zh("（可留空：用事件把目标逼出来）", "(optional: let events reveal the goal)")
    conflict = conflict or _zh("（用利益/关系对抗落地，别抽象）", "(ground it in interests/relationships)")
    hook = hook or _zh("（可不写：钩子可以藏在动作或一句话里）", "(optional: hide hook in action/dialogue)")

    # Dialogue seeds: do NOT require copying, only suggest tone
    dialogue_seed_lines = "\n".join(f'- "{s}"' for s in mats["dialogue_seeds"])

    if BRIEF_LANG == "en":
        brief = f"""\
# Editor Brief (task sheet)

1) What must happen (events, not themes)
- Chapter goal: {goal}
- Primary conflict: {conflict}
- Beats:
{beats_lines}

2) Facts that must stay consistent
- Last chapter summary: {(last_summary or "No previous chapter.").strip()}
- Open loops: {(open_loops or "None").strip()}
- Threads limit: {threads_limit}

3) Style dials (preferences, not KPIs)
- Opening: {strat.opening}
- Rhythm: {strat.rhythm}
- Camera: {strat.camera}
- Dialogue: {strat.dialogue_density}
- POV: {pov_line}
- Hook question: {hook}

4) Material cards (use naturally; no need to use all)
- Objects: {", ".join(mats["objects"])}
- Ambient sounds: {", ".join(mats["sounds"])}
- Smell/temperature: {mats["senses"][0]}
- Small gestures: {", ".join(mats["gestures"])}
- Place micro-details: {", ".join(mats["place_details"])}

5) Dialogue seeds (do not copy; keep the vibe human)
{dialogue_seed_lines}

6) Don'ts (light touch)
{donts_lines}
- Use fewer fillers like: {", ".join(BANNED_FILLERS)}

7) Output
- Target length: ~{chapter_word_target} (flexible)
- Output chapter body only. No explanations, no meta commentary.
"""
        return brief

    # Default: Chinese brief (keep it concise; avoid long preachy lines)
    brief = f"""\
# 编辑简报（写作任务单）

 本章任务（写发生了什么，别写想表达什么）
- 章节目标：{goal}
- 主要冲突：{conflict}
- 节拍：
{beats_lines}

 必须一致的事实（避免穿帮）
- 上章摘要：{(last_summary or "No previous chapter.").strip()}
- 未收束线索：{(open_loops or "None").strip()}
- 线程上限：{threads_limit}

 叙事拨片（倾向，不是硬指标）
- 开头：{strat.opening}
- 节奏：{strat.rhythm}
- 镜头：{strat.camera}
- 对白：{strat.dialogue_density}
- POV：{pov_line}
- 钩子问题：{hook}

 素材卡（随手拿来用，用得自然就行）
- 物件：{"、".join(mats["objects"])}
- 环境声：{"、".join(mats["sounds"])}
- 气味/温度：{mats["senses"][0]}
- 小动作：{"、".join(mats["gestures"])}
- 地点碎细节：{"、".join(mats["place_details"])}

 对白种子（别照抄，意思对、口气像人就行）
{dialogue_seed_lines}

 禁区（点到为止）
{donts_lines}
- 少用垫词：{banned_line}

 输出要求
- 字数目标：约 {chapter_word_target}（允许上下浮动）
- 只输出章节正文，不要写任何解释/分析/总结写法。
"""
    return brief


def build_prompt(
    chapter_no: int,
    chapter_word_target: int,
    threads_limit: int,
    plan: Dict[str, Any],
    last_summary: str,
    open_loops: str,
    continuity: Continuity,
    seed: int | None = None,
) -> str:
    template = load_text(TEMPLATE_PATH)

    # Softened rules to reduce "AI instruction" tone at runtime
    style_rules_raw = load_text(STYLE_RULES_PATH)
    style_rules = soften_style_rules(style_rules_raw, add_preface=False)

    bible = load_json(BIBLE_PATH)
    bible_mini = minify_bible(bible)

    continuity_mini = minify_continuity(continuity.data)
    global_summary = load_text(GLOBAL_SUMMARY)

    characters_s = gather_characters(CHAR_DIR / "S")
    characters_a = gather_characters(CHAR_DIR / "A")

    seed_i = _coerce_int_seed(seed, chapter_no)
    editor_brief = render_editor_brief(
        chapter_no=chapter_no,
        chapter_word_target=chapter_word_target,
        threads_limit=threads_limit,
        plan=plan,
        last_summary=last_summary,
        open_loops=open_loops,
        seed=seed_i,
    )

    prompt = (
        template.replace("{{STYLE_RULES}}", style_rules)
        .replace("{{BIBLE_MINI}}", bible_mini)
        .replace("{{GLOBAL_SUMMARY}}", global_summary or "(empty)")
        .replace("{{CONTINUITY_MINI}}", continuity_mini)
        .replace("{{CHARACTERS_S_MINI}}", characters_s or "(see S-tier cards)")
        .replace("{{CHARACTERS_A_MINI}}", characters_a or "(A-tier cards will be created on demand)")
        .replace("{{LAST_CHAPTER_SUMMARY}}", last_summary or "No previous chapter.")
        .replace("{{OPEN_LOOPS}}", open_loops or "None")
        .replace("{{CHAPTER_NO}}", str(chapter_no))
        .replace("{{CHAPTER_WORD_TARGET}}", str(chapter_word_target))
        .replace("{{THREADS_LIMIT}}", str(threads_limit))
        .replace("{{SCENE_GOAL}}", plan.get("goal", ""))
        .replace("{{PRIMARY_CONFLICT}}", plan.get("conflict", ""))
        .replace("{{BEATS}}", "\n".join("- " + b for b in plan.get("beats", [])))
        .replace("{{POV_SUGGESTIONS}}", ", ".join(plan.get("pov_suggestions", [])))
        .replace("{{HOOK_QUESTION}}", plan.get("hook", ""))
    )

    # Minimal intrusion: inject brief via placeholder, otherwise append.
    if "{{EDITOR_BRIEF}}" in prompt:
        prompt = prompt.replace("{{EDITOR_BRIEF}}", editor_brief)
    else:
        prompt = prompt + "\n\n" + editor_brief
    # Prompt snapshot (on by default; off by default under pytest)
    default_enabled = "0" if "PYTEST_CURRENT_TEST" in os.environ else "1"
    enabled = os.getenv("NOVEL_FACTORY_SNAPSHOT_PROMPT", default_enabled).strip() != "0"
    if enabled:
        try:
            save_prompt_snapshot(prompt=prompt, chapter_no=chapter_no, seed=seed_i)
        except Exception as e:
            # Snapshot failure must never break prompt generation
            print(f"[novel_factory] WARN: prompt snapshot failed: {e}")
    return prompt
def plan_from_pack(pack: Dict[str, Any]) -> Dict[str, Any]:
    nxt = pack.get("next_chapter_plan", {})
    return {
        "goal": nxt.get("goal", ""),
        "conflict": nxt.get("conflict", ""),
        "beats": nxt.get("beats", []),
        "pov_suggestions": nxt.get("pov_suggestions", []),
        "hook": nxt.get("hook", ""),
    }





