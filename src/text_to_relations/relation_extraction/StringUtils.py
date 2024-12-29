import re

import unicodedata

regexMultipleSpaces = re.compile(r' +', re.IGNORECASE)

def removeMultipleSpaces(inStr):
    """ Remove multiple consecutive spaces from a string. """
    return regexMultipleSpaces.sub(' ', inStr)


def isAllPunc(inputString):
    """
    Is the given string all punctuation?
    :param inputString:
    :return: boolean
    """
    bAllPunc = True
    for char in inputString:
        category = unicodedata.category(char)
        if category.startswith('P') or category == 'Sm':
            continue
        bAllPunc = False
        break

    return bAllPunc


def isAllWordChars(inputStr):
    """
    Does the given string consist only of word characters?
    :return:
    """
    regexWordChar = re.compile(r'^\w+$')

    if re.match(regexWordChar, inputStr):
        return True
    return False
