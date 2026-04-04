import unittest

from text_to_relations.relation_extraction import StringUtils


class TestStringUtils(unittest.TestCase):

    def testRemoveMultipleSpaces(self):
        inputStr = 'Hello, how  are     you ?   '
        self.assertEqual('Hello, how are you ? ', StringUtils.remove_multiple_spaces(inputStr))

    def testIsAllPunc(self):
        actual = StringUtils.is_all_punc('iiii???***6rrrrr')
        self.assertEqual(False, actual)

        actual = StringUtils.is_all_punc('???***6')
        self.assertEqual(False, actual)

        actual = StringUtils.is_all_punc('???***')
        self.assertEqual(True, actual)

        # Unicode tilde.
        actual = StringUtils.is_all_punc(u"\u007E")
        self.assertEqual(True, actual)
        # Unicode multiplication.
        actual = StringUtils.is_all_punc(u"\u00D7")
        self.assertEqual(True, actual)

        # Non-breaking space.
        actual = StringUtils.is_all_punc(u"\u00A0")
        self.assertEqual(False, actual)

        # Reverse line feed control character.
        actual = StringUtils.is_all_punc(u"\u008D")
        self.assertEqual(False, actual)

    def testIsWordChars(self):
        actual = StringUtils.is_all_word_chars('iiii6rrrrr')
        self.assertEqual(True, actual)

        actual = StringUtils.is_all_word_chars('iiii???***6rrrrr')
        self.assertEqual(False, actual)

        actual = StringUtils.is_all_word_chars('???***6')
        self.assertEqual(False, actual)

        actual = StringUtils.is_all_word_chars('???***')
        self.assertEqual(False, actual)

        # Unicode tilde.
        actual = StringUtils.is_all_word_chars(u"\u007E")
        self.assertEqual(False, actual)
        # Unicode multiplication.
        actual = StringUtils.is_all_word_chars(u"\u00D7")
        self.assertEqual(False, actual)

        # Non-breaking space.
        actual = StringUtils.is_all_word_chars(u"\u00A0")
        self.assertEqual(False, actual)

        # Reverse line feed control character.
        actual = StringUtils.is_all_word_chars(u"\u008D")
        self.assertEqual(False, actual)
