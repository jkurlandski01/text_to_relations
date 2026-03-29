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

color_phrase = RegexString.concat_with_word_distances(qualifiers, colors,
                                                      min_nbr_words=0,
                                                      max_nbr_words=0)
print(color_phrase.get_match_triples(text))
# [('bright blue', 11, 22), ('dark green', 40, 50), ('brown', 57, 62)]
```

`get_match_triples()` returns a list of `(matched_text, start_offset, end_offset)` tuples.

The key classes — `RegexString`, `Annotation`, `TokenAnn`, `SentenceAnn`, and `ExtractionPhaseABC` — are all importable directly from `text_to_relations`.

## Further Reading

For a full walkthrough, including entity recognition and relation extraction examples, see [TUTORIAL.md](TUTORIAL.md).
