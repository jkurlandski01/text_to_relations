from text_to_relations.relation_extraction import StringUtils
from text_to_relations.relation_extraction import SpacyUtils
from text_to_relations.relation_extraction.Annotation import Annotation
from typing import Tuple, List, Self

class TokenAnn(Annotation):
    # A class of objects representing word tokens which "know" their 
    # starting and ending offsets in a source document. 
    
    # Contractions and the possessive 's are considered word tokens despite the apostrophe punctuation 
    # which they contain.
    kindExceptions = ["'s", "'ve", "'d", "'ll", "n't"]

    def __init__(self, start_offset, end_offset, contents):
        """"""
        if contents in TokenAnn.kindExceptions:
            kind = 'word'
        elif StringUtils.isAllPunc(contents):
            kind = 'punc'
        elif StringUtils.isAllWordChars(contents):
            kind = 'word'
        else: 
            kind = 'other'
        
        features = {'kind': kind}
        super().__init__('Token', contents, start_offset, end_offset, features)


    @staticmethod
    def build_annotation_distance_regex(first_ann: Annotation, 
                                        word_distance_range: Tuple[int, int], 
                                        token_kind: str, 
                                        second_ann: Annotation) -> str:
        """
        Build a string regular expression that specifies the token distance between two annotations
        necessary for a match.

        Args:
            first_ann (Annotation): 
            word_distance_range (Tuple[int, int]): a pair of integers, whose first element is a minimum token distance
        and whose second element is a maximum token distance 
            token_kind (str): the Token.kind property necessary for a match; None if all Token objects
        are to match
            second_ann (Annotation): 

        Returns:
            str: a regular expression
        """
        """
        :param first_ann: 
        :param word_distance_range: 
        :param token_kind: 
        :param second_ann: 
        :return: 
        """
        distanceToken = 'Token'

        result = r"<'"
        result += first_ann
        result += r"[^>]*>(?:<'"
        result += distanceToken

        if token_kind is None:
            result += r"[^>]*>){"
        else:
            result += r"'[^>]*kind='"
            result += token_kind
            result += r"'[^>]*>){"

        minTs, maxTs = word_distance_range
        result += str(minTs) + ',' + str(maxTs)
        result += r"}<'"
        result += second_ann
        result += r"[^>]*>"

        return result


    @staticmethod
    def get_token_objects(input_str: str, 
                          start_pos_in_doc: int) -> List[Self]:
        """
        Create TokenAnn objects on the given substring of a longer document.
        Args:
            input_str (str): a substring of some document
            start_pos_in_doc (int): the starting offset of inputStr in the 
                source document

        Returns:
            List[Self]: a list of TokenAnn objects
        """
        result = []

        # This is how we track the starting and ending position of each token. 
        # For each token, we find the first instance in this string--and use
        # that to determine the starting position. We replace the found substring
        # with x's to avoid the problem of repeating tokens.
        consumedStr = input_str

        tokenStrs = SpacyUtils.tokenize(input_str)

        # lastPos = 0
        for tokenStr in tokenStrs:
            startPosInInput = consumedStr.index(tokenStr)
            xStr = 'x' * len(tokenStr)
            consumedStr = consumedStr.replace(tokenStr, xStr, 1)
            endPosInInput = startPosInInput + len(tokenStr)
            token = TokenAnn(start_pos_in_doc + startPosInInput, start_pos_in_doc + endPosInInput, tokenStr)
            result.append(token)

        return result
    
    
    @staticmethod
    def text_to_token_anns(text_input: str) -> List[Self]:
        """
        Split the given input text into tokens, and create a TokenAnn
        on each one.

        Args:
            text_input (str): 

        Returns:
            List[Self]: a list of TokenAnn annotations created on the given text
        """
        tokenStrs = SpacyUtils.tokenize(text_input)

        result = []
        startSearchIdx = 0
        for token in tokenStrs:
            startIdx = text_input.find(token, startSearchIdx)
            endIdx = startIdx + len(token)
            tokenAnn = TokenAnn(startIdx, endIdx, token.strip())
            result.append(tokenAnn)
            startSearchIdx = endIdx

        return result


if __name__ == '__main__':
    pass
