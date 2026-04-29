## Development

### Set Up Dev Environment

There are two ways to set up the dev environment. Both require creating and activating a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Option A — full reproducible snapshot (recommended):**

```bash
python3 -m pip install -r reqs.txt
python3 -m pip install -e .
python3 -m spacy download en_core_web_lg
```

`reqs.txt` is a `pip freeze` snapshot of all dependencies — including dev tools like `build` and `twine` — and should be refreshed periodically when upgrading.

`python3 -m pip install -r reqs.txt` installs every dependency but does not register the package itself, so the second `pip install` command is required.

`python3 -m pip install -e .` writes a `.pth` file into the venv's `site-packages` pointing at the `src` directory, making `text_to_relations` importable from any working directory without `sys.path` manipulation. You only need to do this once per venv — re-run it if you delete and recreate the venv.

**Option B — minimal install of top-level dev tools only:**

```bash
python3 -m pip install -e ".[dev]"
python3 -m spacy download en_core_web_lg
```
This installs the runtime dependencies declared in `pyproject.toml` (e.g. `spacy`, `typing_extensions`) plus the dev extras (`build`, `twine`), and performs the editable install in one step, so no separate `pip install -e .` is needed. Unlike Option A, dependency versions are not pinned to a snapshot.

### Run Tests

```bash
python -m unittest
```

### Linting and Type Checking

```bash
pylint src/ tests/ examples/
mypy src/ tests/ examples/
```

### Debugging Chain Extraction

Pass `verbose=True` to any `ExtractionPhaseABC` subclass or to `run_loop()` directly to print a trace of the matching process.

Each line is indented by two spaces per loop level, so you can see the recursion depth at a glance. A typical successful trace looks like this:

```
Loop 0 [AtLeast→CARDINAL, tokens=0..3] — [AtLeast, Token, CARDINAL, UNIT_OF_MEASUREMENT, ...]
  match: ['AtLeast', 'Token', 'CARDINAL']

  Loop 1 [CARDINAL→UNIT_OF_MEASUREMENT, tokens=0..2] — [CARDINAL, UNIT_OF_MEASUREMENT, Token, ...]
    match: ['CARDINAL', 'UNIT_OF_MEASUREMENT']
    SUCCESS → <'MinMax'(text='lower limit of 87 ft-lb', ...)>
```

A failing trace where a chain partially matches but cannot complete:

```
Loop 0 [AtLeast→CARDINAL, tokens=0..3] — [AtLeast, Token, CARDINAL, UNIT_OF_MEASUREMENT, ...]
  match: ['AtLeast', 'Token', 'CARDINAL']

  Loop 1 [CARDINAL→UNIT_OF_MEASUREMENT, tokens=0..2] — [CARDINAL, Token, Token, AtMost, ...]
    NO MATCH
  ^ backtracking
  NO MATCH
```

**Reading the output:**

- The header line `Loop N [A→B, tokens=min..max]` shows which chain step is running and the allowed gap size.
- The annotation list after `—` shows what types are visible from the current search position (truncated to 20).
- `match: [...]` shows the annotation types consumed by this loop's regex.
- `^ backtracking` means the recursive call from the line above returned no result; the current loop will try its next candidate match if one exists.
- `NO MATCH` means this loop exhausted all candidates without success.
- `SUCCESS →` shows the final `Annotation` that was built.

**Common failure patterns:**

- Loop 0 finds a `match` but the next loop immediately shows `NO MATCH` — the gap between the two annotation types is larger than `max_distance` allows.
- The annotation list at a deeper loop level doesn't contain the expected endpoint type at all — an upstream match consumed the wrong annotation, leaving the remainder without a valid target.

### Build

Run the following, which cleans old builds from `dist/` before building:
```bash
make build
```

### Upload

```bash
python3 -m twine upload dist/*
```
