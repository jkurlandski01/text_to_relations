from typing import Tuple, List, Union, Optional

from text_to_relations.relation_extraction import StringUtils
from text_to_relations.relation_extraction import SpacyUtils
from text_to_relations.relation_extraction.Annotation import Annotation


class TokenAnn(Annotation):
    """A class of objects representing word tokens which "know" their
    starting and ending offsets in a source document."""

    # Contractions and the possessive 's are considered word tokens despite the
    # apostrophe punctuation which they contain.
    kindExceptions = ["'s", "'ve", "'d", "'ll", "n't"]

    def __init__(self, start_offset, end_offset, contents):
        if contents in TokenAnn.kindExceptions:
            kind = 'word'
        elif StringUtils.is_all_punc(contents):
            kind = 'punc'
        elif StringUtils.is_all_word_chars(contents):
            kind = 'word'
        else:
            kind = 'other'

        features = {'kind': kind}
        super().__init__('Token', contents, start_offset, end_offset, features)


    @staticmethod
    def build_annotation_distance_regex(first_ann: Union[str, Annotation],
                                        word_distance_range: Tuple[int, int],
                                        token_type: Optional[str],
                                        second_ann: Union[str, Annotation]) -> str:
        """
        Build a string regular expression that specifies the token distance between two annotations
        necessary for a match.

        The gap quantifier is non-greedy, so the regex matches the shortest possible span between
        first_ann and second_ann. This prevents gap annotations of the same type as second_ann from
        being consumed as gap items instead of serving as the endpoint.

        Args:
            first_ann (Annotation):
            word_distance_range (Tuple[int, int]): a pair of integers, whose first element is a
        minimum token distance and whose second element is a maximum token distance
            token_type (str): the Token.kind property necessary for a match; None to allow any
        annotation type in the gap
            second_ann (Annotation):

        Returns:
            str: a regular expression
        """
        result = r"<'"
        result += str(first_ann)

        if token_type is None:
            result += r"[^>]*>(?:<'[^>]*>){"          # fix: any annotation type in gap
        else:
            result += r"[^>]*>(?:<'Token'[^>]*kind='"
            result += token_type
            result += r"'[^>]*>){"

        min_ts, max_ts = word_distance_range
        result += str(min_ts) + ',' + str(max_ts)
        result += r"}?<'"
        result += str(second_ann)
        result += r"[^>]*>"

        return result


    @staticmethod
    def get_token_objects(input_str: str,
                          start_pos_in_doc: int) -> List['TokenAnn']:
        """
        Tokenize a substring of a larger document, returning TokenAnn objects
        whose offsets are relative to the full document rather than the substring.

        Use this instead of text_to_token_anns when input_str is a slice of a
        longer document and the caller needs offsets that are valid in that
        document. start_pos_in_doc is added to each token's local offset to
        produce the document-level position.

        Args:
            input_str (str): a substring of some document
            start_pos_in_doc (int): character offset of input_str within the
                source document; added to each token's local offset

        Returns:
            List['TokenAnn']: TokenAnn objects with offsets relative to the
                source document
        """
        result = []
        token_strs = SpacyUtils.tokenize(input_str)
        start_search_idx = 0
        for token_str in token_strs:
            start_pos_in_input = input_str.find(token_str, start_search_idx)
            end_pos_in_input = start_pos_in_input + len(token_str)
            start_search_idx = end_pos_in_input
            token = TokenAnn(start_pos_in_doc + start_pos_in_input,
                             start_pos_in_doc + end_pos_in_input, token_str)
            result.append(token)

        return result


    @staticmethod
    def text_to_token_anns(text_input: str) -> List['TokenAnn']:
        """
        Split the given input text into tokens, and create a TokenAnn
        on each one.

        Args:
            text_input (str):

        Returns:
            List['TokenAnn']: a list of TokenAnn annotations created on the given text
        """
        token_strs = SpacyUtils.tokenize(text_input)

        result = []
        start_search_idx = 0
        for token in token_strs:
            start_idx = text_input.find(token, start_search_idx)
            end_idx = start_idx + len(token)
            token_ann = TokenAnn(start_idx, end_idx, token.strip())
            result.append(token_ann)
            start_search_idx = end_idx

        return result


if __name__ == '__main__':
    pass
