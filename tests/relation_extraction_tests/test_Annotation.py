import unittest

from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.SentenceAnn import SentenceAnn
from text_to_relations.relation_extraction.TokenAnn import TokenAnn


class TestAnnotation(unittest.TestCase):

    def testInvalidOffsets(self):
        with self.assertRaises(ValueError):
            Annotation('ShareQuantity', '10,000', 0, -6)

        with self.assertRaises(ValueError):
            Annotation('ShareQuantity', 'xxx', -1, 5)

        with self.assertRaises(ValueError):
            Annotation('ShareQuantity', 'xxx', 1, -5)

    def testStringToAnnotation(self):
        annStr = "<'ShareQuantity'(normalizedContents='15,000,000'start='0', end='10')>"
        actual = Annotation.str_to_Annotation(annStr)

        expected = Annotation('ShareQuantity', '15,000,000', 0, 10)
        self.assertEqual(expected, actual)


    def testStringToAnnotationDifferent(self):
        annStr = "<'ShareQuantity'(normalizedContents='15,000,000', start='0', end='10')>"
        actual = Annotation.str_to_Annotation(annStr)

        expected = Annotation('zShareQuantity', '15,000,000', 0, 10)
        self.assertNotEqual(expected, actual)

        expected = Annotation('ShareQuantity', '15,000,000', 10, 10)
        self.assertNotEqual(expected, actual)

        expected = Annotation('ShareQuantity', '15,000,000', 0, 100)
        self.assertNotEqual(expected, actual)

        expected = Annotation('ShareQuantity', '115,000,000', 0, 10)
        self.assertNotEqual(expected, actual)


    def testAnnotationCreation(self):
        ann = Annotation('FreakyThing', 'freak out!', 0, 16)
        expected = "<'FreakyThing'(normalizedContents='freak out!', start='0', end='16')>"
        self.assertEqual(expected, str(ann))

        features = {'kind': 'exclamation'}
        ann = Annotation('FreakyThing', 'freak out!', 0, 16, features)
        expected = "<'FreakyThing'(normalizedContents='freak out!', start='0', end='16', kind='exclamation')>"
        self.assertEqual(expected, str(ann))

        features = {'kind': 'exclamation', 'type': 'Thing'}
        ann = Annotation('FreakyThing', 'freak out!', 0, 16, features)
        expected = "<'FreakyThing'(normalizedContents='freak out!', start='0', end='16', " \
                   "kind='exclamation', type='Thing')>"
        self.assertEqual(expected, str(ann))


    def testEncloses(self):
        # Test Annotation.encloses() by creating sentence and token annotations on a doc.
        # Also tests Annotation.get_enclosed()
        textIn1 = "MyVulture today announced the pricing of an underwritten registered public offering of "
        textIn1 += "1,347,232 shares of its common stock at a public offering price of $305.00 per share."
        textIn2 = "Â In the offering, DadRight will issue and sell 983,607 shares and existing stockholders "
        textIn2 += "of the company, including certain of its executive officers and directors and affiliates "
        textIn2 += "thereof will sell 363,625 shares"

        textIn = textIn1 + " " + textIn2

        # Get and verify the sentence annotations.
        sentenceAnns = SentenceAnn.text_to_SentenceAnns(textIn)
        # The sentence splitter splits the text into three, not two.
        sentenceAnn1 = SentenceAnn(textIn1, 0, 172)
        sentenceAnn2 = SentenceAnn('Â', 173, 174)
        sentenceAnn3 = SentenceAnn(textIn2[2:], 175, 383)
        expected = [sentenceAnn1,
                    sentenceAnn2,
                    sentenceAnn3]
        self.assertEqual(expected, sentenceAnns)
        
        # Get and verify the token annotations.
        tokenAnns = TokenAnn.text_to_token_anns(textIn)
        self.assertEqual(63, len(tokenAnns))
        
        myVultureAnn = TokenAnn(0, 9, 'MyVulture')
        sharesAnn = TokenAnn(377, 383, 'shares')
        self.assertEqual(myVultureAnn, tokenAnns[0])
        self.assertEqual(sharesAnn, tokenAnns[62])

        # Finally, test encloses().
        self.assertTrue(Annotation.encloses(sentenceAnn1, myVultureAnn))
        self.assertFalse(Annotation.encloses(sentenceAnn2, myVultureAnn))
        self.assertFalse(Annotation.encloses(sentenceAnn3, myVultureAnn))

        self.assertFalse(Annotation.encloses(sentenceAnn1, sharesAnn))
        self.assertFalse(Annotation.encloses(sentenceAnn2, sharesAnn))
        self.assertTrue(Annotation.encloses(sentenceAnn3, sharesAnn))
        
        # Create a new annotation that spans from sentence1 across sentence2
        # to sentence3.
        crossesSentenceBoundariesAnn = Annotation('MyAnn', "someNonsenseText", 170, 180)

        self.assertFalse(Annotation.encloses(sentenceAnn1, crossesSentenceBoundariesAnn))
        self.assertFalse(Annotation.encloses(sentenceAnn2, crossesSentenceBoundariesAnn))
        self.assertFalse(Annotation.encloses(sentenceAnn3, crossesSentenceBoundariesAnn))

        # Create an annotation that covers the entire document.
        entireDocAnn = Annotation('MyBigAnn', "someNonsenseText", 0, 383)

        self.assertFalse(Annotation.encloses(sentenceAnn1, entireDocAnn))
        self.assertFalse(Annotation.encloses(sentenceAnn2, entireDocAnn))
        self.assertFalse(Annotation.encloses(sentenceAnn3, entireDocAnn))

        self.assertTrue(Annotation.encloses(entireDocAnn, sentenceAnn1))
        self.assertTrue(Annotation.encloses(entireDocAnn, sentenceAnn2))
        self.assertTrue(Annotation.encloses(entireDocAnn, sentenceAnn3))
        
        # Use the same input data to test get_enclosed().
        actual = Annotation.get_enclosed(entireDocAnn,
                                        [myVultureAnn, sharesAnn, crossesSentenceBoundariesAnn, entireDocAnn])
        expected = [myVultureAnn, sharesAnn, crossesSentenceBoundariesAnn, entireDocAnn]
        self.assertEqual(expected, actual)

        actual = Annotation.get_enclosed(sentenceAnn1,
                                        [myVultureAnn, sharesAnn, crossesSentenceBoundariesAnn, entireDocAnn])
        expected = [myVultureAnn]
        self.assertEqual(expected, actual)

        actual = Annotation.get_enclosed(sentenceAnn2,
                                        [myVultureAnn, sharesAnn, crossesSentenceBoundariesAnn, entireDocAnn])
        expected = []
        self.assertEqual(expected, actual)
