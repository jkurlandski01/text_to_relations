import unittest

from text_to_relations.relation_extraction import SpacyUtils
from text_to_relations.relation_extraction.SpacyUtils import spacyEnglishModel


class TestSpacyUtils(unittest.TestCase):

    def testTokens(self):
        # Note the starting and ending whitespace.
        docContents = " I saw a sad monkey. The monkey's face was miserable--miserable and forlorn. "

        # The SpacyUtils function fixes a Spacy bug by stripping the input string of 
        # beginning and ending whitespace.
        actual = SpacyUtils.tokenize(docContents)

        expected = ['I',
                    'saw',
                    'a',
                    'sad',
                    'monkey',
                    '.',
                    'The',
                    'monkey',
                    "'s",
                    'face',
                    'was',
                    'miserable',
                    '--',
                    'miserable',
                    'and',
                    'forlorn',
                    '.']
        self.assertEqual(expected, actual)

        # A heavy-weight Spacy doc returns almost the same results, but includes
        # the whitespace "token" which the Spacy bug inserts.
        heavyweightDoc = spacyEnglishModel(docContents)

        actual = [str(x) for x in heavyweightDoc]

        expected = [' '] + expected
        self.assertEqual(expected, actual)


    def testTokensWithWhitespace(self):
        # Same as above, but adding whitespacew throughout the "doc".
        docContents = " I saw a sad monkey. \n "
        docContents += "The \n\nmonkey's face       was miserable--miserable and\nforlorn. "

        # The SpacyUtils function fixes a Spacy bug by stripping the input string of
        # beginning and ending whitespace.
        actual = SpacyUtils.tokenize(docContents)

        expected = ['I',
                    'saw',
                    'a',
                    'sad',
                    'monkey',
                    '.',
                    'The',
                    'monkey',
                    "'s",
                    'face',
                    'was',
                    'miserable',
                    '--',
                    'miserable',
                    'and',
                    'forlorn',
                    '.']
        self.assertEqual(expected, actual)

        # A heavy-weight Spacy doc returns almost the same results, but includes
        # the whitespace "token" which the Spacy bug inserts.
        heavyweightDoc = spacyEnglishModel(docContents)

        actual = [str(x) for x in heavyweightDoc]

        expected = [' ',
                    'I',
                    'saw',
                    'a',
                    'sad',
                    'monkey',
                    '.',
                    '\n ',
                    'The',
                    '\n\n',
                    'monkey',
                    "'s",
                    'face',
                    '      ',
                    'was',
                    'miserable',
                    '--',
                    'miserable',
                    'and',
                    '\n',
                    'forlorn',
                    '.']
        self.assertEqual(expected, actual)
