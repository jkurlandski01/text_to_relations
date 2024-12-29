"""
Utility functions built on spaCy.
"""

import spacy
import re

"""
Load the spaCy English language model one time for the entire application.
"""
spacyEnglishModel = spacy.load('en_core_web_lg')
lightSpacyEnglishModel = spacy.load('en_core_web_lg', 
                                    disable=["tagger", "parser", "ner", "textcat", "lemmatizer"])

def tokenize(inputStr):
    """
    Use the lightweight English model to tokenize a piece of text.
    Fixes a couple of bugs in the default Spacy tokenizer.
    :param inputStr: 
    :return: a list of tokens
    """
    
    inputStr = inputStr.strip()

    # Bug 1: Hyphen issue: if the input consists solely of '- + word' or 'word + -',
    # Spacy fails to separate the hyphen from the word.
    if inputStr.startswith('-'):
        inputStr = re.sub('-(\\w)', '- \\1', inputStr)
    if inputStr.endswith('-'):
        inputStr = re.sub('(\\w)-', '\\1 -', inputStr)

    # Tokenize with a light-weight Spacy doc.
    lightweightDoc = lightSpacyEnglishModel(inputStr)

    # Bug 2: Spacy outputs strings of whitespace as tokens. Strip these out here.)
    return [str(x) for x in lightweightDoc if str(x).strip() != '']


if __name__ == '__main__':
    pass
