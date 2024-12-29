import re
import unittest

from text_to_relations.relation_extraction.TokenAnn import TokenAnn


class TestTokenAnn(unittest.TestCase):
    
    def testInit(self):
        token = TokenAnn(0, 3, 'whoo')
        self.assertEqual('whoo', token.normalizedContents)
        self.assertEqual('word', token.properties['kind'])

        token = TokenAnn(0, 3, '?')
        self.assertEqual('?', token.normalizedContents)
        self.assertEqual('punc', token.properties['kind'])

        token = TokenAnn(0, 3, "'a")
        self.assertEqual("'a", token.normalizedContents)
        self.assertEqual('other', token.properties['kind'])

        # Test exceptions.
        token = TokenAnn(0, 3, "'s")
        self.assertEqual("'s", token.normalizedContents)
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
        inputStr = "<'Token'(start='0', end='125', normalizedContents='zzz', kind='word')>"
        inputStr += "<'WarrantPurchase'(start='126', end='144', normalizedContents='Option to Purchase')>"
        inputStr += "<'Token'(start='145', end='148', normalizedContents='zzz', kind='word')>"
        inputStr += "<'Token'(start='200', end='210', normalizedContents='zzz', kind='word')>"
        inputStr += "<'Token'(start='333', end='334', normalizedContents='zzz', kind='word')>"
        inputStr += "<'ShareQuantity'(start='569', end='578', normalizedContents='9,947,500')>"
        inputStr += "<'Token'(start='579', end='582', normalizedContents='zzz', kind='word')>"

        # Literal match on 'word' property.
        testRegex = r"<'WarrantPurchase[^>]*>(?:<'Token'[^>]*kind='word'[^>]*>){0,3}<'ShareQuantity[^>]*>"

        match_strs = re.findall(testRegex, inputStr)
        expected = ["<'WarrantPurchase'(start='126', end='144', normalizedContents='Option to Purchase')>"
                    "<'Token'(start='145', end='148', normalizedContents='zzz', kind='word')>"
                    "<'Token'(start='200', end='210', normalizedContents='zzz', kind='word')>"
                    "<'Token'(start='333', end='334', normalizedContents='zzz', kind='word')>"
                    "<'ShareQuantity'(start='569', end='578', normalizedContents='9,947,500')>"]
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
        inputStr = "<'Token'(start='0', end='125', normalizedContents='zzz', kind='word')>"
        inputStr += "<'WarrantPurchase'(start='126', end='144', normalizedContents='Option to Purchase')>"
        inputStr += "<'Token'(start='145', end='148', normalizedContents='zzz', kind='word')>"
        inputStr += "<'Token'(start='200', end='210', normalizedContents='zzz', kind='word')>"
        inputStr += "<'Token'(start='333', end='334', normalizedContents='zzz', kind='word')>"
        inputStr += "<'ShareQuantity'(start='569', end='578', normalizedContents='9,947,500')>"
        inputStr += "<'Token'(start='579', end='582', normalizedContents='zzz', kind='word')>"

        expected = ["<'WarrantPurchase'(start='126', end='144', normalizedContents='Option to Purchase')>"
                    "<'Token'(start='145', end='148', normalizedContents='zzz', kind='word')>"
                    "<'Token'(start='200', end='210', normalizedContents='zzz', kind='word')>"
                    "<'Token'(start='333', end='334', normalizedContents='zzz', kind='word')>"
                    "<'ShareQuantity'(start='569', end='578', normalizedContents='9,947,500')>"]

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
        inputStr = "<'Token'(start='0', end='125', normalizedContents='zzz', kind='word')>"
        inputStr += "<'WarrantPurchase'(start='126', end='144', normalizedContents='Option to Purchase')>"
        inputStr += "<'Token'(start='145', end='148', normalizedContents='zzz', kind='word')>"
        inputStr += "<'Token'(start='200', end='210', normalizedContents='zzz', kind='punc')>"
        inputStr += "<'Token'(start='333', end='334', normalizedContents='zzz', kind='word')>"
        inputStr += "<'ShareQuantity'(start='569', end='578', normalizedContents='9,947,500')>"
        inputStr += "<'Token'(start='579', end='582', normalizedContents='zzz', kind='word')>"

        testRegex = TokenAnn.build_annotation_distance_regex("WarrantPurchase", (0, 10), "word", "ShareQuantity")

        match_strs = re.findall(testRegex, inputStr)
        expected = []
        self.assertEqual(expected, match_strs)
