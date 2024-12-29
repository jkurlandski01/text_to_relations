import unittest

from text_to_relations.relation_extraction.SentenceAnn import SentenceAnn


class TestSentenceAnn(unittest.TestCase):

    def testTextToSentenceAnns1(self):
        textIn = "She loves me. "
        textIn += "She loves me not. "
        textIn += "She loves me. "
        textIn += "She loves me not."

        actual = SentenceAnn.text_to_SentenceAnns(textIn)
        expected = [SentenceAnn("She loves me.", 0, 13),
                    SentenceAnn("She loves me not.", 14, 31),
                    SentenceAnn("She loves me.", 32, 45),
                    SentenceAnn("She loves me not.", 46, 63)]
        self.assertEqual(expected, actual)

    def testTextToSentenceAnns2(self):
        textIn1 = "MyVulture today announced the pricing of its follow-on public offering of 5,600,000 "
        textIn1 += "shares of its Class A common stock at a price of $35 per share, for a total "
        textIn1 += "offering size of $196,000,000."
        textIn2 = "Of these shares, 3,292,580 shares are being "
        textIn2 += "offered by AltWay and 2,307,420 shares are being offered by certain selling stockholders"

        textIn = textIn1 + " " + textIn2

        actual = SentenceAnn.text_to_SentenceAnns(textIn)
        expected = [SentenceAnn(textIn1, 0, 190),
                    SentenceAnn(textIn2, 191, 323)]
        self.assertEqual(expected, actual)
