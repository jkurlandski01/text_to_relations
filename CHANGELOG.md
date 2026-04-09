# Changelog

## 0.1.0

- Add `escape` parameter to `RegexString.__init__()`. When `escape=False`, items in `match_strs` are inserted into the regex pattern verbatim rather than being passed through `re.escape()`, allowing regex metacharacters such as `\d+` and `[A-Z]+` directly in match strings. All other constructor features (`whole_word`, `optional`, `prepend`, `append`, `concat()`) work normally with `escape=False`.

---

- Add `SimpleExtractionPhase`: a concrete subclass of `ExtractionPhaseABC` that accepts `relation_name`, `regex_patterns`, and `chain` as constructor arguments, so callers that need no custom behaviour can avoid defining a subclass.
- Add `ChainLink` class with `start_property` and `end_property` fields, so each step in a proximity chain maps matched annotations to named attributes in the extracted relation.
- Add automatic validation of `ExtractionPhaseABC` subclasses at construction time: required fields must be set, chain links must be continuous, and property names must be unique across the chain.
- Add `find_match(text, entity_annotations=None)` as the standard entry point for relation extraction; accepts optional externally-produced annotations alongside those derived from `regex_patterns`.
- Add `examples/README.md` with a sequence diagram documenting the end-to-end extraction flow.

### Breaking changes

- **`ChainLink`** now takes six required positional arguments: `start_type`, `start_property`, `min_distance`, `max_distance`, `end_type`, `end_property`. The `start_property` and `end_property` arguments are new; existing `ChainLink` constructions must be updated.

- **`run_phase()` and `check_annotation_proximity()` removed.** Use `find_match()` instead. Subclasses that overrode either method must be rewritten.

- **`create_relation_annotation()` and `_create_relation_annotation()` removed.** This logic is now internal to `run_loop()`.

- **`run_loop()`** now requires a `relation_name: str` argument (added in place of the removed `create_relation_annotation` helpers).

- **`determine_new_annotation_properties` callback** (passed to `ExtractionLoop`) now takes only `(match_triples)`, dropping the previously-passed `doc` argument.

- **`TokenAnn.build_annotation_distance_regex()`**: parameter `token_kind` renamed to `token_type`. Callers passing this argument by keyword must update their code.

## 0.0.6

- Add `ExtractionPhaseABC.run_chained_loops()`: given regex patterns and a
  proximity chain, handles all boilerplate (building annotations, merged
  representation, constructing loops, extracting properties) so clients only
  need to define what to match and how close together.
- Make `ExtractionPhaseABC.run_phase()` concrete: splits the document on blank
  lines and calls `check_annotation_proximity()` for each entry. Subclasses that
  override `run_phase()` directly are unaffected.
- Add `ExtractionPhaseABC.check_annotation_proximity()` as a non-abstract base
  method that raises `NotImplementedError`. Subclasses using the default
  `run_phase()` must override it; subclasses that override `run_phase()` directly
  do not.
- Add `verbose` parameter to `ExtractionPhaseABC.__init__()`.
- Add `case_insensitive` parameter to `RegexString.get_match_triples()`. When `True`,
  matching ignores case via `re.IGNORECASE` and the matched text in each triple preserves
  the original casing of the input string.
- Update `DEVELOPING.md`: add venv creation/activation steps, replace `pip`
  with `python3 -m pip`, and document the required `spacy` model download.

### Breaking changes

- **`ExtractionLoop.__init__`** now raises `ValueError` if `regex_str` is not a `str`.
  Previously the parameter was typed as `RegexString` but used internally as a plain string,
  causing a silent runtime error. If you have a `RegexString` object, pass
  `regex_str.get_regex_str()` instead.

- **`RegexString.match_strs`** items are now escaped via `re.escape()` before being
  inserted into the regex pattern. Regex metacharacters (e.g. `(`, `[`, `.`, `\`) in
  `match_strs` items are treated as literals. If you were embedding regex syntax directly
  in `match_strs` items, move that syntax to `prepend`/`append` or use `concat()`.

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
