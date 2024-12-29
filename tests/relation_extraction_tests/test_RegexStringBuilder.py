import unittest

from text_to_relations.relation_extraction.RegexString import RegexString


class Testbuild_regex_string(unittest.TestCase):
    
    def testInvalid(self):
        inputList = [['holy', 'smoke'], 2]
        with self.assertRaises(ValueError):
            RegexString.build_regex_string(inputList)
            
        inputList = [['holy', 'smoke']]
        with self.assertRaises(ValueError):
            RegexString.build_regex_string(inputList)


    def testSimple(self):
        inputList = [['good', 'terrific'], 2, ['work', 'job']]
        regexString = RegexString.build_regex_string(inputList)

        self.assertEqual(r'(?:terrific|good)(?:\b\S+)?(?:\s\S+){0,2}\s(?:work|job)', regexString.get_regex_str())


    def testThree(self):
        inputList = [['incredibly'], 0, ['good', 'terrific'], 2, ['work', 'job']]
        regexString = RegexString.build_regex_string(inputList)
    
        self.assertEqual(r'incredibly(?:\b\S+)?\s(?:terrific|good)(?:\b\S+)?(?:\s\S+){0,2}\s(?:work|job)', regexString.get_regex_str())
