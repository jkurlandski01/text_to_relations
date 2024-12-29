import re

from typing import List, Tuple, Self

class RegexString(object):
    """
    A class wrapped around a regular expression, offering functionality
    to create, concatenate and construct complex regex strings via an
    easy-to-use set of functions.
    """

    def __init__(self, match_strs: List[str], 
                 whole_word: bool=False,
                 optional: bool=False, 
                 non_capturing: bool=True,
                 prepend: str='', append: str=''):
        """

        Args:
            match_strs (List[str]): a collection of strings; if there 
                is more than one element, each element is to be OR'd together 
                for a match; if only one element, then there is no OR'd group
            whole_word (bool, optional): whether or not to require a match on
                whole words only. Defaults to True.
            optional (bool, optional): whether or not the OR'd items in the 
                regex should be optional. Defaults to False.
            non_capturing (bool, optional): if True, the OR'd items should 
                form a non-capturing group (i.e., '?:' should be inserted 
                after the left parenthesis). Note that other RegexString functions,
                such as get_match_triples() may behave unexpectedly if this
                is set to False. Defaults to True.
            prepend (str, optional): regex string to prepend to the OR'd list. 
                Defaults to ''.
            append (str, optional): regex string to append to the OR'd list. 
                Defaults to ''.
        """
        # If match_strs is a string, the user has made an error.
        if isinstance(match_strs, str):
            raise ValueError("match_strs parameter must be a list. You passed in a string.")

        # If passed a list of regex's re.findall() will take the first match found
        # even if a longer match is possible. E.g. if `text` contains "18" and we call
        # re.findall("(1|18)", text), only "1" will be found. Here we fix this
        # by sorting on string length descending on all strings, not bothering to
        # first check whether they are substrings.
        match_strs.sort(key=len, reverse=True)
        self.match_strs = match_strs

        self.whole_word = whole_word
        self.optional = optional
        self.non_capturing = non_capturing

        # '\b' causes debugging issues because in print statements it 
        # is invisible because it is interpreted as backspace. We don't 
        # attempt to fix this if '\b' is just a substring of a longer
        # prepend or append.
        esc_backslash_b = r'\b'
        if prepend == '\b':
            prepend = esc_backslash_b
        if append == '\b':
            append = esc_backslash_b
        self.prepend = prepend
        self.append = append

        if self.whole_word:
            msg = "Do not use 'whole_word=True' with '\\b' in "
            if r'\b' in self.prepend:
                msg += f"'prepend'. prepend = '{self.prepend}'."
                raise ValueError(msg)
            elif r'\b' in self.append:
                msg += f"'append'. append = '{self.append}'."
                raise ValueError(msg)

        self.regex_str = self.set_regex()


    def set_regex(self):
        result = ''

        if self.prepend != '':
            result += self.prepend

        if len(self.match_strs) > 1:
            # OR the match_strs together
            result += '('
            if self.non_capturing:
                result += '?:'

            for item in self.match_strs:
                result += item + '|'
            # Remove last pipe.
            result = result[0:-1]

            result += ')'

            if self.optional:
                result += '?'
        else:
            # There is only one item to put into the regex.
            if self.optional:
                # Make the item optional.
                result += '('
                if self.non_capturing:
                    result += '?:'
                result += self.match_strs[0]
                result += ')?'
            else:
                # The item is required.
                result += self.match_strs[0]
                if not self.non_capturing:
                    result = '(' + result + ')'

        if self.whole_word:
            result = r'\b' + result + r'\b'

        if self.append != '':
            result += self.append

        return result

    def get_regex_str(self):
        """
        Return the regular expression for this object's properties.
        :return:
        """
        return self.regex_str
    
    def get_match_triples(self, input: str) -> List[Tuple]:
        """
        Run re.finditer() on this regex.
        Note that this function is likely to fail if you have created any RegexString objects where non-group capturing is False.
        
        Args:
            input (str): text to run re.finditer() against.
        Returns:
            List[Tuple]: a list of (text-matched, start-offset, end-offset)
            triples.
        """
        match_triples = [(m.group(), m.start(), m.end()) for m in re.finditer(self.get_regex_str(), input)]
        return match_triples

    @staticmethod
    def concat(rs1: Self, 
               rs2: Self, 
               insert_opt_ws: bool=False) -> Self:
        """
        Create a new RegexString by concatenating the two input RegexString objects.
        Note: This method does not allow words between the two regex's. To
        allow words, use concat_with_word_distances().

        Args:
            rs1 (RegexString): 
            rs2 (RegexString): 
            insert_opt_ws (bool, optional): if True, allow a single whitespace 
            character between the regex expressions. Defaults to False.

        Raises:
            ValueError: if parameters are not RegexStings
        Returns:
            RegexString: the new RegexString
        """
        if not isinstance(rs1, RegexString):
            raise ValueError("rs1 parameter must be a RegexString object.")
        if not isinstance(rs2, RegexString):
            raise ValueError("rs2 parameter must be a RegexString object.")

        if insert_opt_ws:
            joinStrRegex = r'(?:\s)?'
        else:
            joinStrRegex = ''  # In other words, no whitespace allowed.

        # Create an empty/invalid RegexString object, and make it valid by editing
        # its regex_str property.
        resultRegexString = RegexString([''])
        resultRegexString.regex_str = rs1.regex_str + joinStrRegex + rs2.regex_str

        if rs2.optional:
            resultRegexString.optional = True
        else:
            resultRegexString.optional = False

        return resultRegexString


    @staticmethod
    def concat_with_word_distances(rs1: Self, 
                                   rs2: Self,  
                                   min_nbr_words: int=0, 
                                   max_nbr_words: int=0) -> Self:
        """
        Create a new RegexString by concatenating the two input 
        RegexString objects with a minimum and maximum number of 
        non-whitespace-character strings between them. Note that, 
        in this implementation, all of these strings are considered 
        single words: 'John', 'John:', '("John.")'.
        Note:
        - This functionality assumes that the input text does not have 
        spurious or accidental consecutive whitespace. In other words, if 
        the input text has 'a  dog' and you are looking for 'a' followed by 
        'dog', no match will occur because of the double spaces.

        Args:
            rs1 (RegexString): _description_
            rs2 (RegexString): _description_
            min_nbr_words (int, optional): the minimum number of words 
                allowed between the 
            two regex expressions. Defaults to 0.
            max_nbr_words (int, optional): the maximum number of words 
                allowed between the two regex expressions. Defaults to 0.
        Raises:
            ValueError: if parameters are not RegexStings
            ValueError: if min_nbr_words > max_nbr_words
        Returns:
            RegexString: the new RegexString
        """
        # Constants.
        wordRegex = r'\s\S+'
        readyForDistanceRangeWordRegex = r'(?:' + wordRegex + ')'

        interveningPunc = r'(?:\b\S+)?'
        interveningPuncAndSpace = interveningPunc + '\s'

        # Check input parameters.
        if not isinstance(rs1, RegexString):
            raise ValueError("rs1 parameter must be a RegexString object.")
        if not isinstance(rs2, RegexString):
            raise ValueError("rs2 parameter must be a RegexString object.")

        if min_nbr_words > max_nbr_words:
            raise ValueError("min_nbr_words cannot be greater than max_nbr_words.")

        # Set min/max word distance.
        wordDistanceRegex = '{' + str(min_nbr_words) + ',' + str(max_nbr_words) + '}'

        if rs1.optional:
            ending_paren_pos = -1
            if rs1.whole_word:
                # Things get a little messy if both rs1.optional and rs1.whole_word.
                ending_paren_pos = -3
                # We don't have to worry about the \b for rs1 because
                # `interveningPuncAndSpace` contains a \b.

            # (Assuming that it ends in '?'.)
            # Find the left parens which the last '?' pertains to
            leftParenIdx = rs1.get_regex_str().rfind('(')

            if min_nbr_words == 0 and max_nbr_words == 0:
                firstPart = rs1.get_regex_str()[0:leftParenIdx] + \
                            '(?:' + rs1.get_regex_str()[leftParenIdx : ending_paren_pos] + \
                            interveningPuncAndSpace + \
                            ')?'
                joinStrRegex = ''
            else:
                # Not sure about this
                firstPart = rs1.get_regex_str()[0:leftParenIdx] + \
                            '(?:' + rs1.get_regex_str()[leftParenIdx:-1] + \
                            interveningPunc + ')?'
                joinStrRegex = readyForDistanceRangeWordRegex + wordDistanceRegex + '\s'
        else:
            firstPart = rs1.get_regex_str() + interveningPunc

            if min_nbr_words == 0 and max_nbr_words == 0:
                joinStrRegex = '\s'
            else:
                joinStrRegex = readyForDistanceRangeWordRegex + wordDistanceRegex + '\s'


        # Create an empty/invalid RegexString object, and make it valid by editing
        # its regex_str property.
        resultRegexString = RegexString([''])
        resultRegexString.regex_str = firstPart + joinStrRegex + rs2.regex_str

        if rs2.optional:
            resultRegexString.optional = True
        else:
            resultRegexString.optional = False

        return resultRegexString


    @staticmethod
    def regex_to_RegexString(regex: str) -> 'RegexString':
        """
        Build a RegexString object from the given regular
        expression.
        Args:
            regex (str): 

        Returns:
            RegexString: 
        """
        # Create an empty/invalid RegexString object, and make it valid by editing
        # its regex_str property.
        result = RegexString([''])
        result.regex_str = regex
        return result


    @staticmethod
    def build_regex_string(input_list: List[str]) -> Self:
        """
        Read the input list to create a new RegexString object from 
        the concatenated elements.

        Args:
            input_list (List[str]): a list having an odd number of elements 
            following the pattern "phraseList1, maxDistance1, phraseList2, 
            maxDistance2, phraseList3, ...", each phraseList consisting of a 
            list of strings and each distance consisting of an integer >= 0;
            each phraseList will be used to create a new RegexString object, 
            after which each RegexString distance RegexString triple will be 
            concatenated to create another set of RegexString objects

        Raises:
            ValueError: if the input list has an invalid number of elements

        Returns:
            RegexString: a single RegexString object concatenating all the 
                list items
        """
        if len(input_list) < 3 or len(input_list) % 2 == 0:
            msg = "Input parameter list must have an odd number of elements "
            msg += "following this pattern:\n"
            msg += "   'phraseList1, maxDistance1, phraseList2, maxDistance2, "
            msg += "phraseList3, ...'"
            raise ValueError(msg)

        finalRegexStr = None
        currRegexStr = RegexString(input_list[0])
        currMaxDistance = input_list[1]
        idx = 2
        while idx < len(input_list):
            nextRegexStr = RegexString(input_list[idx])
            finalRegexStr = RegexString.concat_with_word_distances(currRegexStr, 
                                                                   nextRegexStr, 
                                                                   max_nbr_words=currMaxDistance)
            if idx + 2 < len(input_list):
                currRegexStr = finalRegexStr
                currMaxDistance = input_list[idx+1]
                idx += 2
            else:
                idx += 1

        return finalRegexStr


    def __repr__(self):
        return self.regex_str


    def __eq__(self, other):
        if type(self) != type(other):
            return False
        elif self is other:
            return True
        elif self.get_regex_str() == other.get_regex_str():
            return True
        return False


