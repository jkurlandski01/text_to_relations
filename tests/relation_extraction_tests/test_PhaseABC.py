import unittest

from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink


class TestPhaseABC(unittest.TestCase):

    def testValidSubclass(self):

        class PhaseTest(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()
                self.relation_name = 'Test'
                self.regex_patterns = {}
                self.chain = []

            def find_match(self, text):
                return ['Hi!']

        phase = PhaseTest()
        actual = phase.find_match('blahBlahBlah')

        self.assertEqual(['Hi!'], actual)

    def testMissingRelationName(self):
        class PhaseTest(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()
                self.regex_patterns = {}
                self.chain = []

        with self.assertRaises(ValueError):
            PhaseTest()

    def testMissingRegexPatterns(self):
        class PhaseTest(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()
                self.relation_name = 'Test'
                self.chain = []

        with self.assertRaises(ValueError):
            PhaseTest()

    def testMissingChain(self):
        class PhaseTest(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()
                self.relation_name = 'Test'
                self.regex_patterns = {}

        with self.assertRaises(ValueError):
            PhaseTest()

    def testChainLinkInvalidDistance(self):
        # min_distance > max_distance must raise ValueError at ChainLink construction.
        with self.assertRaises(ValueError):
            ChainLink(start_type='Number', start_property='number',
                      min_distance=3, max_distance=0,
                      end_type='Unit', end_property='unit')

    def testChainConsecutiveMismatch(self):
        # A chain where link[1].start does not match link[0].end must raise ValueError.
        class PhaseTest(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()
                self.relation_name = 'Test'
                self.regex_patterns = {}
                self.chain = [
                    ChainLink(start_type='A', start_property='a',
                              min_distance=0, max_distance=2,
                              end_type='B', end_property='b'),
                    ChainLink(start_type='X', start_property='x',
                              min_distance=0, max_distance=2,
                              end_type='C', end_property='c'),  # should be ('B', 'b', ...)
                ]

        with self.assertRaises(ValueError):
            PhaseTest()

    def testChainPropertyNameCollision(self):
        # Reusing a property name at a non-adjacent slot must raise ValueError.
        class PhaseTest(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()
                self.relation_name = 'Test'
                self.regex_patterns = {}
                self.chain = [
                    ChainLink(start_type='A', start_property='a',
                              min_distance=0, max_distance=2,
                              end_type='B', end_property='b'),
                    ChainLink(start_type='B', start_property='b',
                              min_distance=0, max_distance=2,
                              end_type='C', end_property='a'),  # 'a' already used for slot 0
                ]

        with self.assertRaises(ValueError):
            PhaseTest()

    def testBuildMergedInput1(self):
        # All assertions expect the same output, except for sometimes the annotation offsets.

        self.maxDiff = None

        expected = "<'Token'(text='SafestWay', start='0', end='9', kind='word')>"
        expected += "<'Token'(text=',', start='9', end='10', kind='punc')>"
        expected += "<'Token'(text='Inc.', start='11', end='15', kind='other')>"
        expected += "<'Token'(text='(', start='16', end='17', kind='punc')>"
        expected += "<'Token'(text='NASDAQ', start='17', end='23', kind='word')>"
        expected += "<'Token'(text=':', start='23', end='24', kind='punc')>"
        expected += "<'Token'(text='Â', start='24', end='25', kind='word')>"
        expected += "<'Token'(text='SFSY', start='26', end='30', kind='word')>"
        expected += "<'Token'(text=')', start='30', end='31', kind='punc')>"
        expected += "<'Token'(text=',', start='31', end='32', kind='punc')>"
        expected += "<'Token'(text='a', start='33', end='34', kind='word')>"
        expected += "<'Token'(text='precision', start='35', end='44', kind='word')>"
        expected += "<'Token'(text='medicine', start='45', end='53', kind='word')>"
        expected += "<'Token'(text='biotechnology', start='54', end='67', kind='word')>"
        expected += "<'Token'(text='company', start='68', end='75', kind='word')>"
        expected += "<'Token'(text=',', start='75', end='76', kind='punc')>"
        expected += "<'Token'(text='today', start='77', end='82', kind='word')>"
        expected += "<'Token'(text='announced', start='83', end='92', kind='word')>"
        expected += "<'Token'(text='the', start='93', end='96', kind='word')>"
        expected += "<'Token'(text='pricing', start='97', end='104', kind='word')>"
        expected += "<'Token'(text='of', start='105', end='107', kind='word')>"
        expected += "<'Token'(text='a', start='108', end='109', kind='word')>"
        expected += "<'Token'(text='public', start='110', end='116', kind='word')>"
        expected += "<'Token'(text='offering', start='117', end='125', kind='word')>"
        expected += "<'Token'(text='of', start='126', end='128', kind='word')>"
        expected += "<'ShareQuantity'(text='15,000,000', start='129', end='139')>"
        expected += "<'Token'(text='shares', start='140', end='146', kind='word')>"
        expected += "<'Token'(text='of', start='147', end='149', kind='word')>"
        expected += "<'Token'(text='its', start='150', end='153', kind='word')>"
        expected += "<'Token'(text='common', start='154', end='160', kind='word')>"
        expected += "<'Token'(text='stock', start='161', end='166', kind='word')>"
        expected += "<'Token'(text='(', start='167', end='168', kind='punc')>"
        expected += "<'Token'(text='or', start='168', end='170', kind='word')>"
        expected += "<'Token'(text='common', start='171', end='177', kind='word')>"
        expected += "<'Token'(text='stock', start='178', end='183', kind='word')>"
        expected += "<'Token'(text='equivalents', start='184', end='195', kind='word')>"
        expected += "<'Token'(text=')', start='195', end='196', kind='punc')>"
        expected += "<'Token'(text='and', start='197', end='200', kind='word')>"
        expected += "<'Token'(text='common', start='201', end='207', kind='word')>"
        expected += "<'WarrantPurchase'(text='warrants to purchase', start='208', end='228')>"
        expected += "<'Token'(text='up', start='229', end='231', kind='word')>"
        expected += "<'Token'(text='to', start='232', end='234', kind='word')>"
        expected += "<'Token'(text='an', start='235', end='237', kind='word')>"
        expected += "<'Token'(text='aggregate', start='238', end='247', kind='word')>"
        expected += "<'Token'(text='of', start='248', end='250', kind='word')>"
        expected += "<'ShareQuantity'(text='5,000,000', start='251', end='259')>"
        expected += "<'Token'(text='shares', start='261', end='267', kind='word')>"
        expected += "<'Token'(text='of', start='268', end='270', kind='word')>"
        expected += "<'Token'(text='common', start='271', end='277', kind='word')>"
        expected += "<'Token'(text='stock', start='278', end='283', kind='word')>"
        expected += "<'Token'(text='.', start='283', end='284', kind='punc')>"

        inputStr = "SafestWay, Inc. (NASDAQ:Â SFSY), a precision medicine biotechnology company, " + \
                   "today announced the pricing of a public offering of 15,000,000 shares of its common " + \
                   "stock (or common stock equivalents) and common warrants to purchase up to an aggregate " + \
                   "of 5,000,000 shares of common stock."

        ann1 = Annotation('ShareQuantity', '15,000,000', 129, 139)
        ann2 = Annotation('WarrantPurchase', 'warrants to purchase', 208, 228)
        ann3 = Annotation('ShareQuantity', '5,000,000', 251, 259)
        anns = [ann1, ann2, ann3]

        actual = ExtractionPhaseABC.build_merged_representation(inputStr, anns)
        self.assertEqual(expected, actual)

        # Add empty spaces to end of input string.
        inputStr = "SafestWay, Inc. (NASDAQ:Â SFSY), a precision medicine biotechnology company, " + \
                   "today announced the pricing of a public offering of 15,000,000 shares of its common " + \
                   "stock (or common stock equivalents) and common warrants to purchase up to an aggregate " + \
                   "of 5,000,000 shares of common stock.  "

        ann1 = Annotation('ShareQuantity', '15,000,000', 129, 139)
        ann2 = Annotation('WarrantPurchase', 'warrants to purchase', 208, 228)
        ann3 = Annotation('ShareQuantity', '5,000,000', 251, 259)
        anns = [ann1, ann2, ann3]

        actual = ExtractionPhaseABC.build_merged_representation(inputStr, anns)
        self.assertEqual(expected, actual)


    def testBuildMergedInput2(self):
        # Test build_merged_representation( ) where annotations begin and end the test document.

        expected = "<'ShareQuantity'(text='15,000,000', start='0', end='10')>"
        expected += "<'Token'(text='shares', start='11', end='17', kind='word')>"
        expected += "<'Token'(text='of', start='18', end='20', kind='word')>"
        expected += "<'Token'(text='its', start='21', end='24', kind='word')>"
        expected += "<'Token'(text='common', start='25', end='31', kind='word')>"
        expected += "<'Token'(text='stock', start='32', end='37', kind='word')>"
        expected += "<'Token'(text='(', start='38', end='39', kind='punc')>"
        expected += "<'Token'(text='or', start='39', end='41', kind='word')>"
        expected += "<'Token'(text='common', start='42', end='48', kind='word')>"
        expected += "<'Token'(text='stock', start='49', end='54', kind='word')>"
        expected += "<'Token'(text='equivalents', start='55', end='66', kind='word')>"
        expected += "<'Token'(text=')', start='66', end='67', kind='punc')>"
        expected += "<'Token'(text='and', start='68', end='71', kind='word')>"
        expected += "<'Token'(text='common', start='72', end='78', kind='word')>"
        expected += "<'WarrantPurchase'(text='warrants to purchase', start='79', end='99')>"

        inputStr = "15,000,000 shares of its common " + \
                   "stock (or common stock equivalents) and common warrants to purchase"

        ann1 = Annotation('ShareQuantity', '15,000,000', 0, 10)
        ann2 = Annotation('WarrantPurchase', 'warrants to purchase', 79, 99)
        anns = [ann1, ann2]

        actual = ExtractionPhaseABC.build_merged_representation(inputStr, anns)
        self.assertEqual(expected, actual)


    def testBuildMergedInputInvalidAnnotation(self):
        # Test build_merged_representation( ) when we input annotations whose offsets don't match the
        # input contents.

        inputStr = "15,000,000 shares of its common " + \
                   "stock (or common stock equivalents) and common warrants to purchase"

        ann1 = Annotation('ShareQuantity', '15,000,000', 0, 10)
        ann2 = Annotation('WarrantPurchase', 'warrants to purchase', 79, 99)
        # This is not in the input string and goes beyond its length.
        ann3 = Annotation('ShareQuantity', '5,000,000', 251, 259)
        anns = [ann1, ann2, ann3]

        with self.assertRaises(ValueError):
            ExtractionPhaseABC.build_merged_representation(inputStr, anns)


    def testBuildMergedInputWithUnconsumedAnnotation(self):
        # Use as input a doc which at one time resulted in the unconsumed annotations
        # value error (due to the annotations' being within parentheses).

        expected = "<'Token'(text='Millennial', start='2', end='12', kind='word')>"
        expected += "<'Token'(text='(', start='13', end='14', kind='punc')>"
        expected += "<'Token'(text='NASDAQ', start='14', end='20', kind='word')>"
        expected += "<'Token'(text=':', start='20', end='21', kind='punc')>"
        expected += "<'Token'(text='MILL', start='21', end='25', kind='word')>"
        expected += "<'Token'(text=')', start='25', end='26', kind='punc')>"
        expected += "<'Token'(text='today', start='27', end='32', kind='word')>"
        expected += "<'Token'(text='announced', start='33', end='42', kind='word')>"
        expected += "<'Token'(text='a', start='43', end='44', kind='word')>"
        expected += "<'Token'(text='public', start='45', end='51', kind='word')>"
        expected += "<'Token'(text='offering', start='52', end='60', kind='word')>"
        expected += "<'Token'(text='of', start='61', end='63', kind='word')>"
        expected += "<'ShareQuantity'(text='25,000,000', start='64', end='74')>"
        expected += "<'Token'(text='shares', start='75', end='81', kind='word')>"
        expected += "<'Token'(text='of', start='82', end='84', kind='word')>"
        expected += "<'Token'(text='common', start='85', end='91', kind='word')>"
        expected += "<'Token'(text='stock', start='92', end='97', kind='word')>"
        expected += "<'Token'(text='by', start='98', end='100', kind='word')>"
        expected += "<'Token'(text='Riverstone', start='101', end='111', kind='word')>"
        expected += "<'Token'(text='VI', start='112', end='114', kind='word')>"
        expected += "<'Token'(text='(', start='115', end='116', kind='punc')>"
        expected += "<'ShareQuantity'(text='15,000,000', start='116', end='126')>"
        expected += "<'Token'(text='shares', start='127', end='133', kind='word')>"
        expected += "<'Token'(text=')', start='133', end='134', kind='punc')>"
        expected += "<'Token'(text='and', start='135', end='138', kind='word')>"
        expected += "<'Token'(text='Millennial', start='139', end='149', kind='word')>"
        expected += "<'Token'(text='(', start='150', end='151', kind='punc')>"
        expected += "<'ShareQuantity'(text='10,000,000', start='151', end='161')>"
        expected += "<'Token'(text='shares', start='162', end='168', kind='word')>"
        expected += "<'Token'(text=')', start='168', end='169', kind='punc')>"
        expected += "<'Token'(text='.', start='169', end='170', kind='punc')>"


        inputStr = "  Millennial (NASDAQ:MILL) today announced a "
        inputStr += "public offering of 25,000,000 shares of "
        inputStr += "common stock by Riverstone VI (15,000,000 shares) "
        inputStr += "and Millennial (10,000,000 shares)."

        ann0 = Annotation('ShareQuantity', '25,000,000', 64, 74)
        ann1 = Annotation('ShareQuantity', '15,000,000', 116, 126)
        ann2 = Annotation('ShareQuantity', '10,000,000', 151, 161)
        anns = [ann0, ann1, ann2]

        actual = ExtractionPhaseABC.build_merged_representation(inputStr, anns)
        self.assertEqual(expected, actual)


    def testGetTokenObjects1(self):
        docStr = "My friend (i.e., my best friend) has betrayed me."

        actualObjs = TokenAnn.get_token_objects(docStr[0:2], 0)
        actual = [str(x) for x in actualObjs]
        expected = ["<'Token'(text='My', start='0', end='2', kind='word')>"]
        self.assertEqual(expected, actual)

        actualObjs = TokenAnn.get_token_objects(docStr[0:16], 0)
        actual = [str(x) for x in actualObjs]
        expected = ["<'Token'(text='My', start='0', end='2', kind='word')>",
                    "<'Token'(text='friend', start='3', end='9', kind='word')>",
                    "<'Token'(text='(', start='10', end='11', kind='punc')>",
                    "<'Token'(text='i.e.', start='11', end='15', kind='other')>",
                    "<'Token'(text=',', start='15', end='16', kind='punc')>"]
        self.assertEqual(expected, actual)

        # Start the input string with a space.
        actualObjs = TokenAnn.get_token_objects(docStr[9:16], 9)
        actual = [str(x) for x in actualObjs]
        expected = ["<'Token'(text='(', start='10', end='11', kind='punc')>",
                    "<'Token'(text='i.e.', start='11', end='15', kind='other')>",
                    "<'Token'(text=',', start='15', end='16', kind='punc')>"]
        self.assertEqual(expected, actual)


    def testGetTokenObjects2(self):
        docStr = "SafestWay, Inc. (NASDAQ:Â SFSY),  "

        actualObjs = TokenAnn.get_token_objects(docStr, 0)

        actual = [str(x) for x in actualObjs]
        expected = ["<'Token'(text='SafestWay', start='0', end='9', kind='word')>",
                    "<'Token'(text=',', start='9', end='10', kind='punc')>",
                    "<'Token'(text='Inc.', start='11', end='15', kind='other')>",
                    "<'Token'(text='(', start='16', end='17', kind='punc')>",
                    "<'Token'(text='NASDAQ', start='17', end='23', kind='word')>",
                    "<'Token'(text=':', start='23', end='24', kind='punc')>",
                    "<'Token'(text='Â', start='24', end='25', kind='word')>",
                    "<'Token'(text='SFSY', start='26', end='30', kind='word')>",
                    "<'Token'(text=')', start='30', end='31', kind='punc')>",
                    "<'Token'(text=',', start='31', end='32', kind='punc')>"]

        self.assertEqual(expected, actual)
