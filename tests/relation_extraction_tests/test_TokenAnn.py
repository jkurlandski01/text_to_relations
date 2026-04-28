import re
import unittest
import inspect

from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.ExtractionPhaseABC import ChainLink


class TestTokenAnn(unittest.TestCase):

    def testInit(self):
        token = TokenAnn(0, 3, 'whoo')
        self.assertEqual('whoo', token.text)
        self.assertEqual('word', token.properties['kind'])

        token = TokenAnn(0, 3, '?')
        self.assertEqual('?', token.text)
        self.assertEqual('punc', token.properties['kind'])

        token = TokenAnn(0, 3, "'a")
        self.assertEqual("'a", token.text)
        self.assertEqual('other', token.properties['kind'])

        # Test exceptions.
        token = TokenAnn(0, 3, "'s")
        self.assertEqual("'s", token.text)
        self.assertEqual('word', token.properties['kind'])

    def testEquals(self):
        token1 = TokenAnn(0, 3, 'whoo')
        token2 = TokenAnn(0, 3, 'whood')
        self.assertNotEqual(token1, token2)

        token1 = TokenAnn(0, 3, 'whoo')
        token2 = TokenAnn(0, 3, 'whoo')
        self.assertEqual(token1, token2)

        # Test properties equivalence test by artificially playing with the map.
        token1 = TokenAnn(0, 3, 'whoo')
        token2 = TokenAnn(0, 3, 'whoo')
        token2.properties['test'] = 'testing'
        self.assertNotEqual(token1, token2)

        token1 = TokenAnn(0, 3, 'whoo')
        token2 = TokenAnn(0, 3, 'whoo')
        token2.properties['kind'] = 'punc'
        self.assertNotEqual(token1, token2)

    def testAnnotationDistance(self):
        # Test demonstrates how to do token distance matching with regular expressions.
        # Note that there is a helper method in Token to do this for you--build_annotation_distance_regex().

        # 3 words between annotations.
        inputStr = "<'Token'(start='0', end='125', text='zzz', kind='word')>"
        inputStr += "<'WarrantPurchase'(start='126', end='144', text='Option to Purchase')>"
        inputStr += "<'Token'(start='145', end='148', text='zzz', kind='word')>"
        inputStr += "<'Token'(start='200', end='210', text='zzz', kind='word')>"
        inputStr += "<'Token'(start='333', end='334', text='zzz', kind='word')>"
        inputStr += "<'ShareQuantity'(start='569', end='578', text='9,947,500')>"
        inputStr += "<'Token'(start='579', end='582', text='zzz', kind='word')>"

        # Literal match on 'word' property.
        testRegex = r"<'WarrantPurchase[^>]*>(?:<'Token'[^>]*kind='word'[^>]*>){0,3}<'ShareQuantity[^>]*>"

        match_strs = re.findall(testRegex, inputStr)
        expected = ["<'WarrantPurchase'(start='126', end='144', text='Option to Purchase')>"
                    "<'Token'(start='145', end='148', text='zzz', kind='word')>"
                    "<'Token'(start='200', end='210', text='zzz', kind='word')>"
                    "<'Token'(start='333', end='334', text='zzz', kind='word')>"
                    "<'ShareQuantity'(start='569', end='578', text='9,947,500')>"]
        self.assertEqual(expected, match_strs)

        # Match on any kind. Expected output is the same as above.
        testRegex = r"<'WarrantPurchase[^>]*>(?:<'Token[^>]*>){0,3}<'ShareQuantity[^>]*>"

        match_strs = re.findall(testRegex, inputStr)
        self.assertEqual(expected, match_strs)

        # Now run the same tests, requiring the match occur within 2 words instead of 3.
        # This means that no match will occur.
        # Literal match on 'word' property.
        testRegex = r"<'WarrantPurchase[^>]*>(?:<'Token'[^>]*kind='word'[^>]*>){0,2}<'ShareQuantity[^>]*>"

        match_strs = re.findall(testRegex, inputStr)
        expected = []
        self.assertEqual(expected, match_strs)

        # Match on any kind. Expected output is the same as above.
        testRegex = r"<'WarrantPurchase[^>]*>(?:<'Token[^>]*>){0,2}<'ShareQuantity[^>]*>"

        match_strs = re.findall(testRegex, inputStr)
        self.assertEqual(expected, match_strs)

    def testBuildAnnotationDistanceRegex(self):
        # 3 words between annotations.
        inputStr = "<'Token'(start='0', end='125', text='zzz', kind='word')>"
        inputStr += "<'WarrantPurchase'(start='126', end='144', text='Option to Purchase')>"
        inputStr += "<'Token'(start='145', end='148', text='zzz', kind='word')>"
        inputStr += "<'Token'(start='200', end='210', text='zzz', kind='word')>"
        inputStr += "<'Token'(start='333', end='334', text='zzz', kind='word')>"
        inputStr += "<'ShareQuantity'(start='569', end='578', text='9,947,500')>"
        inputStr += "<'Token'(start='579', end='582', text='zzz', kind='word')>"

        expected = ["<'WarrantPurchase'(start='126', end='144', text='Option to Purchase')>"
                    "<'Token'(start='145', end='148', text='zzz', kind='word')>"
                    "<'Token'(start='200', end='210', text='zzz', kind='word')>"
                    "<'Token'(start='333', end='334', text='zzz', kind='word')>"
                    "<'ShareQuantity'(start='569', end='578', text='9,947,500')>"]

        # Use build_annotation_distance_regex() to match any Token.
        testRegex = TokenAnn.build_annotation_distance_regex("WarrantPurchase", (0, 3), None, "ShareQuantity")

        expectedRegex = r"<'WarrantPurchase[^>]*>(?:<'Token[^>]*>){0,3}<'ShareQuantity[^>]*>"
        self.assertEqual(expectedRegex, testRegex)

        match_strs = re.findall(testRegex, inputStr)
        self.assertEqual(expected, match_strs)

        # Use strToAnnDistanceRegex() to match on kind.
        testRegex = TokenAnn.build_annotation_distance_regex("WarrantPurchase", (0, 3), "word", "ShareQuantity")

        expectedRegex = r"<'WarrantPurchase[^>]*>(?:<'Token'[^>]*kind='word'[^>]*>){0,3}<'ShareQuantity[^>]*>"
        self.assertEqual(expectedRegex, testRegex)

        match_strs = re.findall(testRegex, inputStr)
        self.assertEqual(expected, match_strs)

        # Verify that we fail to match on the wrong kind of token.

        # 1 word token, 1 punc token, 1 word token.
        inputStr = "<'Token'(start='0', end='125', text='zzz', kind='word')>"
        inputStr += "<'WarrantPurchase'(start='126', end='144', text='Option to Purchase')>"
        inputStr += "<'Token'(start='145', end='148', text='zzz', kind='word')>"
        inputStr += "<'Token'(start='200', end='210', text='zzz', kind='punc')>"
        inputStr += "<'Token'(start='333', end='334', text='zzz', kind='word')>"
        inputStr += "<'ShareQuantity'(start='569', end='578', text='9,947,500')>"
        inputStr += "<'Token'(start='579', end='582', text='zzz', kind='word')>"

        testRegex = TokenAnn.build_annotation_distance_regex("WarrantPurchase", (0, 10), "word", "ShareQuantity")

        match_strs = re.findall(testRegex, inputStr)
        expected = []
        self.assertEqual(expected, match_strs)

    def testConsecutiveIdenticalAnnotations(self):
        # FIXME: working here
        # 3 words between annotations.
        inputStr = "<'Token'(start='0', end='125', text='zzz', kind='word')>"
        inputStr += (
            "<'WarrantPurchase'(start='126', end='144', text='Option to Purchase')>"
        )
        inputStr += (
            "<'WarrantPurchase'(start='145', end='163', text='Option to Purchase')>"
        )
        inputStr += "<'Token'(start='164', end='182', text='zzz', kind='word')>"
        inputStr += "<'Token'(start='183', end='201', text='zzz', kind='word')>"
        inputStr += "<'ShareQuantity'(start='569', end='578', text='9,947,500')>"
        inputStr += "<'Token'(start='579', end='582', text='zzz', kind='word')>"

        expected = [
            "<'WarrantPurchase'(start='126', end='144', text='Option to Purchase')>"
            "<'WarrantPurchase'(start='145', end='163', text='Option to Purchase')>"
            "<'Token'(start='164', end='182', text='zzz', kind='word')>"
            "<'Token'(start='183', end='201', text='zzz', kind='word')>"
            "<'ShareQuantity'(start='569', end='578', text='9,947,500')>"
        ]

        # Use build_annotation_distance_regex() to match any Token.
        testRegex = TokenAnn.build_annotation_distance_regex(
            "WarrantPurchase", (0, 3), None, "ShareQuantity"
        )

        expectedRegex = (
            r"<'WarrantPurchase[^>]*>(?:<'Token[^>]*>){0,3}<'ShareQuantity[^>]*>"
        )
        self.assertEqual(expectedRegex, testRegex)

        match_strs = re.findall(testRegex, inputStr)
        print(f"{match_strs=}")
        self.assertEqual(expected, match_strs)

    def testConsecutiveIdenticalAnnotations2(self):
        # FIXME: working here

        # inputStr = "<'UNIT_OF_MEASUREMENT'(text='ft-lb', start='214', end='219')><'UNIT_OF_MEASUREMENT'(text='Foot', start='220', end='224')><'Token'(text='-', start='224', end='225', kind='punc')><'Token'(text='pounds', start='225', end='231', kind='word')><'Token'(text='(', start='232', end='233', kind='punc')><'Token'(text='Torque', start='233', end='239', kind='word')><'Token'(text=')', start='239', end='240', kind='punc')><'Token'(text='to', start='241', end='243', kind='word')><'AtMost'(text='upper limit', start='244', end='255')><'Token'(text='of', start='256', end='258', kind='word')><'CARDINAL'(text='92', start='259', end='261')><'UNIT_OF_MEASUREMENT'(text='ft-lb', start='262', end='267')><'UNIT_OF_MEASUREMENT'(text='Foot', start='268', end='272')><'Token'(text='-', start='272', end='273', kind='punc')><'Token'(text='pounds', start='273', end='279', kind='word')><'Token'(text='(', start='280', end='281', kind='punc')><'Token'(text='Torque', start='281', end='287', kind='word')><'Token'(text=')', start='287', end='288', kind='punc')><'Token'(text='.', start='288', end='289', kind='punc')>"
        inputStr = """
            <'UNIT_OF_MEASUREMENT'(text='ft-lb', start='214', end='219')>
            <'UNIT_OF_MEASUREMENT'(text='Foot', start='220', end='224')>
            <'Token'(text='-', start='224', end='225', kind='punc')>
            <'Token'(text='pounds', start='225', end='231', kind='word')>
            <'Token'(text='(', start='232', end='233', kind='punc')>
            <'Token'(text=')', start='239', end='240', kind='punc')>
            <'Token'(text='to', start='241', end='243', kind='word')>
            <'AtMost'(text='upper limit', start='244', end='255')>
            <'Token'(text='of', start='256', end='258', kind='word')>
        """

        # Remove whitespace at the start of each line.
        inputStr = inspect.cleandoc(inputStr)
        # Replace consecutive whitespace with a single space char.
        inputStr = " ".join(inputStr.split())

        expected = [
            "<'UNIT_OF_MEASUREMENT'(text='ft-lb', start='214', end='219')>"
            "<'UNIT_OF_MEASUREMENT'(text='Foot', start='220', end='224')>"
            "<'Token'(text='-', start='224', end='225', kind='punc')>"
            "<'Token'(text=')', start='239', end='240', kind='punc')>"
            "<'Token'(text='to', start='241', end='243', kind='word')>"
            "<'AtMost'(text='upper limit', start='244', end='255')>"
        ]

        # Use build_annotation_distance_regex() to match any Token.
        testRegex = TokenAnn.build_annotation_distance_regex(
            "UNIT_OF_MEASUREMENT", (0, 10), None, "AtMost"
        )

        expectedRegex = (
            # FIXME: doesn't work: r"<'UNIT_OF_MEASUREMENT[^>]*>(?:<'[^>]+>){0,10}<'AtMost[^>]*>"
            r"<'UNIT_OF_MEASUREMENT[^>]*>(?:<'Token[^>]*>){0,10}<'AtMost[^>]*>"
        )
        self.assertEqual(expectedRegex, testRegex)

        match_strs = re.findall(testRegex, inputStr)
        print(f"{match_strs=}")
        self.assertEqual(expected, match_strs)

