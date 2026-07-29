---
name: cfold
description: >
  Use the cfold CLI to fold code into LLM-portable JSON, unfold LLM edits back
  onto a tree, AST-summarize Python packages (cfold sum), or build a once-per-git-tip
  state pack for multi-question agent runs. Invoke when the user wants to package
  a codebase for another LLM, apply a fold return, get a symbol/structure map of
  Python trees, or precompute a summary so agents stop re-walking the monorepo.
---

# cfold

**cfold** folds files + optional prompts into a single JSON for LLM interaction,
unfolds modified folds back onto a directory, and **summarizes Python trees via AST**
(`cfold sum`). Use it when shipping code into a context window, applying structured
edits, or building a **state summary once** for a series of questions on a fixed tip.

Source: [github.com/wr1/cfold](https://github.com/wr1/cfold).

## Install

```sh
pipx install git+https://github.com/wr1/cfold
# or
uv tool install git+https://github.com/wr1/cfold
# local dev
uv tool install .
```

Requires Python 3. Prefer `cfold` on `PATH` before running anything. If missing,
install as above — do not reimplement AST walkers in shell.

## Agent skill file

This `SKILL.md` lives at the **repo root**. Install for any agent runtime by
copying or **symlinking** into the tool’s skills directory:

| Runtime (examples) | Typical skill path |
|--------------------|--------------------|
| Home / shared | `~/.claude/skills/cfold/SKILL.md` → repo `SKILL.md` |
| Grok / Cursor-style | `~/.grok/skills/cfold/SKILL.md` → repo `SKILL.md` |
| Hermes | `~/.hermes/skills/…/cfold/SKILL.md` → repo `SKILL.md` |
| Project-local | `.cursor/skills/cfold/SKILL.md` or `.grok/skills/cfold/SKILL.md` |

```sh
mkdir -p ~/.claude/skills/cfold
ln -sf /path/to/cfold/SKILL.md ~/.claude/skills/cfold/SKILL.md
```

Symlink when developing cfold so agents always see the current skill.

## CLI reference source

CLI is defined with [treeparse](https://github.com/wr1/treeparse). Prefer
**`cfold -j` / `cfold --json`** for exact flags after CLI changes; do not invent
options from memory.

```sh
cfold -j > /tmp/cfold-cli.json
cfold --help
cfold sum --help
```

Boolean options (e.g. `--clip`) take an explicit value with treeparse:

```sh
cfold sum packages/foo -o summary.txt -c false
cfold fold src/foo --bare -o design.json -c false
```

Default `--clip` is **true** (copies result to clipboard) — use `-c false` on
headless agents (GB10, CI) so clipboard failures do not confuse the run.

---

## Commands (quick map)

| Command | Purpose | Typical output |
|---------|---------|----------------|
| `sum` | AST map of Python trees (cls / fn / imports / docs) | `summary.txt` |
| `fold` | Bundle files (+ optional prompt) into JSON for an LLM | `codefold.json` |
| `fold --bare` | Same without unfold/instruction boilerplate | design JSON |
| `view` | Inspect a fold file (tree / headers) | stdout |
| `add` | Append files to an existing fold JSON | updated fold |
| `unfold` | Apply a modified fold back onto a directory | tree edits |
| `rc` | Create/update `.foldrc` | config |

---

## When to use which

```
Need structure / “what exists where” for agents?
  → cfold sum   (cheap, scalable, once per git tip)

Need full source of a small design slice for offline LLM?
  → cfold fold … --bare   (pick files; watch token size)

Need LLM to return structured multi-file edits?
  → cfold fold (with dialect) → LLM → cfold unfold

Need to grow an existing fold?
  → cfold add -f fold.json extra.py
```

### `sum` vs `fold --bare`

| | `sum` | `fold --bare` |
|---|--------|----------------|
| Content | AST structure only | Full file contents |
| Size | Small–medium | Grows with source |
| Best for | State packs, routing, inventory | Deep design chat without FS |
| Python only | Yes (`.py` AST) | Any text files you pass |

If a bare fold exceeds ~400k chars (~100k tokens), drop files or use **`cfold sum`**
for the overview and fold only hot modules.

---

## Workflow A — once-per-state summary (multi-question agents)

For a **series of questions on a fixed codebase tip**, precompute the summary
**once**. Do not re-walk the monorepo inside every question.

```sh
COMMIT=$(git rev-parse --short HEAD)
OUT="${STATE_ROOT:-$HOME/temp}/state_${COMMIT}"
mkdir -p "$OUT"

# Scope to the domain of the question series (never sum an entire huge monorepo
# unless the series truly needs it).
cfold sum \
  packages/b3_blade packages/snb_blade packages/se_blade \
  -o "$OUT/CFOLD_SUM.txt" -c false

cat > "$OUT/META.md" << EOF
- commit: ${COMMIT}
- branch: $(git branch --show-current)
- built_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- tool: cfold sum
EOF
```

Per-question brief should say:

> State pack: `$OUT`. Read `META.md` + `CFOLD_SUM.txt` first. Do not re-run
> `cfold sum` or re-clone. Open source only for symbols the sum surfaces.

Optional deep slice after the sum points at hot files:

```sh
cfold fold \
  packages/b3_blade/src/b3_blade/dashboard.py \
  packages/b3_blade/src/b3_blade/optimize.py \
  --bare -o "$OUT/HOT_PATHS.json" -c false
```

**Rebuild the pack only when the tip moves** (new commit) or the sum is proven wrong.

---

## Workflow B — design-defining bare fold (offline / Claude web)

Portable snapshot of architecture-shaping Python for an LLM **without** filesystem access.

**Include:**

- Public surface: top-level `__init__.py` and re-exports
- Shapes: ABCs, Protocols, dataclasses, pydantic models, TypedDicts, enums
- CLI / app entry: `[project.scripts]`, `main.py`, `app.py`, `__main__.py`
- Domain modules: `engine.py`, `pipeline.py`, `solver.py`, `models.py`, `schema.py`, `core.py`
- Modules the README / architecture docs call out

**Exclude:** tests, build/cache, migrations, fixtures, generated stubs, vendored code,
pure helpers unless requested.

When the candidate list is borderline, **show it and let the user prune** before folding.

```sh
cfold fold path/to/a.py path/to/b.py ... --bare -o codebase-design.json -c false
python -m json.tool codebase-design.json > /dev/null
# report size: chars and ~tokens (chars/4); warn if huge
```

Tell the user: attach `codebase-design.json` and open with e.g. *“Attached is a
cfold --bare JSON of design-defining files in \<project\>. Use `tree` / `files` as
the codebase under discussion.”* Snapshot is frozen — re-run after design changes.

```sh
cfold add -f codebase-design.json extra.py   # grow without full redo
cfold view codebase-design.json
```

---

## Workflow C — fold → LLM edit → unfold

1. Fold working set (with dialect if using default instruction packaging):

   ```sh
   cfold fold src/mypkg -o codefold.json -c false
   # or with an extra prompt file:
   cfold fold src/mypkg -p prompt.md -o codefold.json -c false
   ```

2. LLM returns a fold JSON in the same schema (`instructions` + `files` with
   `path` / `content` / optional `delete`).

3. Apply:

   ```sh
   cfold unfold codefold_out.json -i /path/to/project -o /path/to/out
   ```

### Fold file shape (for agents producing edits)

- `instructions`: list of `{type: system|user|assistant, content, name?}`
- `files`: list of `{path, content?, delete?}`
  - modify: set `content`, `delete: false`
  - delete: `delete: true`
  - add: new `{path, content}`
  - rename: delete old + add new path

Prefer `--bare` only when the consumer does not need the unfold instruction
boilerplate (read-only design chat). Use a non-bare fold when the LLM is expected
to return edits for `unfold`.

---

## `sum` details

```sh
cfold sum path/to/pkg [path/to/pkg2 ...] -o summary.txt -c false
cfold sum path/to/pkg -t true -o summary_with_tests.txt -c false   # include tests
```

Produces an LLM-oriented text map:

- per-file relative path  
- non-stdlib imports  
- `cls: Name` (+ docstring)  
- `fn: name(args) -> ret` (+ docstring; methods indented under class)

Skips non-Python files; syntax errors are noted and skipped. This **is** the
Python tree walker — do not reimplement `ast` walkers in agent scripts unless
`cfold` is unavailable and install is blocked (then record that as a harness issue).

---

## `.foldrc`

```sh
cfold rc    # create or update .foldrc in the project
```

Use project `.foldrc` when the team wants consistent fold defaults; agents should
respect it if present but still pass explicit `-o` / `-c false` in automation.

---

## Behaviour guidance for agents

- **Prefer `sum` for inventory**, **`fold --bare` for small full-source slices**.
- **Scope paths** on monorepos; never dump the entire tree into context by default.
- On **headless / remote agents**: always `-c false`.
- **State packs**: build once per commit; questions only read the pack + dig surgically.
- After CLI changes: refresh from `cfold -j`, then update this skill’s command tables
  only if behaviour or workflows changed (not every flag rename if `-j` is the source of truth).
- If `cfold` is missing on the machine (e.g. agent hub): install with `uv tool install`
  or report `ISSUE-ENV` and fall back to targeted `rg` — do not invent a parallel sum tool.

---

## Quick reference

```sh
cfold sum packages/foo packages/bar -o summary.txt -c false
cfold fold a.py b.py --bare -o design.json -c false
cfold fold src/pkg -p prompt.md -o codefold.json -c false
cfold view codefold.json
cfold add -f codefold.json extra.py
cfold unfold codefold_out.json -i . -o ./applied
cfold rc
cfold -j
```

## Maintaining this skill

When the cfold CLI or recommended agent workflows change:

1. Run `cfold -j` and reconcile flags / commands with this file.
2. Keep Workflow A (state sum) and Workflow B (design bare fold) accurate.
3. Keep install + skill symlink instructions portable across Claude / Grok / Hermes.

Do not vendor large monorepo-specific package lists here; pass scoped paths at call time.
