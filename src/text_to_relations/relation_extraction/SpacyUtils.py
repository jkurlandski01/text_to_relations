"""
Utility functions built on spaCy.
"""

import re
from typing import List

import spacy

# Load the spaCy English language model one time for the entire application.
# Either of these models is acceptable:
try:
    spacyEnglishModel = spacy.load('en_core_web_lg')
    lightSpacyEnglishModel = spacy.load('en_core_web_lg',
                                    disable=["tagger", "parser", "ner", "textcat", "lemmatizer"])
except IOError:
    spacyEnglishModel = spacy.load('en_core_web_trf')
    # Does not work under Python 3.9:
    lightSpacyEnglishModel = spacy.load('en_core_web_trf',
                                    disable=["tagger", "parser", "ner", "textcat", "lemmatizer"])


def tokenize(input_str: str) -> List[str]:
    """
    Use the lightweight English model to tokenize a piece of text.
    Fixes a couple of bugs in the default Spacy tokenizer.
    :param input_str:
    :return: a list of tokens
    """

    input_str = input_str.strip()

    # Bug 1: Hyphen issue: if the input consists solely of '- + word' or 'word + -',
    # Spacy fails to separate the hyphen from the word.
    if input_str.startswith('-'):
        input_str = re.sub('-(\\w)', '- \\1', input_str)
    if input_str.endswith('-'):
        input_str = re.sub('(\\w)-', '\\1 -', input_str)

    # Tokenize with a light-weight Spacy doc.
    lightweight_doc = lightSpacyEnglishModel(input_str)

    # Bug 2: Spacy outputs strings of whitespace as tokens. Strip these out here.)
    return [str(x) for x in lightweight_doc if str(x).strip() != '']


if __name__ == '__main__':
    pass
