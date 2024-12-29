"""
Test RegexString functionality outside of the concat() and concat_with_word_distances() methods.
Some of the functionality tested here may no longer be very useful, now that
concat() and concat_with_word_distances() have been implemented.
"""

import re
import unittest

from text_to_relations.relation_extraction.RegexString import RegexString


class TestRegexString(unittest.TestCase):
    
    def testInvalidInit(self):
        with self.assertRaises(ValueError):
            RegexString('a monkey')


    def testSimpleNoCollection(self):
        # Test with a single, non-OR'd match, with an append string.
        inputStr = 'I saw a monkey. The monkey was sad. It made me sad to see a sad monkey.'
        inputStr = inputStr.lower()

        matchStrings = ['a monkey']
        regexString = RegexString(matchStrings, append='\.')

        # Test the regex.
        expected = r'a monkey\.'
        self.assertEqual(expected, str(regexString))

        # Test matching.
        match_strs = re.findall(regexString.get_regex_str(), inputStr)
        expected = ['a monkey.']
        self.assertEqual(expected, match_strs)


    def testSimpleNoCollectionOptional(self):
        # Test with a single, non-OR'd match which is optional, with an append string.
        inputStr = 'I saw a monkey. The monkey was sad. It made me sad to see a sad monkey.'
        inputStr = inputStr.lower()

        matchStrings = ['a monkey']
        regexString = RegexString(matchStrings, optional=True, append='\.')

        # Test the regex.
        expected = r'(?:a monkey)?\.'
        self.assertEqual(expected, str(regexString))

        # Test matching.
        match_strs = re.findall(regexString.get_regex_str(), inputStr)
        expected = ['a monkey.', '.', '.']
        self.assertEqual(expected, match_strs)
    
    
    def testSimpleWithCollection(self):
        """ Test on the normal case--no grouping and case-insensitive. """
        inputStr = 'I saw a monkey. The monkey was sad. It made me sad to see a sad monkey.'
        inputStr = inputStr.lower()

        matchStrings = ['a monkey', 'the monkey', 'a sad monkey']

        regexString = RegexString(matchStrings)

        # Test the regex.
        expected = r'(?:a sad monkey|the monkey|a monkey)'
        self.assertEqual(expected, str(regexString))

        # Test matching.
        match_strs = re.findall(regexString.get_regex_str(), inputStr)
        expected = ['a monkey', 'the monkey', 'a sad monkey']
        self.assertEqual(expected, match_strs)


    def testPrependAppendWithCollection(self):
        """ Test on the normal case--no grouping and case-insensitive. """
        inputStr = 'See. I saw a monkey. The monkey was sad. It made me sad to see a sad monkey.'
        inputStr = inputStr.lower()

        matchStrings = ['see', 'saw']

        # Require one word before see/saw.
        regexString = RegexString(matchStrings, prepend='\w+ ')

        # Test the regex.
        expected = r'\w+ (?:see|saw)'
        self.assertEqual(expected, str(regexString))

        # Test matching.
        match_strs = re.findall(regexString.get_regex_str(), inputStr)
        expected = ['i saw', 'to see']
        self.assertEqual(expected, match_strs)

        # Allow an optional one word before see/saw.
        regexString = RegexString(matchStrings, prepend='(?:\w+ )?')

        # Test the regex.
        expected = r'(?:\w+ )?(?:see|saw)'
        self.assertEqual(expected, str(regexString))

        # Test matching.
        match_strs = re.findall(regexString.get_regex_str(), inputStr)
        expected = ['see', 'i saw', 'to see']
        self.assertEqual(expected, match_strs)

        # Allow an optional one word before 'see/saw'--
        # and require the word 'a' after.
        regexString = RegexString(matchStrings, 
                        prepend='(?:\w+ )?', append=' a')
    
        # Test the regex.
        expected = r'(?:\w+ )?(?:see|saw) a'
        self.assertEqual(expected, str(regexString))
    
        # Test matching.
        match_strs = re.findall(regexString.get_regex_str(), inputStr)
        expected = ['i saw a', 'to see a']
        self.assertEqual(expected, match_strs)
    
    
    def testCaseSensitiveWithCollection(self):
        """ Test on a case-sensitive usage. """
        inputStr = 'I saw a monkey. The monkey was sad. It made me sad to see a sad monkey.'

        matchStrings = ['a monkey', 'the monkey', 'a sad monkey']

        regexString = RegexString(matchStrings)

        # Test the regex.
        expected = r'(?:a sad monkey|the monkey|a monkey)'
        self.assertEqual(expected, str(regexString))

        # Test matching.
        triples = regexString.get_match_triples(inputStr)
        expected = [('a monkey', 6, 14), ('a sad monkey', 58, 70)]
        self.assertEqual(expected, triples)


    def testNestedRegexStringWithCollection(self):
        """ Test on nested RegexStrings. """
        inputStr = 'I saw a monkey. The monkey was sad.'
        inputStr += 'It made me sad to see a sad monkey. It made me weep to see a weeping monkey.'
        inputStr = inputStr.lower()

        unhappyMatchStrings = [' sad', ' weeping']
        unhappyRegexString = RegexString(unhappyMatchStrings)
        self.assertEqual('(?: weeping| sad)', str(unhappyRegexString))
        
        wholeMatchStrings = ['a monkey', 'the monkey', 'a' + unhappyRegexString.get_regex_str() + ' monkey']

        wholeRegexString = RegexString(wholeMatchStrings, non_capturing=True)

        # Test the regex.
        expected = r'(?:a(?: weeping| sad) monkey|the monkey|a monkey)'
        self.assertEqual(expected, str(wholeRegexString))

        # Test matching.
        match_strs = re.findall(str(wholeRegexString), inputStr)
        expected = ['a monkey',
                    'the monkey',
                    'a sad monkey',
                    'a weeping monkey']
        self.assertEqual(expected, match_strs)
        
        
        # Try an optional nested match.
        unhappyMatchStrings = [' sad', ' weeping']
        unhappyRegexString = RegexString(unhappyMatchStrings, optional=True)
        self.assertEqual('(?: weeping| sad)?', str(unhappyRegexString))

        wholeMatchStrings = ['a' + unhappyRegexString.get_regex_str() + ' monkey']

        wholeRegexString = RegexString(wholeMatchStrings, non_capturing=True)

        # Test the regex.
        expected = r'a(?: weeping| sad)? monkey'
        self.assertEqual(expected, str(wholeRegexString))

        # Test matching.
        match_strs = re.findall(str(wholeRegexString), inputStr)
        expected = ['a monkey',
                    'a sad monkey',
                    'a weeping monkey']
        self.assertEqual(expected, match_strs)


    def testNestedGroupingTrueWithCollection(self):
        """ Test on nested RegexStrings with grouping turned on. """
        inputStr = 'I saw a monkey. The monkey was sad.'
        inputStr += 'It made me sad to see a sad monkey. It made me weep to see a weeping monkey.'
        inputStr = inputStr.lower()

        unhappyMatchStrings = [' sad', ' weeping']
        unhappyRegexString = RegexString(unhappyMatchStrings, non_capturing=False)
        self.assertEqual('( weeping| sad)', str(unhappyRegexString))

        wholeMatchStrings = ['a monkey', 'the monkey', 'a' + unhappyRegexString.get_regex_str() + ' monkey']

        wholeRegexString = RegexString(wholeMatchStrings, non_capturing=False)

        # Test the regex.
        expected = r'(a( weeping| sad) monkey|the monkey|a monkey)'
        self.assertEqual(expected, str(wholeRegexString))

        # Test matching.
        match_strs = re.findall(str(wholeRegexString), inputStr)
        expected = [('a monkey', ''),
                    ('the monkey', ''),
                    ('a sad monkey', ' sad'),
                    ('a weeping monkey', ' weeping')]
        self.assertEqual(expected, match_strs)

    def test_wholeword(self):
        """ Test the whole_word option. """
        input = 'IVY IV YIV'

        # whole_word = False
        regex = RegexString(['IV'])
        triples = regex.get_match_triples(input)
        self.assertEqual(3, len(triples))

        # whole_word = True
        regex = RegexString(['IV'], whole_word=True)
        triples = regex.get_match_triples(input)
        self.assertEqual(1, len(triples))

        # prepend and append of '\b'--word boundary prints as
        # backspace; fixed in RegexString()
        backslash_b = '\b'
        esc_backslash_b = r'\b'

        regex = RegexString(['IV'], whole_word=False, prepend=backslash_b, append=backslash_b)
        actual = regex.get_regex_str()
        self.assertEqual("\\bIV\\b", actual)
        self.assertEqual(f"{esc_backslash_b}IV{esc_backslash_b}", actual)

        # whole_word = True and prepend and append of \b
        with self.assertRaises(ValueError):
            RegexString(['IV'], whole_word=True, prepend=esc_backslash_b)
        with self.assertRaises(ValueError):
            RegexString(['IV'], whole_word=True, append=esc_backslash_b)
        with self.assertRaises(ValueError):
            RegexString(['IV'], whole_word=True, prepend=backslash_b)
        with self.assertRaises(ValueError):
            RegexString(['IV'], whole_word=True, append=backslash_b)
