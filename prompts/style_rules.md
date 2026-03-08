# Style Rules (Hard Constraints)

## Tone & Texture
- Urban underworld, Northeast China texture (ice, old industry, debt-of-favor, rules).
- Strong-but-explainable: heightened grit/physicality/courage/means, but no magic, no invincible wins.
- Violence: non-graphic. Focus on rhythm, positioning, consequences, leverage. Avoid gore.

## Anti-AI Tell Rules
- No summary paragraphs, no moral lectures, no "in conclusion".
- Avoid vague adjective piles (e.g., mysterious, grand, unbelievable).
- No narrator explaining the world; show via action, objects, constraints.
- No template jokes or repeating catchphrases. Dialogue must arise from context.

## Concrete Detail Policy (Density, Not Quota)
- Use concrete details as needed to make scenes believable, but do not check boxes.
- Prefer: object details, sensory cues, small logistics (time, distance, money, temperature).
- In high-tension scenes, details are brief and sharp; in slower scenes, details can breathe.

## Dialogue Voice System (Hard)
- Major characters MUST have distinguishable speaking voices; lines should not be interchangeable after removing name tags.
- Enforce per-character speech_profile (register / tempo / sentence shape / profanity level / signature markers).
- In one scene, keep at least 3 visible contrasts among speakers (e.g., terse vs verbose, slang vs formal, profanity-heavy vs clean).
- Avoid all-character same-length lines and same syntax cadence.
- If a character is stressed by trigger_sensitivities, voice should drift in a consistent direction (faster, rougher, more fragmented, etc.).

## Chapter Mechanics (Web-serial)
- Within the first ~300 words: establish goal or conflict.
- Middle: introduce a setback or misread.
- Late: reversal / hard推进 (a move that changes the board).
- End: a hook question that forces the next chapter.

## Character Consistency Rules
- If a character trigger_sensitivities happens, behavior MUST shift and must be observable via behavioral_tells.
- Any meaningful advancement must pay at least one cost in cost_mechanism (reputation / law_attention / relationship_damage / evidence_risk / moral_decay).

## Output Policy
- Output only the requested blocks and formats.
- No meta commentary. No "as an AI".


## Character Evolution System (Hard)
- Do NOT hard-code fixed personality outputs (e.g., permanent one-note tone). Use condition-based shifts by event, relationship change, and phase.
- Important characters must evolve via visible state changes (trust, fear, loss tolerance, moral load), not only plot labels.
- After major events, reflect at least one behavior shift and one dialogue-shift within 1-2 chapters.
- Avoid fixed catchphrase loops; keep voice identity through ranges and conditional choices.

## Bright/Dark Line Coupling (Hard)
- Each rolling 2-3 chapters must advance both: 明线 (current conflict/business/power) and 暗线 (old case/hidden player/capital chain).
- 暗线揭示必须分层：侧证 -> 可验证证据 -> 局部真相，禁止一次性全开。
- Any dark-line gain should carry a present-time cost on the bright line (law pressure, relationship damage, resource loss, etc.).
