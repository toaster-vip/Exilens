# Novel Chapter Prompt

You are writing the next chapter of a long-form serialized novel.

You MUST follow all hard constraints below. Do NOT explain. Do NOT output plans. Output only the required blocks at the end.

---

## HARD STYLE CONSTRAINTS
{{STYLE_RULES}}

---

## CANON (MINIFIED)
### Bible (must-follow facts only)
{{BIBLE_MINI}}

### Rolling Global Summary (compressed)
{{GLOBAL_SUMMARY}}

### Continuity Index (timeline / open loops / states)
{{CONTINUITY_MINI}}

---

## CHARACTER RULES (Do NOT quote these; use to guide behavior)
### S-tier (always loaded)
{{CHARACTERS_S_MINI}}

### A-tier (only those appearing in this chapter)
{{CHARACTERS_A_MINI}}

Behavior enforcement:
- If any trigger_sensitivities occurs for a character, their behavior MUST shift and MUST be observable via behavioral_tells.
- Any meaningful advancement must pay at least one cost from cost_mechanism.

---

## LAST CHAPTER CONTEXT
{{LAST_CHAPTER_SUMMARY}}
Open loops to respect:
{{OPEN_LOOPS}}

---

## THIS CHAPTER PLAN (keep within limits)
Chapter No: {{CHAPTER_NO}}
Word target: {{CHAPTER_WORD_TARGET}}
Threads limit (max threads in one chapter): {{THREADS_LIMIT}}

Scene goal (what must change by the end):
{{SCENE_GOAL}}

Primary conflict (who blocks it and how):
{{PRIMARY_CONFLICT}}

Beats (3-8):
{{BEATS}}

POV suggestions (1-3):
{{POV_SUGGESTIONS}}

Hook question at end:
{{HOOK_QUESTION}}

---

## OUTPUT FORMAT (STRICT)
You MUST output exactly two blocks in this order:

===CHAPTER_TEXT===
(Only the chapter prose. No headings. No bullet points. No author notes.)

===NEXT_CHAPTER_PACK===
(Strict JSON that validates against pack.schema.json. No trailing commentary.)
