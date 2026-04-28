import unittest

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink
from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.extraction_loop import ExtractionLoop, run_loop, get_sorted_annotations_for_matching


def _simple_properties(match_triples):
    # Stub callback for the determine_new_annotation_properties parameter of ExtractionLoop.
    # run_loop() requires the last loop in a chain to have a non-None value for that parameter,
    # so tests that exercise validation logic (rather than the resulting Annotation's properties)
    # pass this no-op to satisfy the contract.
    return {}


class OneTwoThreePhase(ExtractionPhaseABC):
    """Test phase: matches One -> Two -> Three, each within 2 tokens of the next."""
    def __init__(self, verbose: bool = False):
        super().__init__(verbose=verbose)
        self.relation_name = 'MinMax'
        self.regex_patterns = {
            'One':   RegexString(['1']),
            'Two':   RegexString(['2']),
            'Three': RegexString(['3']),
        }
        self.chain = [
            ChainLink(start_type='One', start_property='one',
                      min_distance=0, max_distance=2,
                      end_type='Two', end_property='two'),
            ChainLink(start_type='Two', start_property='two',
                      min_distance=0, max_distance=2,
                      end_type='Three', end_property='three'),
        ]


class TestExtractionLoop(unittest.TestCase):

    def test_invalid_loop_list(self):
        # Verify an exception is thrown if any but the last loop has
        # a defined determine_new_annotation_properties.
        one_rs = RegexString(['1'])
        regex_strs = {"One": one_rs}

        text = "1 a 2 b 3"

        anns = get_sorted_annotations_for_matching(text=text, regex_strs=regex_strs, given_anns=[])
        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        regex_1 = TokenAnn.build_annotation_distance_regex("One", (0, 2), None, "Two")
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two',
                                determine_new_annotation_properties=_simple_properties,
                                verbose=False)

        regex_2 = TokenAnn.build_annotation_distance_regex("Two", (0, 2), None, "Three")
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three',
                                determine_new_annotation_properties=_simple_properties,
                                verbose=False)

        loop_list = [loop_1, loop_2]
        loops_in_process = []

        with self.assertRaises(ValueError):
            run_loop(annotation_view_str=annotation_view_str,
                doc=text,
                relation_name='MinMax',
                curr_loop=loop_1,
                loop_idx=0,
                loops_in_process=loops_in_process,
                loop_list=loop_list,
                match_triples_list=[],
                new_annotations=[],
                verbose=False)

        # Verify that an exception is thrown if the last loop does not
        # have a determine_new_annotation_properties defined.
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two', verbose=False)
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three', verbose=False)
        loop_list = [loop_1, loop_2]
        with self.assertRaises(ValueError):
            run_loop(annotation_view_str=annotation_view_str,
                doc=text,
                relation_name='MinMax',
                curr_loop=loop_1,
                loop_idx=0,
                loops_in_process=loops_in_process,
                loop_list=loop_list,
                match_triples_list=[],
                new_annotations=[],
                verbose=False)

    def test_failure(self):
        # Verify that the process fails gracefully if there are no matches.
        # 1 is within two tokens of 2, but 2 is not within two tokens of 3.
        text = "1 a 2 b c d e f g h i 3"
        phase = OneTwoThreePhase()
        result = phase.find_match(text)
        self.assertEqual([], result)

    def test_two_loops(self):
        phase = OneTwoThreePhase()

        # First test: simple match.
        text = "1 a 2 b 3"
        result = phase.find_match(text)
        props = {"one": "1", "two": "2", "three": "3"}
        self.assertEqual([Annotation("MinMax", "1 a 2 b 3", 0, 9, props)], result)

        # Second test: multiple matches.
        text = "z 1 a 1 b 2 c 2 d 3 y 1 2 3 x"
        result = phase.find_match(text)
        props = {"one": "1", "two": "2", "three": "3"}
        ann2 = Annotation("MinMax", "1 2 3", 22, 27, props)
        self.assertEqual([ann2], result)

    def test_failures(self):
        phase = OneTwoThreePhase()

        # First test: fail to match first pair.
        text = "1 a a a 2 b 3"
        result = phase.find_match(text)
        self.assertEqual([], result)

        # Second test: fail to match second pair.
        text = "1 a 2 b b b 3"
        result = phase.find_match(text)
        self.assertEqual([], result)

        # Third test: The first pair has a match and the second pair
        # has a match, but the first element of the second pair match is
        # not a valid second element of the first match.
        text = "1 a 2 b b b 2 b 3"
        result = phase.find_match(text)
        self.assertEqual([], result)

    def test_RegexString_object_raises(self):
        # Verify that passing a RegexString object (instead of a str) raises a
        # ValueError with a message pointing to .get_regex_str().
        regex_1_str = TokenAnn.build_annotation_distance_regex("One", (0, 2), None, "Two")
        regex_1 = RegexString.from_regex(regex_1_str)
        with self.assertRaises(ValueError):
            ExtractionLoop(regex_str=regex_1, last_ann_str="Two")
