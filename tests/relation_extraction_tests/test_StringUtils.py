import unittest

from text_to_relations.relation_extraction import StringUtils


class TestStringUtils(unittest.TestCase):

    def testRemoveMultipleSpaces(self):
        inputStr = 'Hello, how  are     you ?   '
        self.assertEqual('Hello, how are you ? ', StringUtils.removeMultipleSpaces(inputStr))

    def testIsAllPunc(self):
        actual = StringUtils.isAllPunc('iiii???***6rrrrr')
        self.assertEqual(False, actual)

        actual = StringUtils.isAllPunc('???***6')
        self.assertEqual(False, actual)

        actual = StringUtils.isAllPunc('???***')
        self.assertEqual(True, actual)

        # Unicode tilde.
        actual = StringUtils.isAllPunc(u"\u007E")
        self.assertEqual(True, actual)
        # Unicode multiplication.
        actual = StringUtils.isAllPunc(u"\u00D7")
        self.assertEqual(True, actual)

        # Non-breaking space.
        actual = StringUtils.isAllPunc(u"\u00A0")
        self.assertEqual(False, actual)

        # Reverse line feed control character.
        actual = StringUtils.isAllPunc(u"\u008D")
        self.assertEqual(False, actual)

    def testIsWordChars(self):
        actual = StringUtils.isAllWordChars('iiii6rrrrr')
        self.assertEqual(True, actual)

        actual = StringUtils.isAllWordChars('iiii???***6rrrrr')
        self.assertEqual(False, actual)

        actual = StringUtils.isAllWordChars('???***6')
        self.assertEqual(False, actual)

        actual = StringUtils.isAllWordChars('???***')
        self.assertEqual(False, actual)

        # Unicode tilde.
        actual = StringUtils.isAllWordChars(u"\u007E")
        self.assertEqual(False, actual)
        # Unicode multiplication.
        actual = StringUtils.isAllWordChars(u"\u00D7")
        self.assertEqual(False, actual)

        # Non-breaking space.
        actual = StringUtils.isAllWordChars(u"\u00A0")
        self.assertEqual(False, actual)

        # Reverse line feed control character.
        actual = StringUtils.isAllWordChars(u"\u008D")
        self.assertEqual(False, actual)
