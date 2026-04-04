import re

import unicodedata

regex_multiple_spaces = re.compile(r' +', re.IGNORECASE)

def remove_multiple_spaces(in_str: str) -> str:
    """ Remove multiple consecutive spaces from a string. """
    return regex_multiple_spaces.sub(' ', in_str)


def is_all_punc(input_string: str) -> bool:
    """
    Is the given string all punctuation?
    :param input_string:
    :return: boolean
    """
    all_punc = True
    for char in input_string:
        category = unicodedata.category(char)
        if category.startswith('P') or category == 'Sm':
            continue
        all_punc = False
        break

    return all_punc


def is_all_word_chars(input_str: str) -> bool:
    """
    Does the given string consist only of word characters?
    :return:
    """
    regex_word_char = re.compile(r'^\w+$')

    if re.match(regex_word_char, input_str):
        return True
    return False
