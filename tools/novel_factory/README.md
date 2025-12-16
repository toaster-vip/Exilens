# novel_factory CLI

Offline CLI for producing serialized web novel chapters with a copy–paste workflow. The tool does **not** call any LLM API. Instead, it prepares prompts that you paste into ChatGPT, then ingests the returned chapter text plus a JSON pack.

## Repository-aware behavior

The CLI works directly against the repository root:
- Prompts are stored under `chapters/00NN/prompt_next.md`.
- Ingested outputs and summaries live beside the prompts under `chapters/00NN/`.
- Canon data is read from `bible/`, `characters/`, `prompts/`, and `timeline/`.
- Exports are written to `exports/novel.docx` and `exports/novel.txt`.

## Install (editable)

```bash
cd tools/novel_factory
pip install -e .
```

## Commands

All commands can be invoked via `python -m novel_factory` or `novel-factory`.

### init

```bash
python -m novel_factory init --project "slug" --topic "one line" [--target-words 1000000] [--chapter-words 2500] [--threads 3]
```

- Updates `timeline/continuity.json` with project metadata and resets progress.
- Ensures `notes/global_summary.md` exists.
- Generates the first prompt: `chapters/0001/prompt_next.md`.

### next

```bash
python -m novel_factory next [--chapter N] [--copy]
```

- Builds the prompt for chapter `N` (or the next pending chapter when omitted).
- Writes it to `chapters/00NN/prompt_next.md` and prints it.
- `--copy` copies the prompt to clipboard when `pyperclip` is available.

### ingest

```bash
python -m novel_factory ingest --chapter N (--from-file path | --from-clipboard)
```

Provide ChatGPT output containing:

```
===CHAPTER_TEXT===
...prose...
===NEXT_CHAPTER_PACK===
{ ...json matching prompts/pack.schema.json }
```

- Saves `output.md` for the chapter.
- Validates and stores the JSON pack as `summary.json`.
- Updates continuity (timeline, open loops, progress) and appends to `notes/global_summary.md`.
- Creates/updates A-tier character cards for new names while never overwriting `characters/S/`.
- Automatically generates the next chapter prompt.

### export

```bash
python -m novel_factory export [--docx] [--txt]
```

Exports all ingested chapter texts in order to `exports/novel.docx` and/or `exports/novel.txt`.

### status

```bash
python -m novel_factory status
```

Shows completed chapter count, estimated words, continuity phase, and open loop counts.

## Copy–paste workflow

1. Run `init` once to seed metadata and create chapter 1 prompt.
2. Open the prompt file and paste it into ChatGPT.
3. Copy ChatGPT's response (prose + JSON pack) into `ingest` via file or clipboard.
4. Use `next` to obtain the following prompt and repeat.
5. Periodically run `export` to generate DOCX/TXT manuscripts.