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

        # Test the regex. Note: re.escape() escapes spaces, so 'a monkey' becomes
        # 'a\ monkey' in the pattern. In normal (non-verbose) mode, '\ ' and ' ' match identically.
        expected = r'a\ monkey\.'
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

        # Test the regex. Note: re.escape() escapes spaces ('a\ monkey'); '\ ' matches
        # identically to ' ' in normal (non-verbose) mode.
        expected = r'(?:a\ monkey)?\.'
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

        # Test the regex. Note: re.escape() escapes spaces ('a\ sad\ monkey'); '\ ' matches
        # identically to ' ' in normal (non-verbose) mode.
        expected = r'(?:a\ sad\ monkey|the\ monkey|a\ monkey)'
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

        # Test the regex. Note: re.escape() escapes spaces ('a\ sad\ monkey'); '\ ' matches
        # identically to ' ' in normal (non-verbose) mode.
        expected = r'(?:a\ sad\ monkey|the\ monkey|a\ monkey)'
        self.assertEqual(expected, str(regexString))

        # Test matching.
        triples = regexString.get_match_triples(inputStr)
        expected = [('a monkey', 6, 14), ('a sad monkey', 58, 70)]
        self.assertEqual(expected, triples)


    def testMatchStringsWithCollection(self):
        """ Test that match_strs items are treated as plain strings.
        Previously, regex syntax could be embedded in match_strs items; this is
        no longer supported as items are now escaped via re.escape(). Use
        prepend/append or concat() for regex syntax in patterns. """
        inputStr = 'I saw a monkey. The monkey was sad.'
        inputStr += 'It made me sad to see a sad monkey. It made me weep to see a weeping monkey.'
        inputStr = inputStr.lower()

        # List all variants explicitly instead of embedding regex syntax.
        wholeMatchStrings = ['a sad monkey', 'a weeping monkey', 'the monkey', 'a monkey']
        wholeRegexString = RegexString(wholeMatchStrings, non_capturing=True)

        # Test the regex.
        expected = r'(?:a\ weeping\ monkey|a\ sad\ monkey|the\ monkey|a\ monkey)'
        self.assertEqual(expected, str(wholeRegexString))

        # Test matching.
        match_strs = re.findall(str(wholeRegexString), inputStr)
        expected = ['a monkey', 'the monkey', 'a sad monkey', 'a weeping monkey']
        self.assertEqual(expected, match_strs)


    def testNestedGroupingTrueWithCollection(self):
        """ Test RegexStrings with capturing groups (non_capturing=False). """
        inputStr = 'I saw a monkey. The monkey was sad.'
        inputStr += 'It made me sad to see a sad monkey. It made me weep to see a weeping monkey.'
        inputStr = inputStr.lower()

        matchStrings = ['a monkey', 'the monkey', 'a sad monkey', 'a weeping monkey']
        regexString = RegexString(matchStrings, non_capturing=False)

        # With non_capturing=False the group uses a capturing group, not '(?:...)'.
        # Note: re.escape() escapes spaces ('a\ weeping\ monkey'); '\ ' matches
        # identically to ' ' in normal (non-verbose) mode.
        expected = r'(a\ weeping\ monkey|a\ sad\ monkey|the\ monkey|a\ monkey)'
        self.assertEqual(expected, str(regexString))

        # re.findall returns the captured group text.
        match_strs = re.findall(str(regexString), inputStr)
        expected = ['a monkey', 'the monkey', 'a sad monkey', 'a weeping monkey']
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

    def test_case_insensitive(self):
        """Test case_insensitive=True matches regardless of case and preserves original casing in triples."""
        inputStr = 'I Saw A Monkey. The MONKEY was SAD.'

        rs = RegexString(['monkey', 'sad'])

        # Without the flag: lowercase match_strs don't match mixed-case input.
        triples = rs.get_match_triples(inputStr)
        self.assertEqual([], triples)

        # With the flag: matches all case variants; original casing preserved in matched text.
        triples = rs.get_match_triples(inputStr, case_insensitive=True)
        self.assertEqual([('Monkey', 8, 14), ('MONKEY', 20, 26), ('SAD', 31, 34)], triples)

        # Old approach (lowercase both sides): works but matched text is lowercased.
        triples_lower = rs.get_match_triples(inputStr.lower())
        self.assertEqual([('monkey', 8, 14), ('monkey', 20, 26), ('sad', 31, 34)], triples_lower)

    def test_special_chars_in_match_strs(self):
        """ Test that regex metacharacters in match_strs are treated as literals
        via re.escape(). Previously these would cause re.error at match time. """
        inputStr = 'price is (10) dollars or [20] euros'

        # Parentheses
        rs = RegexString(['(10)'])
        self.assertEqual(r'\(10\)', rs.get_regex_str())
        triples = rs.get_match_triples(inputStr)
        self.assertEqual([('(10)', 9, 13)], triples)

        # Square brackets
        rs = RegexString(['[20]'])
        self.assertEqual(r'\[20\]', rs.get_regex_str())
        triples = rs.get_match_triples(inputStr)
        self.assertEqual([('[20]', 25, 29)], triples)

