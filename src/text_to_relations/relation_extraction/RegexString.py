"""
RegexString: a wrapper around regular expressions for building and combining patterns.
"""
import re

from typing import List, Tuple, Union, cast

class RegexString:
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
            match_strs (List[str]): a collection of plain strings to match
                literally; if there is more than one element, each element is
                OR'd together. Items are automatically escaped via re.escape(),
                so regex metacharacters (e.g. '(', '[', '.') are treated as
                literals. Use prepend/append or concat() for regex syntax.
                If you need to use regex metacharacters directly in a pattern
                (e.g. '\d+'), use from_regex() instead.
                For case-insensitive matching, lowercase all items here and
                also lowercase the input string before calling
                get_match_triples().
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
            if r'\b' in self.append:
                msg += f"'append'. append = '{self.append}'."
                raise ValueError(msg)

        self.regex_str = self.set_regex()


    def set_regex(self):
        """
        Build and return the regex string from this object's properties.

        Combines match_strs (escaped), optional, non_capturing, whole_word,
        prepend, and append into a single regex pattern string. Called once
        during __init__; result is stored in self.regex_str.

        Returns:
            str: the compiled regex pattern string.
        """
        result = ''

        if self.prepend != '':
            result += self.prepend

        if len(self.match_strs) > 1:
            # OR the match_strs together
            result += '('
            if self.non_capturing:
                result += '?:'

            for item in self.match_strs:
                result += re.escape(item) + '|'
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
                result += re.escape(self.match_strs[0])
                result += ')?'
            else:
                # The item is required.
                result += re.escape(self.match_strs[0])
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

    def get_match_triples(self, text: str, case_insensitive: bool = False) -> List[Tuple]:
        """
        Run re.finditer() on this regex.
        Note that this function is likely to fail if you have created any
        RegexString objects where non-group capturing is False.

        Args:
            text (str): text to run re.finditer() against.
            case_insensitive (bool): if True, matching ignores case and the
                matched text in each triple preserves the original casing of
                the input string. Defaults to False.
        Returns:
            List[Tuple]: a list of (text-matched, start-offset, end-offset)
            triples.
        """
        flags = re.IGNORECASE if case_insensitive else 0
        match_triples = [(m.group(), m.start(), m.end())
                         for m in re.finditer(self.get_regex_str(), text, flags)]
        return match_triples

    @staticmethod
    def concat(rs1: 'RegexString',
               rs2: 'RegexString',
               insert_opt_ws: bool=False) -> 'RegexString':
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
            join_str_regex = r'(?:\s)?'
        else:
            join_str_regex = ''  # In other words, no whitespace allowed.

        # Create an empty/invalid RegexString object, and make it valid by editing
        # its regex_str property.
        result_regex_string = RegexString([''])
        result_regex_string.regex_str = rs1.regex_str + join_str_regex + rs2.regex_str

        if rs2.optional:
            result_regex_string.optional = True
        else:
            result_regex_string.optional = False

        return result_regex_string


    @staticmethod
    def concat_with_word_distances(rs1: 'RegexString',
                                   rs2: 'RegexString',
                                   min_nbr_words: int=0,
                                   max_nbr_words: int=0) -> 'RegexString':
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
            rs1 (RegexString): the left-hand RegexString to concatenate.
            rs2 (RegexString): the right-hand RegexString to concatenate.
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
        word_regex = r'\s\S+'
        ready_for_distance_range_word_regex = r'(?:' + word_regex + ')'

        intervening_punc = r'(?:\b\S+)?'
        intervening_punc_and_space = intervening_punc + r'\s'

        # Check input parameters.
        if not isinstance(rs1, RegexString):
            raise ValueError("rs1 parameter must be a RegexString object.")
        if not isinstance(rs2, RegexString):
            raise ValueError("rs2 parameter must be a RegexString object.")

        if min_nbr_words > max_nbr_words:
            raise ValueError("min_nbr_words cannot be greater than max_nbr_words.")

        # Set min/max word distance.
        word_distance_regex = '{' + str(min_nbr_words) + ',' + str(max_nbr_words) + '}'

        if rs1.optional:
            ending_paren_pos = -1
            if rs1.whole_word:
                # Things get a little messy if both rs1.optional and rs1.whole_word.
                ending_paren_pos = -3
                # We don't have to worry about the \b for rs1 because
                # `intervening_punc_and_space` contains a \b.

            # (Assuming that it ends in '?'.)
            # Find the left parens which the last '?' pertains to
            left_paren_idx = rs1.get_regex_str().rfind('(')

            if min_nbr_words == 0 and max_nbr_words == 0:
                first_part = rs1.get_regex_str()[0:left_paren_idx] + \
                            '(?:' + rs1.get_regex_str()[left_paren_idx : ending_paren_pos] + \
                            intervening_punc_and_space + \
                            ')?'
                join_str_regex = ''
            else:
                first_part = rs1.get_regex_str()[0:left_paren_idx] + \
                            '(?:' + rs1.get_regex_str()[left_paren_idx:ending_paren_pos] + \
                            intervening_punc + ')?'
                join_str_regex = ready_for_distance_range_word_regex + word_distance_regex + r'\s'
        else:
            first_part = rs1.get_regex_str() + intervening_punc

            if min_nbr_words == 0 and max_nbr_words == 0:
                join_str_regex = r'\s'
            else:
                join_str_regex = ready_for_distance_range_word_regex + word_distance_regex + r'\s'


        # Create an empty/invalid RegexString object, and make it valid by editing
        # its regex_str property.
        result_regex_string = RegexString([''])
        result_regex_string.regex_str = first_part + join_str_regex + rs2.regex_str

        if rs2.optional:
            result_regex_string.optional = True
        else:
            result_regex_string.optional = False

        return result_regex_string


    @staticmethod
    def from_regex(regex: str) -> 'RegexString':
        """
        Build a RegexString object from a hand-written regular expression.

        Use this when the normal RegexString constructor cannot express the
        pattern you need. Two common cases:

        1. Your pattern contains regex metacharacters. The constructor escapes
           all match strings via re.escape(), so passing '\d+' would match the
           literal string '\d+', not digits. Use from_regex() instead:

               number_rs = RegexString.from_regex(r'(\d+)')

        2. You need to OR two already-built RegexString objects together:

               rs = RegexString.from_regex(
                   f'(?:{rs1.get_regex_str()}|{rs2.get_regex_str()})')

        The returned object is safe to use with:
        - get_regex_str()
        - get_match_triples()
        - as a value in the regex_patterns dict passed to SimpleExtractionPhase

        All of the above only consult the underlying regex string.

        Warning: do not pass the returned object into concat() or
        concat_with_word_distances(). Those methods read the object's
        attributes (optional, whole_word) to make structural decisions about
        the regex string. Because from_regex() cannot derive those attributes
        from the hand-written regex, they could be wrong, and the concat
        methods could produce incorrect results.

        Not applicable: build_regex_string() constructs its own RegexString
        objects internally and does not accept a RegexString as input, so it
        is neither safe nor unsafe — it simply cannot be called with a
        from_regex() object.

        Args:
            regex (str): a regular expression string.

        Returns:
            RegexString:
        """
        # Create an empty/invalid RegexString object, and make it valid by editing
        # its regex_str property.
        result = RegexString([''])
        result.regex_str = regex
        return result


    @staticmethod
    def build_regex_string(input_list: List[Union[List[str], int]]) -> 'RegexString':
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

        final_regex_str = None
        curr_regex_str = RegexString(cast(List[str], input_list[0]))
        curr_max_distance = cast(int, input_list[1])
        idx = 2
        while idx < len(input_list):
            next_regex_str = RegexString(cast(List[str], input_list[idx]))
            final_regex_str = RegexString.concat_with_word_distances(
                curr_regex_str, next_regex_str, max_nbr_words=curr_max_distance)
            if idx + 2 < len(input_list):
                curr_regex_str = final_regex_str
                curr_max_distance = cast(int, input_list[idx+1])
                idx += 2
            else:
                idx += 1

        assert final_regex_str is not None
        return final_regex_str


    def __repr__(self):
        return self.regex_str


    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self is other:
            return True
        if self.get_regex_str() == other.get_regex_str():
            return True
        return False


