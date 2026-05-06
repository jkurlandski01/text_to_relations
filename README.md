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

The key classes — `RegexString`, `Annotation`, `TokenAnn`, `SentenceAnn`, and `ExtractionPhaseABC` — are all importable directly from `text_to_relations`.

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

Consider the need to perform natural language processing on a document such as the following, where "11A" and #17" are stamp IDs.

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
# 'results' is a list of Annotation objects with labeled properties
```

To be sure, using raw regular expressions is more concise. But consider how much time it took to craft and verify the regular expression--not to mention edit it when (inevitably) it needs to be revised.

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

At this point you want to create a ChainLink that looks for a StampId followed by a MONEY or a Denomination. The problem is that `ChainLink.end_type` is a single string, so there is no direct OR support. The workaround is to normalize both sources to a shared type name before the chain runs.

# FIXME: We discuss case-insensitivity for RegexString and get_match_triples(), but not for relation extraction.

Let's call the combination of a MONEY or a Denomination a StampValue object. The steps to perform this task are:
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

# Step 2: Add Denomination to regex_patterns; (?i) makes 'cents' case-insensitive
cents_rs = RegexString([r'(?i)cents'], escape=False, prepend=r'\d\d?')
regex_patterns = {
    'StampID':    id_rs,
    'Denomination': cents_rs,
}

# Step 3: use Denomination as end_type so the chain accepts either source
chain = [
    ChainLink(start_type='StampID', start_property='StampID',
              min_distance=0, max_distance=4,
              end_type='Denomination', end_property='denomination'),
]
phase = SimpleExtractionPhase(relation_name='StampDescription',
                               regex_patterns=regex_patterns,
                               chain=chain)
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

Power users overriding ExtractionPhaseABC themselves can create a `verbose` parameter for their __init__() methods, and pass it to ExtractionPhaseABC's init function.

See the "Debugging Chain Extraction" section in Developing.md for how to read the chain-matching trace output.


## Further Examples

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

FIXME: proofread as copy editor for typos and other minor mistakes and as content editor for organization and coherence issues.
