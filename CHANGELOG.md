# Changelog

## 0.0.5

- Re-export `RegexString` from package `__init__.py` files, enabling shorter imports:
  - `from text_to_relations import RegexString`
  - `from text_to_relations.relation_extraction import RegexString`

## 0.0.4

- Add `py.typed` marker file (PEP 561) to fix mypy `import-untyped` errors in client projects.
- Add explicit `[build-system]` section to `pyproject.toml`.

## 0.0.3

- Add `extraction_loop.py` for relation extraction without repetitive code.
- Add `reqs.txt` for development/test environments.

## 0.0.2

- Allow use of a different Spacy English language model.
- Make library compatible with pre-3.11 versions of Python.

## 0.0.1

- Initial release.
