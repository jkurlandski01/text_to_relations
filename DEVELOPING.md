## Development

### Set Up Dev Environment

There are two ways to set up the dev environment.

**Option A — full reproducible snapshot (recommended):**

```bash
pip install -r reqs.txt
pip install -e .
```

`reqs.txt` is a `pip freeze` snapshot of all dependencies — including dev tools like `build` and `twine` — and should be refreshed periodically when upgrading.

`pip install -r reqs.txt` installs every dependency but does not register the package itself, so the second `pip install` command is required. 

`pip install -e .` writes a `.pth` file into the venv's `site-packages` pointing at the `src` directory, making `text_to_relations` importable from any working directory without `sys.path` manipulation. You only need to do this once per venv — re-run it if you delete and recreate the venv.

**Option B — minimal install of top-level dev tools only:**

```bash
pip install -e ".[dev]"
```
This installs the runtime dependencies declared in `pyproject.toml` (e.g. `spacy`, `typing_extensions`) plus the dev extras (`build`, `twine`), and performs the editable install in one step, so no separate `pip install -e .` is needed. Unlike Option A, dependency versions are not pinned to a snapshot.

### Run Tests

```bash
python -m unittest
```

### Build

Run the following, which cleans old builds from `dist/` before building:
```bash
make build
```

### Upload

```bash
python3 -m twine upload dist/*
```
