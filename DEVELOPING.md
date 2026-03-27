## Development

### Set Up Dev Environment

```bash
pip install -r reqs.txt
```

Note: `reqs.txt` is a `pip freeze` snapshot and should be refreshed periodically when upgrading dependencies. Alternatively, contributors can install just the top-level dev tools with `pip install -e ".[dev]"`.

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
