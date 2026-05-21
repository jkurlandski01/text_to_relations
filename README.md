# Text-To-Relations

**Text-To-Relations: a tool for Information and Relation Extraction**

Text-To-Relations is built around a two-layer pipeline:

1. **Entity recognition** — `RegexString` provides a simple interface for building complex regular expressions that identify typed entity spans (e.g. a stamp ID, a denomination, a perforation value) in raw text.
2. **Relation extraction** — `ExtractionPhaseABC` and its supporting machinery take those entity spans and find relationships between them based on proximity in token space (e.g. "a StampID followed within 4 tokens by a Denomination"). You define which entity types to link and how close together they must appear; the framework handles the rest.

The two layers are independent: you can use `RegexString` alone for entity recognition tasks, or combine both layers for full relation extraction.

Source code at [GitHub text_to_relations](https://github.com/jkurlandski01/text_to_relations).

## Installation

After setting up your virtual environment:

```
pip install text_to_relations
```

If your Python version is less than 3.11, also run:
```
pip install --upgrade pip
pip install typing_extensions
```

Text-To-Relations requires Spacy:
```
pip install -U spacy
python -m spacy download en_core_web_lg
```

Text-To-Relations has been tested on:
- Python 3.9.18 and Python 3.11.6 on MacOS Sequoia 15.2
- Python 3.10.12 on Ubuntu 22

## Quick Start

```python
from text_to_relations import RegexString

text = "The sky is bright blue and the leaves are dark green or just brown."

# Match individual colors
colors = RegexString(['red', 'blue', 'green', 'brown'], whole_word=True)

# Optionally prepend a qualifier
qualifiers = RegexString(['bright', 'dark', 'dull'], whole_word=True, optional=True)

color_phrase = RegexString.concat_with_word_distances(
    qualifiers, colors,
    min_nbr_words=0,
    max_nbr_words=0)
print(color_phrase.get_match_triples(text))
# [('bright blue', 11, 22), ('dark green', 40, 50), ('brown', 57, 62)]
```

`get_match_triples()` returns a list of `(matched_text, start_offset, end_offset)` tuples.

The function has an optional `case_sensitive` parameter that can be set to False.
```
def get_match_triples(self, text: str, case_sensitive: bool = True) -> List[Tuple]
```

The key classes in this project — `RegexString`, `SimpleExtractionPhase`, and `ExtractionPhaseABC` — are importable directly from `text_to_relations`.

### For Experienced Regex Users

If you are comfortable writing raw regular expressions, `RegexString` may not add much value for entity recognition on its own. But Text-to-Relations still offers what we think are very useful tools for **relation extraction**. See below.

The relation extraction tools require RegexString objects, however. If you prefer to write your own regular expressions, these can be converted into RegexString objects which can be used for downstream relation extraction. By default the constructor escapes all match strings via `re.escape()`, so metacharacters like `\d+` are treated as literals. Pass `escape=False` to use regex syntax directly in `match_strs` while still getting all the constructor features — `whole_word`, `optional`, `prepend`, `append`, and the OR-ing machinery:

```python
number_rs = RegexString([r'\d+'], escape=False)
digits_or_lower = RegexString([r'\d+', r'[a-z]+'], escape=False)
number_word = RegexString([r'\d+'], escape=False, whole_word=True)
```

Use `from_regex()` only when you need to pass a *complete* hand-written regex that cannot be expressed as a list of alternates — for example, when combining two already-built `RegexString` objects:

```python
perf_combined_rs = RegexString.from_regex(
    f'(?:{imperf_rs.get_regex_str()}|{perf_sized_rs.get_regex_str()})')
```

## Relation Extraction

Consider the need to perform natural language processing on a document such as the following, where "11A" and "#17" are stamp IDs.

```
# 11A - 1853-55 3¢ George Washington, dull red, type II, imperf

# 17 - 1851 12c Washington imperforate, black
```

Suppose you want to link a stamp ID to its denomination when they appear within four tokens of each other. A first pass at doing this with a raw regular expression might look like this:

```python
import re
pattern = r'(#\s\d+(?:\w+)?)(?:\s\S+){0,4}\s(\d\d?(?:c|¢))'
matches = re.findall(pattern, text)
# matches is a list of (stamp_id, denomination) tuples -- but unlabeled,
# unfiltered, and with no structure beyond what re.findall() provides
```

Compare the use of regular expressions above to how you might extract this information using the Text-to-Relations framework:

```python
# Stamp ID: e.g. '# 11A', '# 17', '# 62B'
id_rs = RegexString(['#'], append=r'\s\d+(?:\w+)?')

# Denomination: e.g. '3¢', '12c', '5c', '1c', '10c'
cent_rs = RegexString(['c', '¢'], prepend=r'\d\d?')

regex_patterns = {
    'StampID':      id_rs,
    'Denomination': cent_rs,
}

chain = [
    ChainLink(start_type='StampID', start_property='StampID',
              min_distance=0, max_distance=4,
              end_type='Denomination', end_property='denomination'),
]
phase = SimpleExtractionPhase(relation_name='StampDescription',
                               regex_patterns=regex_patterns,
                               chain=chain)
results = phase.find_match(text)
# 'results' is a list of dicts, each with labeled properties
```

To be sure, using raw regular expressions is more concise. But consider how much time it took to craft and verify the regular expression — not to mention edit it when (inevitably) it needs to be revised.

Moreover, extending the raw regex approach to four entities — each pair with its own distance constraint — means chaining the pattern into one long, nearly unreadable expression, and then writing additional code to label, filter, and structure the output. With the Text-to-Relations framework, each new entity is one more dict entry and one more `ChainLink`, each self-contained and labeled. In other words, complexity grows linearly and readably, and it is highly maintainable. For a full four-entity example, see `examples/extract_stamp_description.py`.


## Tips

### Imposing Boundaries on Relations

To prevent a chain link from matching across a boundary annotation — for example, a conjunction that separates two independent phrases — pass a `forbidden_gap_type` parameter to the `ChainLink` constructor. Any candidate match whose gap contains an annotation of that type is rejected:

```python
chain = [
    ChainLink(start_type='StampID', start_property='StampID',
              min_distance=0, max_distance=4,
              end_type='Denomination', end_property='denomination',
              forbidden_gap_type='Conjunction'),
]
```

With this setting, a StampID and Denomination separated by a `Conjunction` annotation will not produce a match even if they are within four tokens of each other. See the unit tests for an additional example.

### Combining Text-to-Relations with Upstream Named Entity Recognition

Text-to-Relations allows the user to combine named entities which were identified previously (upstream) with RegexString objects. The example below shows how to combine a RegexString object named StampID with incoming MONEY named entities which were extracted previously (for example, by Spacy).

```python
# Stamp ID detected by this phase via RegexString
id_rs = RegexString(['#'], append=r'\s\d+(?:\w+)?')

regex_patterns = {
    'StampID': id_rs,
}

# Denominations supplied as MONEY entities from an upstream NER model;
# each entry is a dict with 'type', 'text', 'start', and 'end' keys.
money_annotations = ner_model.extract(text)
# e.g. [{'type': 'MONEY', 'text': '3¢', 'start': 16, 'end': 18}, ...]

chain = [
    ChainLink(start_type='StampID', start_property='StampID',
              min_distance=0, max_distance=4,
              end_type='MONEY', end_property='money'),
]
phase = SimpleExtractionPhase(relation_name='StampDescription',
                               regex_patterns=regex_patterns,
                               chain=chain)
results = phase.find_match(text, entity_annotations=money_annotations)
```

#### Matching Either a RegexString or an Incoming Entity in One ChainLink

Let's continue the example immediately above. Suppose that the incoming MONEY entities correctly identify "3 cents" and "3 ¢", but fail to detect strings like "3 c". You may need to identify these with the following:

```
cents_rs = RegexString(['c'], prepend=r'\d\d?')

regex_patterns = {
    'Denomination': cents_rs,
}
```

At this point you want to create a ChainLink that looks for a StampID followed by a MONEY or a Denomination. The problem is that `ChainLink.end_type` is a single string, so there is no direct OR support. The workaround is to normalize both sources to a shared type name before the chain runs.

The steps to perform this task are:
1. Rename incoming MONEY entities to `Denomination` so they share a type name with the locally-detected denominations.
2. Use `Denomination` as the key in `regex_patterns`.
3. Set `end_type='Denomination'` in the `ChainLink`.

```python
# External NER extracts MONEY as well as other common named entities.
all_incoming_annotations = ner_model.extract(text)

# Step 1: Rename incoming MONEY entities to Denomination.
incoming_entity_annotations = [
    {**ann, 'type': 'Denomination'} if ann['type'] == 'MONEY' else ann
    for ann in all_incoming_annotations
]

# Step 2: Add Denomination to regex_patterns.
cents_rs = RegexString(['cents'], prepend=r'\d\d?')
regex_patterns = {
    'StampID':    id_rs,
    'Denomination': cents_rs,
}

# Step 3: use Denomination as end_type so the chain accepts either source.
# case_sensitive=False so 'Cents', 'CENTS', etc. are also matched.
chain = [
    ChainLink(start_type='StampID', start_property='StampID',
              min_distance=0, max_distance=4,
              end_type='Denomination', end_property='denomination'),
]
phase = SimpleExtractionPhase(relation_name='StampDescription',
                               regex_patterns=regex_patterns,
                               chain=chain,
                               case_sensitive=False)
results = phase.find_match(text, entity_annotations=incoming_entity_annotations)
```

The chain sees a single `Denomination` type regardless of which source produced each annotation.

### Debugging Relation Extraction with Verbose Mode

Relation extraction is implemented via a recursive function. You can run relation extraction in verbose mode to see this recursive behavior so that you can understand why matching does or does not take place.

To run in verbose mode, set verbose to True when creating an object with SimpleExtractionPhase.
```
phase = SimpleExtractionPhase(relation_name='StampDescription',
                               regex_patterns=regex_patterns,
                               chain=chain,
                               verbose=True)
```

Power users overriding `ExtractionPhaseABC` themselves can create a `verbose` parameter for their `__init__()` methods, and pass it to `ExtractionPhaseABC`'s `__init__()`.

See the "Debugging Chain Extraction" section in Developing.md for how to read the chain-matching trace output.


## Further Examples

This section points to places where users can find more documentation on this package, from a full tutorial to examples on specific functionality not already mentioned in this ReadMe.

### The Tutorial
For a full walkthrough, including entity recognition and relation extraction examples, see [TUTORIAL.md](TUTORIAL.md).

Additionally, two runnable scripts in `examples/` illustrate the two main usage patterns:

`extract_stamp_description.py` shows the self-contained case: all entity types (StampID, Denomination, TypePhrase, Perforation) are detected by regex patterns defined inside the phase itself, and `find_match()` is called with only the document text.

`extract_min_max.py` shows the externally-supplied case: the phase only detects Range entities; Number and Unit_of_Measure entities are produced by an external tool (here, simple regex matching standing in for a NER model or gazetteer) and passed to `find_match()` via its `entity_annotations` parameter. This is the pattern to follow whenever part of the entity detection is handled outside the library.

Run them with:

```
python -m examples.extract_stamp_description
python -m examples.extract_min_max
```

Both scripts accept `-v` / `--verbose` to print the internal chain-matching trace.

### Additional Functionality

#### Relation Extraction: Allowing Overlapping Results

By default, `find_match()` returns at most one result per starting annotation. Once a chain rooted at a given span produces a match, any other candidate whose start falls inside that result's span is suppressed.

Set `allow_overlapping=True` on the phase when multiple entities of the same type all link to a single shared entity and you want a result for each one:

```python
text = "speed and torque must both exceed 100 rpm."

regex_patterns = {
    'Metric':    RegexString(['speed', 'torque'], whole_word=True),
    'Threshold': RegexString([r'\d+'], escape=False, append=r'\s+rpm'),
}
chain = [
    ChainLink('Metric', 'metric', 0, 5, 'Threshold', 'threshold'),
]

# Default: only the first Metric (speed) produces a result.
phase = SimpleExtractionPhase(
    relation_name='MetricLimit',
    regex_patterns=regex_patterns,
    chain=chain,
)
phase.find_match(text)
# [{'type': 'MetricLimit',
#   'text': 'speed and torque must both exceed 100 rpm',
#   'start': 0, 'end': 41,
#   'metric': 'speed', 'threshold': '100 rpm'}]

# allow_overlapping=True: both metrics produce a result.
phase = SimpleExtractionPhase(
    relation_name='MetricLimit',
    regex_patterns=regex_patterns,
    chain=chain,
    allow_overlapping=True,
)
phase.find_match(text)
# [{'type': 'MetricLimit',
#   'text': 'speed and torque must both exceed 100 rpm',
#   'start': 0, 'end': 41,
#   'metric': 'speed', 'threshold': '100 rpm'},
#  {'type': 'MetricLimit',
#   'text': 'torque must both exceed 100 rpm',
#   'start': 10, 'end': 41,
#   'metric': 'torque', 'threshold': '100 rpm'}]
```

Both `speed` and `torque` are within five tokens of `100 rpm`, so both chains match the same threshold annotation. With the default `allow_overlapping=False` only the first is returned because `torque` falls inside its span. With `allow_overlapping=True` both are returned.

See `tests/relation_extraction_tests/test_extraction_loop.py` for additional examples.

#### Relation Extraction: Same Annotation Type Appearing Twice in a Chain

A chain can include the same annotation type more than once. The key is to give each occurrence a distinct `end_property` so both values appear as separate keys in the result dict. Each link's `start_property` must also match the preceding link's `end_property` — the phase validates this at construction time.

The min-max pattern is a natural example — "between 170 and 220 pounds" contains two `Number` annotations:

```python
regex_patterns = {
    'Range': RegexString(['between', 'within the range of']),
}
chain = [
    ChainLink(start_type='Range',         start_property='range_phrase',
              min_distance=0, max_distance=3,
              end_type='Number',           end_property='min_number'),
    ChainLink(start_type='Number',        start_property='min_number',
              min_distance=0, max_distance=2,
              end_type='Number',           end_property='max_number'),
    ChainLink(start_type='Number',        start_property='max_number',
              min_distance=0, max_distance=2,
              end_type='Unit_of_Measure', end_property='unit'),
]
# Result for "between 170 and 220 pounds" (Number and Unit_of_Measure
# supplied via entity_annotations):
# {'type': 'MinMax', ..., 'range_phrase': 'between',
#  'min_number': '170', 'max_number': '220', 'unit': 'pounds'}
```

For a complete runnable example see `examples/extract_min_max.py`.

#### RegexString: Non-Capturing Groups

`RegexString` wraps its alternation in a non-capturing group `(?:...)` by default. This is intentional: the library's own matching functions assume non-capturing groups, and `get_match_triples()` will return incorrect results if capturing groups are present.

The only reason to set `non_capturing=False` is if you are calling `get_regex_str()` to extract the raw pattern for use with your own code outside the library, and that code requires capturing groups:

```python
# Default: non-capturing group.
rs = RegexString(['cat', 'dog'])
rs.get_regex_str()
# '(?:dog|cat)'

# non_capturing=False: capturing group.
rs = RegexString(['cat', 'dog'], non_capturing=False)
rs.get_regex_str()
# '(dog|cat)'
```

Do not use `non_capturing=False` on any `RegexString` that will be passed to `get_match_triples()`, `concat()`, `concat_with_word_distances()`, or a `regex_patterns` dict.

#### RegexString: Optional Whitespace in concat()

`RegexString.concat()` joins two patterns with no separator by default, requiring the second pattern to immediately follow the first character-for-character. Pass `insert_opt_ws=True` to allow a single optional whitespace character at the boundary.

The typical use case is a number-unit pair that appears both with and without a space:

```python
number_rs = RegexString([r'\d+'], escape=False)
unit_rs   = RegexString(['rpm', 'mph'])

# Default: matches '100rpm' but not '100 rpm'.
speed_rs = RegexString.concat(number_rs, unit_rs)

# insert_opt_ws=True: matches both '100rpm' and '100 rpm'.
speed_rs = RegexString.concat(number_rs, unit_rs, insert_opt_ws=True)
speed_rs.get_match_triples("engine runs at 100 rpm or 200rpm")
# [('100 rpm', 15, 22), ('200rpm', 26, 32)]
```

For patterns that need one or more full words between them, use `concat_with_word_distances()` instead. (See the Quick Start for an example.)

#### RegexString: build_regex_string()

`build_regex_string()` is a shorthand for chaining three or more word groups with distance constraints between each consecutive pair. The input alternates between a list of strings and an integer max word distance:

```python
inputList = [['good', 'great', 'excellent'], 1, ['results', 'performance', 'work']]
praise_rs = RegexString.build_regex_string(inputList)
praise_rs.get_match_triples("The audit found excellent results and great overall performance.")
# [('excellent results', 16, 33), ('great overall performance', 38, 63)]
```

Each integer is the maximum number of words permitted between the two adjacent groups; the minimum is always 0. For three groups:

```python
inputList = [['incredibly'], 0, ['good', 'great'], 1, ['work', 'job']]
# matches 'incredibly good work', 'incredibly great solid job', etc.
RegexString.build_regex_string(inputList)
```

The list must have an odd number of elements and at least three. For two groups, use `concat_with_word_distances()` directly. For any link that needs a non-zero minimum distance, also use `concat_with_word_distances()` directly — `build_regex_string()` always uses `min_nbr_words=0`.
