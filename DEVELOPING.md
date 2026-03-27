## Development

### Run Tests

Create a virtual environment with reqs.txt, then run:
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
