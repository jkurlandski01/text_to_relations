"""
Test the RegexString concat() and concat_with_word_distances() methods.
Use these tests for examples on how to use the class in the easiest way.
"""

import re
import unittest

from text_to_relations.relation_extraction.RegexString import RegexString


class TestRegexString(unittest.TestCase):
    
    def testInvalidConcat(self):
        # Test concat() for the cases where the parameters are not RegexString objects.
        regex_str = RegexString(['a monkey'])
        with self.assertRaises(ValueError):
            RegexString.concat(regex_str, ' and')

        with self.assertRaises(ValueError):
            RegexString.concat(' and', regex_str)


    def testInvalidconcat_with_word_distances1(self):
        # Test concat_with_word_distances() for the cases where the parameters are not RegexString objects.
        regex_str = RegexString(['a monkey'])
        with self.assertRaises(ValueError):
            RegexString.concat_with_word_distances(regex_str, ' and')

        with self.assertRaises(ValueError):
            RegexString.concat_with_word_distances(' and', regex_str)
    
    
    def testInvalidconcat_with_word_distances2(self):
        # Test concat_with_word_distances() for invalid min and max parameters.
        rs1 = RegexString(['saw', 'see'], optional=True)
        rs2 = RegexString(['a', 'the'], optional=True)
        with self.assertRaises(ValueError):
            RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=2, max_nbr_words=1)

        rs1 = RegexString(['saw', 'see'], optional=True)
        rs2 = RegexString(['a', 'the'], optional=True)
        with self.assertRaises(ValueError):
            # Uses the default value for max_nbr_words.
            RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1)


    def test_concat_with_word_distances1(self):
        # Run a test that illustrates a basic form of the concat_with_word_distances() functionality.
        # 1) Look for an optional 'saw' or 'see'.
        # 2) Look for an optional 'a' or 'the'.
        # 3) Look for a required 'sad', 'saddest' or 'morose'.
        # 4)_Look for a required 'monkey'.
        inputStr = 'I saw a sad monkey. It made me sad to see a morose monkey. '
        inputStr += 'The monkey was the saddest monkey ever seen. '
        inputStr += 'Such a sad, sad monkey.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['saw', 'see'], optional=True)
        rs2 = RegexString(['a', 'the'], optional=True)
        regexString3 = RegexString.concat_with_word_distances(rs1, rs2)

        # Verify internal state of object.
        self.assertEqual(r'(?:(?:saw|see)(?:\b\S+)?\s)?(?:the|a)?', regexString3.get_regex_str())
        # Not using inputStr because the optional arg leads to many matches on ''.
        match_strs = re.findall(regexString3.get_regex_str(), 'saw a monkey')
        expected = ['saw a', '', '', '', '', '', '', '', '']
        self.assertEqual(expected, match_strs)

        regexString4 = RegexString(['saddest', 'sad', 'morose'])
        regexString5 = RegexString.concat_with_word_distances(regexString3, regexString4)

        # Verify internal state of object.
        expected = r'(?:(?:saw|see)(?:\b\S+)?\s)?(?:(?:the|a)(?:\b\S+)?\s)?(?:saddest|morose|sad)'
        self.assertEqual(expected, regexString5.get_regex_str())
        match_strs = re.findall(regexString5.get_regex_str(), inputStr)
        expected = ['saw a sad', 'sad', 'see a morose', 'the saddest', 'a sad', 'sad']
        self.assertEqual(expected, match_strs)

        regexString6 = RegexString(['monkey'])
        finalRegexString = RegexString.concat_with_word_distances(regexString5, regexString6)

        # Test the regex.
        expected = r'(?:(?:saw|see)(?:\b\S+)?\s)?(?:(?:the|a)(?:\b\S+)?\s)?'
        expected += r'(?:saddest|morose|sad)(?:\b\S+)?\smonkey'
        self.assertEqual(expected, finalRegexString.get_regex_str())

        # Test matching.
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['saw a sad monkey', 'see a morose monkey', 'the saddest monkey', 'sad monkey']
        self.assertEqual(expected, match_strs)


    def test_concat_with_word_distances2(self):
        # Run a test that illustrates a basic form of the concat_with_word_distances() functionality.
        # 1) Look for an optional 'saw'.
        # 2) Look for an optional 'a' or 'the'.
        # 3) Look for a required 'sad', 'saddest' or 'morose'.
        # 4)_Look for a required 'monkey'.
        inputStr = 'I saw a sad monkey. It made me sad to see a morose monkey. '
        inputStr += 'The monkey was the saddest monkey ever seen. '
        inputStr += 'Such a sad, sad monkey.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['saw'], optional=True)
        rs2 = RegexString(['a', 'the'], optional=True)
        regexString3 = RegexString.concat_with_word_distances(rs1, rs2)

        # Verify internal state of object.
        self.assertEqual(r'(?:(?:saw)(?:\b\S+)?\s)?(?:the|a)?', regexString3.get_regex_str())
        # Not using inputStr because the optional arg leads to many matches on ''.
        match_strs = re.findall(regexString3.get_regex_str(), 'saw a monkey')
        expected = ['saw a', '', '', '', '', '', '', '', '']
        self.assertEqual(expected, match_strs)
        
        regexString4 = RegexString(['saddest', 'sad', 'morose'])
        regexString5 = RegexString.concat_with_word_distances(regexString3, regexString4)

        # Verify internal state of object.
        expected = r'(?:(?:saw)(?:\b\S+)?\s)?(?:(?:the|a)(?:\b\S+)?\s)?(?:saddest|morose|sad)'
        self.assertEqual(expected, regexString5.get_regex_str())
        match_strs = re.findall(regexString5.get_regex_str(), inputStr)
        
        expected = ['saw a sad', 'sad', 'a morose', 'the saddest', 'a sad', 'sad']
        self.assertEqual(expected, match_strs)

        regexString6 = RegexString(['monkey'])
        finalRegexString = RegexString.concat_with_word_distances(regexString5, regexString6)

        # Test the regex.
        expected = r'(?:(?:saw)(?:\b\S+)?\s)?(?:(?:the|a)(?:\b\S+)?\s)?(?:saddest|morose|sad)(?:\b\S+)?\smonkey'
        self.assertEqual(expected, finalRegexString.get_regex_str())

        # Test matching.
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['saw a sad monkey', 'a morose monkey', 'the saddest monkey', 'sad monkey']
        self.assertEqual(expected, match_strs)


    def test_concat_with_word_distances3(self):
        # Run a test that illustrates a basic form of the concat_with_word_distances() functionality.
        # 1) Look for a required 'saw'.
        # 2) Look for an optional 'a' or 'the'.
        # 3) Look for a required 'sad', 'saddest' or 'morose'.
        # 4)_Look for a required 'monkey'.
        inputStr = 'I saw a sad monkey. It made me sad to see a morose monkey. '
        inputStr += 'The monkey was the saddest monkey ever seen. '
        inputStr += 'Such a sad, sad monkey.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['saw'])
        rs2 = RegexString(['a', 'the'], optional=True)
        regexString3 = RegexString.concat_with_word_distances(rs1, rs2)

        # Verify internal state of object.
        self.assertEqual(r'saw(?:\b\S+)?\s(?:the|a)?', regexString3.get_regex_str())
        match_strs = re.findall(regexString3.get_regex_str(), inputStr)
        expected = ['saw a']
        self.assertEqual(expected, match_strs)

        regexString4 = RegexString(['saddest', 'sad', 'morose'])
        regexString5 = RegexString.concat_with_word_distances(regexString3, regexString4)

        expected = r'saw(?:\b\S+)?\s(?:(?:the|a)(?:\b\S+)?\s)?(?:saddest|morose|sad)'
        self.assertEqual(expected, regexString5.get_regex_str())
        
        match_strs = re.findall(regexString5.get_regex_str(), inputStr)
        expected = ['saw a sad']
        self.assertEqual(expected, match_strs)

        regexString6 = RegexString(['monkey'])
        finalRegexString = RegexString.concat_with_word_distances(regexString5, regexString6)

        # Test the regex.
        expected = r'saw(?:\b\S+)?\s(?:(?:the|a)(?:\b\S+)?\s)?(?:saddest|morose|sad)(?:\b\S+)?\smonkey'
        self.assertEqual(expected, finalRegexString.get_regex_str())

        # Test matching.
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['saw a sad monkey']
        self.assertEqual(expected, match_strs)


    def test_concat_with_word_distances4(self):
        # Run a test that illustrates a basic form of the concat_with_word_distances() functionality.
        # 1) Look for a required 'saw' or 'see'.
        # 2) Look for an optional 'a' or 'the'.
        # 3) Look for a required 'sad' or 'morose'.
        # 4)_Look for a required 'monkey'.
        inputStr = 'I saw a sad monkey. It made me sad to see a morose monkey. '
        inputStr += 'The monkey was the saddest monkey ever seen. '
        inputStr += 'Such a sad, sad monkey.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['saw', 'see'])
        rs2 = RegexString(['a', 'the'], optional=True)
        regexString3 = RegexString.concat_with_word_distances(rs1, rs2)

        # Verify internal state of object.
        self.assertEqual(r'(?:saw|see)(?:\b\S+)?\s(?:the|a)?', regexString3.get_regex_str())
        match_strs = re.findall(regexString3.get_regex_str(), inputStr)
        expected = ['saw a', 'see a']
        self.assertEqual(expected, match_strs)

        regexString4 = RegexString(['saddest', 'sad', 'morose'])
        regexString5 = RegexString.concat_with_word_distances(regexString3, regexString4)

        # Verify internal state of object.
        expected = r'(?:saw|see)(?:\b\S+)?\s(?:(?:the|a)(?:\b\S+)?\s)?(?:saddest|morose|sad)'
        self.assertEqual(expected, regexString5.get_regex_str())
        match_strs = re.findall(regexString5.get_regex_str(), inputStr)
        expected = ['saw a sad', 'see a morose']
        self.assertEqual(expected, match_strs)

        regexString6 = RegexString(['monkey'])
        finalRegexString = RegexString.concat_with_word_distances(regexString5, regexString6)

        # Test the regex.
        expected = r'(?:saw|see)(?:\b\S+)?\s(?:(?:the|a)(?:\b\S+)?\s)?(?:saddest|morose|sad)(?:\b\S+)?\smonkey'
        self.assertEqual(expected, finalRegexString.get_regex_str())

        # Test matching.
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['saw a sad monkey', 'see a morose monkey']
        self.assertEqual(expected, match_strs)


    def test_concat_with_word_distancesMinMax(self):
        # Run a test that verifies concat_with_word_distances() functionality when you specify a min
        # and max number of words.
        inputStr = 'I saw a sad monkey. It made me sad to see a morose monkey. '
        inputStr += 'The monkey was the saddest, loneliest monkey ever seen. '
        inputStr += 'Such a sad, sorrowful monkey.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['sad', 'saddest', 'morose'])
        rs2 = RegexString(['monkey'])

        # Using the default values of 0,0.
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2)
        # Test
        self.assertEqual(r'(?:saddest|morose|sad)(?:\b\S+)?\smonkey', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['sad monkey', 'morose monkey']
        self.assertEqual(expected, match_strs)

        # Using the values of 0,1.
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, max_nbr_words=1)
        # Test
        self.assertEqual(r'(?:saddest|morose|sad)(?:\b\S+)?(?:\s\S+){0,1}\smonkey', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['sad monkey', 'morose monkey', 'saddest, loneliest monkey', 'sad, sorrowful monkey']
        self.assertEqual(expected, match_strs)

        # Using the values of 1,2.
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'(?:saddest|morose|sad)(?:\b\S+)?(?:\s\S+){1,2}\smonkey', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        # Crossing sentence boundaries.
        expected = ['morose monkey. the monkey', 'saddest, loneliest monkey', 'sad, sorrowful monkey']
        self.assertEqual(expected, match_strs)

        # Using the values of 2,3.
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=2, max_nbr_words=3)
        # Test
        self.assertEqual(r'(?:saddest|morose|sad)(?:\b\S+)?(?:\s\S+){2,3}\smonkey', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        # Crossing sentence boundaries.
        expected = ['morose monkey. the monkey']
        self.assertEqual(expected, match_strs)


    def test_concat_with_word_distancesInterveningPunctuation(self):
        # Verify that punctuation immediately after a target word does not block a
        # match which follows.

        # Intervening comma and double quote. 0-word distance.
        inputStr = '"Stick \'em up," yelled the wounded Sheriff.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['up'])
        rs2 = RegexString(['yelled'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2)
        # Test
        self.assertEqual(r'up(?:\b\S+)?\syelled', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up," yelled']
        self.assertEqual(expected, match_strs)

        # Intervening three exclamation points and double quote. 0-word distance.
        inputStr = '"Stick \'em up!!!" yelled the wounded Sheriff.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['up'])
        rs2 = RegexString(['yelled'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2)
        # Test
        self.assertEqual(r'up(?:\b\S+)?\syelled', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up!!!" yelled']
        self.assertEqual(expected, match_strs)

        # Intervening three exclamation points and double quote. 1-2 word distance.
        inputStr = '"Stick \'em up!!!" yelled the wounded Sheriff.'
        inputStr = inputStr.lower()

        # Too little distance.
        rs1 = RegexString(['up'])
        rs2 = RegexString(['yelled'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'up(?:\b\S+)?(?:\s\S+){1,2}\syelled', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = []
        self.assertEqual(expected, match_strs)

        # Just the right distance.
        rs1 = RegexString(['up'])
        rs2 = RegexString(['the'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'up(?:\b\S+)?(?:\s\S+){1,2}\sthe', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up!!!" yelled the']
        self.assertEqual(expected, match_strs)

        rs1 = RegexString(['up'])
        rs2 = RegexString(['wounded'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'up(?:\b\S+)?(?:\s\S+){1,2}\swounded', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up!!!" yelled the wounded']
        self.assertEqual(expected, match_strs)

        # Too much distance.
        rs1 = RegexString(['up'])
        rs2 = RegexString(['sheriff'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'up(?:\b\S+)?(?:\s\S+){1,2}\ssheriff', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = []
        self.assertEqual(expected, match_strs)


    def test_concat_with_word_distancesInterveningPunctuationOptional(self):
        # Verify that punctuation immediately after a target word does not block a
        # match which follows. Differs from previous test in that the first word of the
        # match is optional here.

        # Intervening comma and double quote. 0-word distance.
        inputStr = '"Stick \'em up," yelled the wounded Sheriff.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['up'], optional=True)
        rs2 = RegexString(['yelled'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2)
        # Test
        self.assertEqual(r'(?:(?:up)(?:\b\S+)?\s)?yelled', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up," yelled']
        self.assertEqual(expected, match_strs)

        # Intervening three exclamation points and double quote. 0-word distance.
        inputStr = '"Stick \'em up!!!" yelled the wounded Sheriff.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['up'], optional=True)
        rs2 = RegexString(['yelled'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2)
        # Test
        self.assertEqual(r'(?:(?:up)(?:\b\S+)?\s)?yelled', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up!!!" yelled']
        self.assertEqual(expected, match_strs)


        # Intervening three exclamation points and double quote. 1-2 word distance.
        inputStr = '"Stick \'em up!!!" yelled the wounded Sheriff.'
        inputStr = inputStr.lower()

        # Matches, but too little distance to match on 'up'.
        rs1 = RegexString(['up'], optional=True)
        rs2 = RegexString(['yelled'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'(?:(?:up)(?:\b\S+)?)?(?:\s\S+){1,2}\syelled', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        # Here we're not matching on 'up', but on the 1-2 optional words preceding 'yelled'.
        expected = [' \'em up!!!" yelled']
        self.assertEqual(expected, match_strs)

        # Just the right distance.
        rs1 = RegexString(['up'], optional=True)
        rs2 = RegexString(['wounded'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'(?:(?:up)(?:\b\S+)?)?(?:\s\S+){1,2}\swounded', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up!!!" yelled the wounded']
        self.assertEqual(expected, match_strs)

        rs1 = RegexString(['up'], optional=True)
        rs2 = RegexString(['wounded'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'(?:(?:up)(?:\b\S+)?)?(?:\s\S+){1,2}\swounded', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = ['up!!!" yelled the wounded']
        self.assertEqual(expected, match_strs)

        # Too much distance.
        rs1 = RegexString(['up'], optional=True)
        rs2 = RegexString(['sheriff'])
        finalRegexString = RegexString.concat_with_word_distances(rs1, rs2, min_nbr_words=1, max_nbr_words=2)
        # Test
        self.assertEqual(r'(?:(?:up)(?:\b\S+)?)?(?:\s\S+){1,2}\ssheriff', finalRegexString.get_regex_str())
        match_strs = re.findall(finalRegexString.get_regex_str(), inputStr)
        expected = [' the wounded sheriff']
        self.assertEqual(expected, match_strs)


    def test_concat_with_word_distances_optional_whole_word(self):
        # Test the fix for a bug where concat_with_word_distances() failed
        # if the first word was both optional and whole word.

        color_qualifiers = ['dull']
        color_qualifiers_rs = RegexString(color_qualifiers, 
                                        whole_word=True, 
                                        optional=True)
        colors = ['red']
        colors_rs = RegexString(colors, whole_word=True)

        color_phrase_rs = RegexString.concat_with_word_distances(color_qualifiers_rs, 
                                                                colors_rs,
                                                                min_nbr_words=0, 
                                                                max_nbr_words=0)
        
        input = "dull red"

        # This is where we would get "re.error: unbalanced parenthesis at position 39"
        matchStrs = color_phrase_rs.get_match_triples(input)
        self.assertEqual([('dull red', 0, 8)], matchStrs)

        # Verify the whole_word requirement.
        matchStrs = color_phrase_rs.get_match_triples("udull red")
        self.assertEqual([('red', 6, 9)], matchStrs)

        # Now turn off whole_word and verify it is turned off.
        color_qualifiers_rs = RegexString(color_qualifiers, 
                                        # whole_word=True, 
                                        optional=True)
        color_phrase_rs = RegexString.concat_with_word_distances(color_qualifiers_rs, 
                                                                colors_rs,
                                                                min_nbr_words=0, 
                                                                max_nbr_words=0)
        matchStrs = color_phrase_rs.get_match_triples("udull red")
        self.assertEqual([('dull red', 1, 9)], matchStrs)



    def testConcatNoCollection(self):
        # Test concat() with two RegexString objects, the first one Non-OR'd and 
        # optional.
        # 1) Look for an optional 'a monkey'.
        # 2) Look for a required period.
        inputStr = 'I saw a monkey. The monkey was sad. It made me sad to see a sad monkey.'
        inputStr = inputStr.lower()

        rs1 = RegexString(['a monkey'], optional=True)
        rs2 = RegexString(['\.'])
        regexString3 = RegexString.concat(rs1, rs2)

        # Test the regex.
        expected = r'(?:a monkey)?\.'
        self.assertEqual(expected, str(regexString3))

        # Test matching.
        match_strs = re.findall(regexString3.get_regex_str(), inputStr)
        expected = ['a monkey.', '.', '.']
        self.assertEqual(expected, match_strs)

    def testConcatWithCollection(self):
        # Test concat() with two RegexString objects, the first an OR'd, optional 
        # collection.
        # 1) Look for an optional 'a monkey', 'the monkey', or 'a sad monkey'.
        # 2) Look for a required period.
        inputStr = 'I saw a monkey. The monkey was sad. It made me sad to see a sad monkey.'
        inputStr = inputStr.lower()

        monkeyStrings = ['a monkey', 'the monkey', 'a sad monkey']
        rs1 = RegexString(monkeyStrings, optional=True)

        rs2 = RegexString(['\.'])
        regexString3 = RegexString.concat(rs1, rs2)

        # Test the regex.
        expected = r'(?:a sad monkey|the monkey|a monkey)?\.'
        self.assertEqual(expected, str(regexString3))

        # Test matching.
        match_strs = re.findall(regexString3.get_regex_str(), inputStr)
        expected = ['a monkey.', '.', 'a sad monkey.']
        self.assertEqual(expected, match_strs)


    def testConcatWithCollectionSpaceOptional(self):
        # Test concat() with two RegexString objects, the first an OR'd, optional 
        # collection.
        # 1) Look for an optional 'a monkey', 'the monkey', or 'a sad monkey'.
        # 2) Look for an optional space character.
        # 3) Look for a required period.
        
        # Note the whitespace between 'monkey' and the period in the first sentence.
        inputStr = 'I saw a monkey . The monkey was sad. It made me sad to see a sad monkey.'
        inputStr = inputStr.lower()

        monkeyStrings = ['a monkey', 'the monkey', 'a sad monkey']
        rs1 = RegexString(monkeyStrings, optional=True)

        rs2 = RegexString(['\.'])
        
        # First try concat() with the insert_opt_ws set to its default of False.
        regexString3 = RegexString.concat(rs1, rs2)

        # Test the regex.
        expected = r'(?:a sad monkey|the monkey|a monkey)?\.'
        self.assertEqual(expected, str(regexString3))

        # Test matching.
        match_strs = re.findall(regexString3.get_regex_str(), inputStr)
        expected = ['.', '.', 'a sad monkey.']
        self.assertEqual(expected, match_strs)

        # First try concat() with the insert_opt_ws set True.
        regexString3 = RegexString.concat(rs1, rs2, insert_opt_ws=True)

        # Test the regex.
        expected = r'(?:a sad monkey|the monkey|a monkey)?(?:\s)?\.'
        self.assertEqual(expected, str(regexString3))

        # Test matching.
        match_strs = re.findall(regexString3.get_regex_str(), inputStr)
        expected = ['a monkey .', '.', 'a sad monkey.']
        self.assertEqual(expected, match_strs)

