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

## For Experienced Regex Users

If you are comfortable writing raw regular expressions, `RegexString` may not add much value for entity recognition. The constructor escapes all match strings via `re.escape()`, which means regex metacharacters are treated as literals--so patterns like `\d+` cannot be expressed through the normal constructor. The `from_regex()` factory method exists as a work-around for this case, letting you plug a hand-written regex directly into the pipeline:

```python
number_rs = RegexString.from_regex(r'(\d+)')
```

Where the framework pays off for everyone, including experienced regex users, is **relation extraction**. Consider linking a stamp ID to its denomination when they appear within four tokens of each other. In raw regex:

```python
import re
pattern = r'(#\s\d+(?:\w+)?)(?:\s\S+){0,4}\s(\d\d?(?:c|¢))'
matches = re.findall(pattern, text)
# matches is a list of (stamp_id, denomination) tuples -- but unlabeled,
# unfiltered, and with no structure beyond what re.findall() provides
```

With the framework:

```python
chain = [
    ChainLink(start_type='StampID', start_property='StampID',
              min_distance=0, max_distance=4,
              end_type='Denomination', end_property='Denomination'),
]
phase = SimpleExtractionPhase(relation_name='StampDescription',
                               regex_patterns=regex_patterns, chain=chain)
results = phase.find_match(text)
# results is a list of Annotation objects with labeled properties
```

Extending the raw regex approach to four entities — each pair with its own distance constraint — means chaining the pattern into one long, nearly unreadable expression, and then writing additional code to label, filter, and structure the output. With the framework, each new entity is one more dict entry and one more `ChainLink`, each self-contained and labeled — complexity grows linearly and readably. For a full four-entity example, see `examples/extract_stamp_description.py`.

## Further Reading

For a full walkthrough, including entity recognition and relation extraction examples, see [TUTORIAL.md](TUTORIAL.md).

A working end-to-end relation extraction example can be found in `examples/extract_stamp_description.py`. Run it with:

```
python -m examples.extract_stamp_description
```
