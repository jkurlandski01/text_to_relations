# Text-To-Relations: Tutorial

## Table of Contents
- [Text-To-Relations: Tutorial](#text-to-relations-tutorial)
  - [Table of Contents](#table-of-contents)
  - [Entity Recognition](#entity-recognition)
    - [RegexString](#regexstring)
      - [Case-Insensitive Matching](#case-insensitive-matching)
    - [Example 1](#example-1)
    - [Example 2](#example-2)
    - [Example 3](#example-3)
    - [Example 4: Using build\_regex\_string( )](#example-4-using-build_regex_string-)
    - [Example 5: Appending More Complicated Regular Expressions](#example-5-appending-more-complicated-regular-expressions)
  - [Relation Extraction](#relation-extraction)
    - [The extraction phase](#the-extraction-phase)
    - [Running the extraction](#running-the-extraction)

## Entity Recognition

For this example we're going to write rules to extract postage stamp descriptions as found at https://www.mysticstamp.com/.

Here is Python code to create an input string containing the descriptions for several 19th Century U.S. postage stamps.

```python
import inspect

from text_to_relations import RegexString

input = \
"""
# 11A - 1853-55 3¢ George Washington, dull red, type II, imperf

# 17 - 1851 12c Washington imperforate, black

# 12 - 1856 5c Jefferson, red brown, type I, imperforate

# 18 - 1861 1c Franklin, type I, perf 15

# 40 - 1875 1c Franklin, bright blue

# 42 - 1875 5c Jefferson, orange brown

# 62B - 1861 10c Washington, dark green

input = inspect.cleandoc(input)
"""
```

We'll break the first description up into its constituent parts:
- id: *# 11A*
- year_issued: *1853-55*
- value: *3*
- denomination: *cents*
- theme: *George Washington*
- color: *dull red*
- type: *II*
- perforation_info: *imperforate*

Let's pretend that our goal is to write rules to successfully process all the data at the Mystic Stamp website. We hope that writing rules for these examples will give us a good start.

### RegexString

With Text-To-Relations, the go-to tool is RegexString, which is essentially a wrapper around your basic regular expression. The wrapper lets you construct highly useful, working regular expressions with little or no fuss--and requiring from you a minimum amount of understanding the arcane details of regular expressions.

The simplest interface is RegexString's constructor, which with default parameters just takes a list of strings which you want to be considered "synonymous" in some way, that is, as different examples of the same kind of thing.

#### Case-Insensitive Matching

RegexString does not use `re.IGNORECASE`. The recommended approach for case-insensitive matching is to lowercase both sides:

```python
match_strs = ['type', 'kind', 'sort']   # already lowercase
rs = RegexString(match_strs, whole_word=True)

input_text = "We need a Type I or a SORT II widget."
matches = rs.get_match_triples(input_text.lower())
print(matches)
# [('type', 9, 13), ('sort', 22, 26)]
```

Note that the offsets returned refer to positions in the lowercased string, which are identical to positions in the original string.

### Example 1

We'll use the *type* entity to begin our demonstration of RegexString. In the text above you see that there are only two--"type I" and "type II". But let's suppose that, in the complete data on the website:
- First, that sometimes the word *type* is capitalized and sometimes it is all-lowercase.
- Second, that the types run from Roman numeral I through V.

```python
type_markers = ['type', 'Type']
type_rs = RegexString(type_markers, whole_word=True)
print(f"Regular expression for 'type_rs': {type_rs.get_regex_str()}\n")

roman_numerals = ['I', 'II', 'III', 'IV', 'V']
roman_nums_rs = RegexString(roman_numerals, whole_word=True)
print(f"Regular expression for 'roman_nums_rs': {roman_nums_rs.get_regex_str()}")
```

If you ran the code above you would see this as output:

```console
Regular expression for 'type_rs': \b(?:type|Type)\b

Regular expression for 'roman_nums_rs': \b(?:III|II|IV|I|V)\b
```
Both "\btype\b" and "\b(?:III|II|IV|I|V)\b" are valid regular expressions that you could use with the Python `re` regular expression library, for example `re.finditer()` or any other one of the library's functions.

Both regular expressions begin and end with '\b,' which is regex-speak for "whole word only." This is controlled by the `whole_word` parameter, whose default value is False.

The meat of the regex for `roman_nums_rs` consists of the five Roman numerals separated by "|" (meaning OR), which will match on any one of the five if found in a piece of text. Some other things to note here:
- The regular expression sorts the OR'd numerals by length so that, for example, if "II" occurs in the text you will get a single match on the entire string rather than two matches on "I." (Note that this is only an issue when `whole_word` is set to False.)
- The scary looking "?:" at the start of the block tells the regular expression matcher not to perform grouping on the match. If you don't know what this means--don't worry, you don't need to know. For most *natural language* processing tasks (as opposed to some text processing tasks), you don't need grouping. Text-To-Relations employs non-capturing by default so that some of the other functionality that builds on RegexString objects can assume the associated regular expression is non-capturing. (If you must have capturing, create the RegexString with `non_capturing=False` to allow capturing.)

Finally we're ready to run our RegexString objects against the stamp descriptions at top.

```python
type_phrase_rs = RegexString.concat_with_word_distances(
    type_rs, 
    roman_nums_rs, 
    min_nbr_words=0, 
    max_nbr_words=0)
matchStrs = type_phrase_rs.get_match_triples(input)
print("\nType info found in the input:")
print(matchStrs)
```
RegexString.concat_with_word_distances() takes two RegexString objects and creates a new RegexString which will match text satisfying both of the original regular expressions when they are within a certain amount of word distance. In our case we are saying that we don't want to allow any words between them. (Note that this is a static function belonging to the RegexString class rather than to any particular RegexSting object.)

When we run this code we see this output:
```console
Type info found in the input:
[('type II', 48, 55), ('type I', 149, 155), ('type I', 195, 201)]
```

get_match_triples( ) runs a MatchString object's regular expression against user-supplied text input. The "triples" it returns are: (1) the matched string; (2) the matched string's starting offset in the input text; and (3) the matched string's ending offset in the input text.

You see that the `type_phrase_rs` object which we constructed from smaller pieces managed to find all three "type" expressions in the postage stamp input.


### Example 2

Now let's extract the value of the postage stamp, which will give us a chance to demo RegexString's `prepend` parameter. Our description above has six unique values, only one of which uses the old-fashioned cents character, '¢'. These are: 3¢, 12c, 5c, 1c, 1c, 5c, 10c.

```python
cent_symbols = ['c', '¢']
# Use `prepend` to look for one or two digits before the cent symbol.
cent_rs = RegexString(cent_symbols, prepend='\d\d?')
print(f"\nRegular expression for 'cent_rs': {cent_rs.get_regex_str()}")
matchStrs = cent_rs.get_match_triples(input)
print("\nCents info found in the input:")
print(matchStrs)
```

This outputs:
```console
Regular expression for 'cent_rs': \d\d?(?:c|¢)

Cents info found in the input:
[('3¢', 16, 18), ('12c', 77, 80), ('5c', 124, 126), ('1c', 182, 184), ('1c', 224, 226), ('5c', 262, 264), ('10c', 303, 306)]
```

As a side note, Text-to-Relations offers at least one other way of accomplishing the same goal: we could have created two RegexString objects and then concatenated them with the RegexString concat( ) function.

### Example 3

Here's one more "Introduction-to-RegexString" example, this time used to extract the perforation information in our postage stamp descriptions. The specific perforation examples we're targeting are: imperf, imperforate, perf 15.

```python
perforation_markers = ['perf', 'imperforate', 'imperf']
perforations_rs = RegexString(perforation_markers)
matchStrs = perforations_rs.get_match_triples(input)
print("\nPerforation info:")
print(matchStrs)
```

When run, the code above gives us:
```console
Perforation info:
[('imperf', 57, 63), ('imperforate', 92, 103), ('imperforate', 157, 168), ('perf', 203, 207)]
```

But this isn't quite what we want. If perforated, the description includes the perforation size. Let's try again.

```python
imperforated_markers = ['imperforate', 'imperf']
imperf_rs = RegexString(imperforated_markers)
matchStrs = imperf_rs.get_match_triples(input)
print("\nImperforated:")
print(matchStrs)

perforation_markers = ['perf']
perf_rs = RegexString(perforation_markers, append=' \d\d')
matchStrs = perf_rs.get_match_triples(input)
print("\nPerforated sizes:")
print(matchStrs)
```

What this produces is much closer to what we expect:
```console
Imperforated:
[('imperf', 57, 63), ('imperforate', 92, 103), ('imperforate', 157, 168)]

Perforated sizes:
[('perf 15', 203, 210)]
```

### Example 4: Using build_regex_string( )

Now for some new RegexString functionality. First we'll use the function build_regex_string( ) to create a regular expression that matches on one set of list items on one word, then on another set for the next word in the text--this seems right for colors that are preceded by qualifiers like *bright* and *dark*.

Before going further let's have a look at the use of colors in the stamp descriptions--one description doesn't mention a color, one has just "black," and five have a *qualifier + color* description. The specific strings we're targeting are: dull red, black, red brown, bright blue, orange brown, dark green.

Now let's get started.

```python
colors = ['black', 'blue', 'brown', 'green', 'orange', 'red']

colors_rs = RegexString(colors, whole_word=True)
matchStrs = colors_rs.get_match_triples(input)
print("\nColors alone:")
print(matchStrs)

# Create the qualifiers.
# Add colors to the qualifiers, so that we can ID, e.g. 'orange brown'.
color_qualifiers = ['bright', 'dark', 'dull'] + colors

inputList = [color_qualifiers, 0, colors]
color_phrase_rs = RegexString.build_regex_string(inputList)
matchStrs = color_phrase_rs.get_match_triples(input)
print("\nColor qualifiers + colors:")
print(matchStrs)
```

Output:
```console
Colors alone:
[('red', 43, 46), ('black', 105, 110), ('red', 138, 141), ('brown', 142, 147), ('blue', 244, 248), ('orange', 276, 282), ('brown', 283, 288), ('green', 324, 329)]

Color qualifiers + colors:
[('dull red', 38, 46), ('red brown', 138, 147), ('bright blue', 237, 248), ('orange brown', 276, 288), ('dark green', 319, 329)]
```

Oops! We're not getting the colors which aren't preceded by a qualifier. The build_regex_string( ) function may be useful in other circumstances, but it's not the right tool for this particular job. (In truth, I knew this function wouldn't work here before I tried it out, but I wanted to introduce you to the function and I had no other use case for this set of postage stamp descriptions.)

Instead, let's try concat_with_word_distances( ), which we've already used successfully to identify *type + roman numeral*, a context where the first word was not optional.

```python
color_qualifiers_rs = RegexString(color_qualifiers, whole_word=True, optional=True)
color_phrase_rs = RegexString.concat_with_word_distances(
    color_qualifiers_rs, 
    colors_rs, 
    min_nbr_words=0, 
    max_nbr_words=0)
matchStrs = color_phrase_rs.get_match_triples(input)
print("\nOptional color qualifiers + colors found in the input:")
print(matchStrs)
```

Final output:
```console
Optional color qualifiers + colors found in the input:
[('dull red', 38, 46), ('black', 105, 110), ('red brown', 138, 147), ('bright blue', 237, 248), ('orange brown', 276, 288), ('dark green', 319, 329)]
```

### Example 5: Appending More Complicated Regular Expressions

For our final example we're going to extract the Mystic Stamp Company's IDs for the postage stamps in our description. These are: # 11A, # 17, # 12, # 18, # 40, # 42, # 62B.

Our quick first pass uses RegexString with the `append` parameter, which completes the regular expression by matching on an empty space followed by one or more digits.

```python
id_symbols = ['#']

id_rs = RegexString(id_symbols, append='\s\d+')
matchStrs = id_rs.get_match_triples(input)
print("\nStamp IDs:")
print(matchStrs)
```

We see that this  gets the digit part of the IDs, but not the capital letter which follows two of them.

```console
Stamp IDs:
[('# 11', 0, 4), ('# 17', 65, 69), ('# 12', 112, 116), ('# 18', 170, 174), ('# 40', 212, 216), ('# 42', 250, 254), ('# 62', 290, 294)]
```

No problem. With our limited understanding of regular expressions, we know that we can add *(\w)?* to the end of the regular expression in order to match on an optional word character. (A word character excludes digits and punctuation.)
- If we use *\w+* instead of just *\w*, we could match on additional word characters, in case some of the IDs which we haven't seen have these extra characters.
- And from the talk above regarding non-grouping expressions, we have learned that, generally speaking, we should insert *?:* at the start of the optional word character parentheses.

```bash
id_rs = RegexString(id_symbols, append='\s\d+(?:\w+)?')
matchStrs = id_rs.get_match_triples(input)
print("\nStamp IDs with letters found in the input:")
print(matchStrs)
```

```console
Stamp IDs with letters found in the input:
[('# 11A', 0, 5), ('# 17', 65, 69), ('# 12', 112, 116), ('# 18', 170, 174), ('# 40', 212, 216), ('# 42', 250, 254), ('# 62B', 290, 295)]
```

## Relation Extraction

By *relation extraction* we mean the identification of relationships between multiple entities. With the stamp data we have been working with, a natural relation is a `StampDescription` that groups together the stamp's ID, denomination, type numeral, and perforation information. Not every stamp entry contains all four fields — only three of the seven have type information — so only those three will produce a result.

To extract a relation, subclass `ExtractionPhaseABC` and implement `check_annotation_proximity()`. The default `run_phase()` splits the document on blank lines and calls `check_annotation_proximity()` for each entry — no further boilerplate required.

### The extraction phase

Inside `check_annotation_proximity()` you define two things:

**1. Regex patterns** — a dict mapping annotation type names to `RegexString` objects, using the same patterns introduced earlier in this tutorial:

```python
id_rs    = RegexString(['#'], append=r'\s\d+(?:\w+)?')
cent_rs  = RegexString(['c', '¢'], prepend=r'\d\d?')

type_markers_rs  = RegexString(['type', 'Type'], whole_word=True)
roman_nums_rs    = RegexString(['I', 'II', 'III', 'IV', 'V'], whole_word=True)
type_phrase_rs   = RegexString.concat_with_word_distances(
    type_markers_rs, roman_nums_rs, min_nbr_words=0, max_nbr_words=0)

imperf_rs        = RegexString(['imperforate', 'imperf'])
perf_sized_rs    = RegexString(['perf'], append=r'\s\d+')
perf_combined_rs = RegexString.from_regex(
    f'(?:{imperf_rs.get_regex_str()}|{perf_sized_rs.get_regex_str()})')

regex_patterns = {
    'StampID':      id_rs,
    'Denomination': cent_rs,
    'TypePhrase':   type_phrase_rs,
    'Perforation':  perf_combined_rs,
}
```

**2. A proximity chain** — a list of `(start_type, (min_tokens, max_tokens), end_type)` tuples specifying how close together consecutive entity types must appear:

```python
chain = [
    ('StampID',      (0, 4), 'Denomination'),   # e.g. '- 1853-55'
    ('Denomination', (0, 8), 'TypePhrase'),      # e.g. 'George Washington, dull red,'
    ('TypePhrase',   (0, 2), 'Perforation'),     # e.g. ','
]
```

Then call `run_chained_loops()`, which handles everything else — building annotations, constructing the merged representation, running the loop engine, and assembling the result:

```python
return self.run_chained_loops(text, 'StampDescription', regex_patterns, chain)
```

The full class looks like this:

```python
class StampDescriptionPhase(ExtractionPhaseABC):
    def __init__(self, doc_contents: str, verbose: bool = False):
        super().__init__(doc_contents, verbose=verbose)

    def check_annotation_proximity(self, text: str) -> List[Annotation]:
        # ... (regex pattern definitions as above) ...
        regex_patterns = { ... }
        chain = [ ... ]
        return self.run_chained_loops(text, 'StampDescription', regex_patterns, chain)
```

### Running the extraction

```python
phase = StampDescriptionPhase(input_text)
results = phase.run_phase()

print(f'{len(results)} of 7 stamp descriptions extracted:\n')
for ann in results:
    p = ann.properties
    print(f"  stamp_id='{p['StampID']}', denomination='{p['Denomination']}', "
          f"type='{p['TypePhrase']}', perforation_info='{p['Perforation']}'")
```

Output:

```console
3 of 7 stamp descriptions extracted:

  stamp_id='# 11A', denomination='3¢', type='type II', perforation_info='imperf'
  stamp_id='# 12', denomination='5c', type='type I', perforation_info='imperforate'
  stamp_id='# 18', denomination='1c', type='type I', perforation_info='perf 15'
```

Only 3 of 7 stamp descriptions were extracted because the loop chain requires all four fields to be present. The other four stamps either lack type information entirely (stamps #40, #42, #62B) or have perforation information but no type (stamp #17). Handling those cases would require additional phases — one for each alternative pattern — following the same approach shown here.

Note that `ann.properties` keys match the annotation type names defined in `regex_patterns` (`StampID`, `Denomination`, `TypePhrase`, `Perforation`).