if __name__ == '__main__':
    import inspect

    # Stamp descriptions from https://www.mysticstamp.com/.

    input_text = \
    """
    # 11A - 1853-55 3¢ George Washington, dull red, type II, imperf

    # 17 - 1851 12c Washington imperforate, black

    # 12 - 1856 5c Jefferson, red brown, type I, imperforate

    # 18 - 1861 1c Franklin, type I, perf 15

    # 40 - 1875 1c Franklin, bright blue

    # 42 - 1875 5c Jefferson, orange brown

    # 62B - 1861 10c Washington, dark green
    """
    input_text = inspect.cleandoc(input_text)

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
    results = type_phrase_rs.get_match_triples(input_text)
    print("\nType info found in the input:")
    print(results)

    cent_symbols = ['c', '¢']
    # Use `prepend` to look for one or two digits before the cent symbol.
    cent_rs = RegexString(cent_symbols, prepend=r'\d\d?')
    print(f"\nRegular expression for 'cent_rs': {cent_rs.get_regex_str()}")
    results = cent_rs.get_match_triples(input_text)
    print("\nCents info found in the input:")
    print(results)

    perforation_markers = ['perf', 'imperforate', 'imperf']
    perforations_rs = RegexString(perforation_markers)
    results = perforations_rs.get_match_triples(input_text)
    print("\nPerforation info:")
    print(results)

    # But if the stamp is perforated we want to also extract the number which follows.
    imperforated_markers = ['imperforate', 'imperf']
    imperf_rs = RegexString(imperforated_markers)
    results = imperf_rs.get_match_triples(input_text)
    print("\nImperforated:")
    print(results)

    perforation_markers = ['perf']
    perf_rs = RegexString(perforation_markers, append=r' \d\d')
    results = perf_rs.get_match_triples(input_text)
    print("\nPerforated sizes:")
    print(results)

    colors = ['black', 'blue', 'brown', 'green', 'orange', 'red']

    colors_rs = RegexString(colors, whole_word=True)
    results = colors_rs.get_match_triples(input_text)
    print("\nColors alone:")
    print(results)

    # Create the qualifiers.
    # Add colors to the qualifiers, so that we can ID, e.g. 'orange brown'.
    color_qualifiers = ['bright', 'dark', 'dull'] + colors

    color_input_list: List[Union[List[str], int]] = [color_qualifiers, 0, colors]
    color_phrase_rs = RegexString.build_regex_string(color_input_list)
    results = color_phrase_rs.get_match_triples(input_text)
    print("\nColor qualifiers + colors:")
    print(results)

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
    results = color_phrase_rs.get_match_triples(input_text)
    print("\nOptional color qualifiers + colors found in the input:")
    print(results)


    id_symbols = ['#']

    id_rs = RegexString(id_symbols, append=r'\s\d+')
    results = id_rs.get_match_triples(input_text)
    print("\nStamp IDs:")
    print(results)

    # Not getting the optional letter.
    id_rs = RegexString(id_symbols, append=r'\s\d+(?:\w+)?')
    results = id_rs.get_match_triples(input_text)
    print("\nStamp IDs with letters found in the input:")
    print(results)
