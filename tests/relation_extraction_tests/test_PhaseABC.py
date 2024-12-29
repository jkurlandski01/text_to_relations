import unittest

from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC


class TestPhaseABC(unittest.TestCase):

    def testInvalidSubclass1(self):

        # noinspection PyAbstractClass
        class PhaseTest(ExtractionPhaseABC):
            """ This class has no run_phase() method. """
            def __init__(self):
                """"""
                super().__init__()

        with self.assertRaises(TypeError):
            PhaseTest()


    def testInvalidSubclass2(self):
        # Test on failure to pass document contents to the 
        # ABC's init().
        
        # noinspection PyAbstractClass
        class PhaseTest(ExtractionPhaseABC):

            # noinspection PyUnusedLocal
            def __init__(self, docContents):
                """"""
                super().__init__()

            def run_phase(self):
                return 'How are you?!'

        with self.assertRaises(TypeError):
            PhaseTest("Hi!")

    def testInvalidSubclass3(self):
        # Test on document contents being an empty string.
        
        # noinspection PyAbstractClass
        class PhaseTest(ExtractionPhaseABC):

            # noinspection PyUnusedLocal
            def __init__(self, docContents):
                """"""
                super().__init__(docContents)

            def run_phase(self):
                return 'How are you?!'

        with self.assertRaises(TypeError):
            PhaseTest("")


    def testValidSubclass(self):

        class PhaseTest(ExtractionPhaseABC):
            # noinspection PyUnusedLocal
            def __init__(self, docContents):
                """"""
                super().__init__(docContents)

            def run_phase(self):
                return 'Hi!'

        phase = PhaseTest('blahBlahBlah')
        actual = phase.run_phase()

        self.assertEqual('Hi!', actual)

    def testBuildMergedInput1(self):
        # All assertions expect the same output, except for sometimes the annotation offsets.

        self.maxDiff = None

        expected = "<'Token'(normalizedContents='SafestWay', start='0', end='9', kind='word')>"
        expected += "<'Token'(normalizedContents=',', start='9', end='10', kind='punc')>"
        expected += "<'Token'(normalizedContents='Inc.', start='11', end='15', kind='other')>"
        expected += "<'Token'(normalizedContents='(', start='16', end='17', kind='punc')>"
        expected += "<'Token'(normalizedContents='NASDAQ', start='17', end='23', kind='word')>"
        expected += "<'Token'(normalizedContents=':', start='23', end='24', kind='punc')>"
        expected += "<'Token'(normalizedContents='Â', start='24', end='25', kind='word')>"
        expected += "<'Token'(normalizedContents='SFSY', start='26', end='30', kind='word')>"
        expected += "<'Token'(normalizedContents=')', start='30', end='31', kind='punc')>"
        expected += "<'Token'(normalizedContents=',', start='31', end='32', kind='punc')>"
        expected += "<'Token'(normalizedContents='a', start='33', end='34', kind='word')>"
        expected += "<'Token'(normalizedContents='precision', start='35', end='44', kind='word')>"
        expected += "<'Token'(normalizedContents='medicine', start='45', end='53', kind='word')>"
        expected += "<'Token'(normalizedContents='biotechnology', start='54', end='67', kind='word')>"
        expected += "<'Token'(normalizedContents='company', start='68', end='75', kind='word')>"
        expected += "<'Token'(normalizedContents=',', start='75', end='76', kind='punc')>"
        expected += "<'Token'(normalizedContents='today', start='77', end='82', kind='word')>"
        expected += "<'Token'(normalizedContents='announced', start='83', end='92', kind='word')>"
        expected += "<'Token'(normalizedContents='the', start='93', end='96', kind='word')>"
        expected += "<'Token'(normalizedContents='pricing', start='97', end='104', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='105', end='107', kind='word')>"
        expected += "<'Token'(normalizedContents='a', start='108', end='109', kind='word')>"
        expected += "<'Token'(normalizedContents='public', start='110', end='116', kind='word')>"
        expected += "<'Token'(normalizedContents='offering', start='117', end='125', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='126', end='128', kind='word')>"
        expected += "<'ShareQuantity'(normalizedContents='15,000,000', start='129', end='139')>"
        expected += "<'Token'(normalizedContents='shares', start='140', end='146', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='147', end='149', kind='word')>"
        expected += "<'Token'(normalizedContents='its', start='150', end='153', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='154', end='160', kind='word')>"
        expected += "<'Token'(normalizedContents='stock', start='161', end='166', kind='word')>"
        expected += "<'Token'(normalizedContents='(', start='167', end='168', kind='punc')>"
        expected += "<'Token'(normalizedContents='or', start='168', end='170', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='171', end='177', kind='word')>"
        expected += "<'Token'(normalizedContents='stock', start='178', end='183', kind='word')>"
        expected += "<'Token'(normalizedContents='equivalents', start='184', end='195', kind='word')>"
        expected += "<'Token'(normalizedContents=')', start='195', end='196', kind='punc')>"
        expected += "<'Token'(normalizedContents='and', start='197', end='200', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='201', end='207', kind='word')>"
        expected += "<'WarrantPurchase'(normalizedContents='warrants to purchase', start='208', end='228')>"
        expected += "<'Token'(normalizedContents='up', start='229', end='231', kind='word')>"
        expected += "<'Token'(normalizedContents='to', start='232', end='234', kind='word')>"
        expected += "<'Token'(normalizedContents='an', start='235', end='237', kind='word')>"
        expected += "<'Token'(normalizedContents='aggregate', start='238', end='247', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='248', end='250', kind='word')>"
        expected += "<'ShareQuantity'(normalizedContents='5,000,000', start='251', end='259')>"
        expected += "<'Token'(normalizedContents='shares', start='261', end='267', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='268', end='270', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='271', end='277', kind='word')>"
        expected += "<'Token'(normalizedContents='stock', start='278', end='283', kind='word')>"
        expected += "<'Token'(normalizedContents='.', start='283', end='284', kind='punc')>"

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
        
        expected = "<'ShareQuantity'(normalizedContents='15,000,000', start='0', end='10')>"
        expected += "<'Token'(normalizedContents='shares', start='11', end='17', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='18', end='20', kind='word')>"
        expected += "<'Token'(normalizedContents='its', start='21', end='24', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='25', end='31', kind='word')>"
        expected += "<'Token'(normalizedContents='stock', start='32', end='37', kind='word')>"
        expected += "<'Token'(normalizedContents='(', start='38', end='39', kind='punc')>"
        expected += "<'Token'(normalizedContents='or', start='39', end='41', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='42', end='48', kind='word')>"
        expected += "<'Token'(normalizedContents='stock', start='49', end='54', kind='word')>"
        expected += "<'Token'(normalizedContents='equivalents', start='55', end='66', kind='word')>"
        expected += "<'Token'(normalizedContents=')', start='66', end='67', kind='punc')>"
        expected += "<'Token'(normalizedContents='and', start='68', end='71', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='72', end='78', kind='word')>"
        expected += "<'WarrantPurchase'(normalizedContents='warrants to purchase', start='79', end='99')>"

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

        expected = "<'Token'(normalizedContents='Millennial', start='2', end='12', kind='word')>"
        expected += "<'Token'(normalizedContents='(', start='13', end='14', kind='punc')>"
        expected += "<'Token'(normalizedContents='NASDAQ', start='14', end='20', kind='word')>"
        expected += "<'Token'(normalizedContents=':', start='20', end='21', kind='punc')>"
        expected += "<'Token'(normalizedContents='MILL', start='21', end='25', kind='word')>"
        expected += "<'Token'(normalizedContents=')', start='25', end='26', kind='punc')>"
        expected += "<'Token'(normalizedContents='today', start='27', end='32', kind='word')>"
        expected += "<'Token'(normalizedContents='announced', start='33', end='42', kind='word')>"
        expected += "<'Token'(normalizedContents='a', start='43', end='44', kind='word')>"
        expected += "<'Token'(normalizedContents='public', start='45', end='51', kind='word')>"
        expected += "<'Token'(normalizedContents='offering', start='52', end='60', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='61', end='63', kind='word')>"
        expected += "<'ShareQuantity'(normalizedContents='25,000,000', start='64', end='74')>"
        expected += "<'Token'(normalizedContents='shares', start='75', end='81', kind='word')>"
        expected += "<'Token'(normalizedContents='of', start='82', end='84', kind='word')>"
        expected += "<'Token'(normalizedContents='common', start='85', end='91', kind='word')>"
        expected += "<'Token'(normalizedContents='stock', start='92', end='97', kind='word')>"
        expected += "<'Token'(normalizedContents='by', start='98', end='100', kind='word')>"
        expected += "<'Token'(normalizedContents='Riverstone', start='101', end='111', kind='word')>"
        expected += "<'Token'(normalizedContents='VI', start='112', end='114', kind='word')>"
        expected += "<'Token'(normalizedContents='(', start='115', end='116', kind='punc')>"
        expected += "<'ShareQuantity'(normalizedContents='15,000,000', start='116', end='126')>"
        expected += "<'Token'(normalizedContents='shares', start='127', end='133', kind='word')>"
        expected += "<'Token'(normalizedContents=')', start='133', end='134', kind='punc')>"
        expected += "<'Token'(normalizedContents='and', start='135', end='138', kind='word')>"
        expected += "<'Token'(normalizedContents='Millennial', start='139', end='149', kind='word')>"
        expected += "<'Token'(normalizedContents='(', start='150', end='151', kind='punc')>"
        expected += "<'ShareQuantity'(normalizedContents='10,000,000', start='151', end='161')>"
        expected += "<'Token'(normalizedContents='shares', start='162', end='168', kind='word')>"
        expected += "<'Token'(normalizedContents=')', start='168', end='169', kind='punc')>"
        expected += "<'Token'(normalizedContents='.', start='169', end='170', kind='punc')>"


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
        expected = ["<'Token'(normalizedContents='My', start='0', end='2', kind='word')>"]
        self.assertEqual(expected, actual)

        actualObjs = TokenAnn.get_token_objects(docStr[0:16], 0)
        actual = [str(x) for x in actualObjs]
        expected = ["<'Token'(normalizedContents='My', start='0', end='2', kind='word')>",
                    "<'Token'(normalizedContents='friend', start='3', end='9', kind='word')>",
                    "<'Token'(normalizedContents='(', start='10', end='11', kind='punc')>",
                    "<'Token'(normalizedContents='i.e.', start='11', end='15', kind='other')>",
                    "<'Token'(normalizedContents=',', start='15', end='16', kind='punc')>"]
        self.assertEqual(expected, actual)

        # Start the input string with a space.
        actualObjs = TokenAnn.get_token_objects(docStr[9:16], 9)
        actual = [str(x) for x in actualObjs]
        expected = ["<'Token'(normalizedContents='(', start='10', end='11', kind='punc')>",
                    "<'Token'(normalizedContents='i.e.', start='11', end='15', kind='other')>",
                    "<'Token'(normalizedContents=',', start='15', end='16', kind='punc')>"]
        self.assertEqual(expected, actual)


    def testGetTokenObjects2(self):
        docStr = "SafestWay, Inc. (NASDAQ:Â SFSY),  "

        actualObjs = TokenAnn.get_token_objects(docStr, 0)

        actual = [str(x) for x in actualObjs]
        expected = ["<'Token'(normalizedContents='SafestWay', start='0', end='9', kind='word')>",
                    "<'Token'(normalizedContents=',', start='9', end='10', kind='punc')>",
                    "<'Token'(normalizedContents='Inc.', start='11', end='15', kind='other')>",
                    "<'Token'(normalizedContents='(', start='16', end='17', kind='punc')>",
                    "<'Token'(normalizedContents='NASDAQ', start='17', end='23', kind='word')>",
                    "<'Token'(normalizedContents=':', start='23', end='24', kind='punc')>",
                    "<'Token'(normalizedContents='Â', start='24', end='25', kind='word')>",
                    "<'Token'(normalizedContents='SFSY', start='26', end='30', kind='word')>",
                    "<'Token'(normalizedContents=')', start='30', end='31', kind='punc')>",
                    "<'Token'(normalizedContents=',', start='31', end='32', kind='punc')>"]
        
        self.assertEqual(expected, actual)