if __name__ == '__main__':
    import inspect

    # Stamp descriptions from https://www.mysticstamp.com/.

    input = \
    """
    # 11A - 1853-55 3¢ George Washington, dull red, type II, imperf

    # 17 - 1851 12c Washington imperforate, black

    # 12 - 1856 5c Jefferson, red brown, type I, imperforate

    # 18 - 1861 1c Franklin, type I, perf 15

    # 40 - 1875 1c Franklin, bright blue

    # 42 - 1875 5c Jefferson, orange brown

    # 62B - 1861 10c Washington, dark green
    """
    input = inspect.cleandoc(input)

    type_markers = ['type', 'Type']
    type_rs = RegexString(type_markers, whole_word=True)
    print(f"Regular expression for 'type_rs': {type_rs.get_regex_str()}\n")

    roman_numerals = ['I', 'II', 'III', 'IV', 'V']
    roman_nums_rs = RegexString(roman_numerals, whole_word=True)
    print(f"Regular expression for 'roman_nums_rs': {roman_nums_rs.get_regex_str()}")

    type_phrase_rs = RegexString.concat_with_word_distances(type_rs, 
                                                            roman_nums_rs,
                                                            min_nbr_words=0, 
                                                            max_nbr_words=0)
    matchStrs = type_phrase_rs.get_match_triples(input)
    print("\nType info found in the input:")
    print(matchStrs)

    cent_symbols = ['c', '¢']
    # Use `prepend` to look for one or two digits before the cent symbol.
    cent_rs = RegexString(cent_symbols, prepend='\d\d?')
    print(f"\nRegular expression for 'cent_rs': {cent_rs.get_regex_str()}")
    matchStrs = cent_rs.get_match_triples(input)
    print("\nCents info found in the input:")
    print(matchStrs)

    perforation_markers = ['perf', 'imperforate', 'imperf']
    perforations_rs = RegexString(perforation_markers)
    matchStrs = perforations_rs.get_match_triples(input)
    print("\nPerforation info:")
    print(matchStrs)

    # But if the stamp is perforated we want to also extract the number which follows.
    imperforated_markers = ['imperforate', 'imperf']
    imperf_rs = RegexString(imperforated_markers)
    matchStrs = imperf_rs.get_match_triples(input)
    print("\nImperforated:")
    print(matchStrs)

    perforation_markers = ['perf']
    perf_rs = RegexString(perforation_markers, append=' \d\d')
    matchStrs = perf_rs.get_match_triples(input)
    print("\nPerforated sizes:")
    print(matchStrs)

    colors = ['black', 'blue', 'brown', 'green', 'orange', 'red']

    colors_rs = RegexString(colors, whole_word=True)
    matchStrs = colors_rs.get_match_triples(input)
    print("\nColors alone:")
    print(matchStrs)

    # Create the qualifiers.
    # Add colors to the qualifiers, so that we can ID, e.g. 'orange brown'.
    color_qualifiers = ['bright', 'dark', 'dull'] + colors

    inputList = [color_qualifiers, 0, colors]
    color_phrase_rs = RegexString.build_regex_string(inputList)
    matchStrs = color_phrase_rs.get_match_triples(input)
    print("\nColor qualifiers + colors:")
    print(matchStrs)

    # Not getting the colors not preceded by a qualifier.
    # Make the qualifier optional.
    color_qualifiers_rs = RegexString(color_qualifiers, 
                                      whole_word=True, 
                                      optional=True
                                    )
    color_phrase_rs = RegexString.concat_with_word_distances(color_qualifiers_rs, 
                                                            colors_rs,
                                                            min_nbr_words=0, 
                                                            max_nbr_words=0)
    matchStrs = color_phrase_rs.get_match_triples(input)
    print("\nOptional color qualifiers + colors found in the input:")
    print(matchStrs)


    id_symbols = ['#']

    id_rs = RegexString(id_symbols, append='\s\d+')
    matchStrs = id_rs.get_match_triples(input)
    print("\nStamp IDs:")
    print(matchStrs)

    # Not getting the optional letter.
    id_rs = RegexString(id_symbols, append='\s\d+(?:\w+)?')
    matchStrs = id_rs.get_match_triples(input)
    print("\nStamp IDs with letters found in the input:")
    print(matchStrs)
