import unittest
import inspect

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink, SimpleExtractionPhase
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

        with self.assertRaises(ValueError):
            run_loop(annotation_view_str=annotation_view_str,
                doc=text,
                relation_name='MinMax',
                curr_loop=loop_1,
                loop_idx=0,
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
        self.assertEqual([{'type': 'MinMax', 'text': '1 a 2 b 3', 'start': 0, 'end': 9,
                           'one': '1', 'two': '2', 'three': '3'}], result)

        # Second test: multiple matches.
        text = "z 1 a 1 b 2 c 2 d 3 y 1 2 3 x"
        result = phase.find_match(text)
        self.assertEqual([{'type': 'MinMax', 'text': '1 2 3', 'start': 22, 'end': 27,
                           'one': '1', 'two': '2', 'three': '3'}], result)

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

    def test_consecutive_identical_annotations(self):
        text = "lower limit of 87 ft-lb Foot-pounds to upper limit of 92 ft-lb Foot-pounds."

        at_least_strs = ["at least", "lower limit", "minimum of", "no less than"]
        at_least_regex_str = RegexString(at_least_strs)
        at_most_strs = ["at most", "upper limit", "maximum of", "no more than"]
        at_most_regex_str = RegexString(at_most_strs)
        regex_patterns = {
            "AtLeast": at_least_regex_str,
            "AtMost": at_most_regex_str,
        }

        entity_annotations = [
            {'type': 'CARDINAL',            'text': '87',    'start': 15, 'end': 17},
            {'type': 'UNIT_OF_MEASUREMENT', 'text': 'ft-lb', 'start': 18, 'end': 23},
            {'type': 'UNIT_OF_MEASUREMENT', 'text': 'Foot',  'start': 24, 'end': 28},
            {'type': 'CARDINAL',            'text': '92',    'start': 54, 'end': 56},
            {'type': 'UNIT_OF_MEASUREMENT', 'text': 'ft-lb', 'start': 57, 'end': 62},
        ]

        # Define the allowable distance between entities for
        # extractions of this particular relation.
        chain = [
            ChainLink(
                start_type="AtLeast",
                start_property="AtLeast",
                min_distance=0,
                max_distance=3,
                end_type="CARDINAL",
                end_property="min",
            ),
            ChainLink(
                start_type="CARDINAL",
                start_property="min",
                min_distance=0,
                max_distance=2,
                end_type="UNIT_OF_MEASUREMENT",
                end_property="unit_of_measure",
            ),
            ChainLink(
                start_type="UNIT_OF_MEASUREMENT",
                start_property="unit_of_measure",
                min_distance=0,
                max_distance=10,
                end_type="AtMost",
                end_property="AtMost",
            ),
            ChainLink(
                start_type="AtMost",
                start_property="AtMost",
                min_distance=0,
                max_distance=3,
                end_type="CARDINAL",
                end_property="max",
            ),
            ChainLink(
                start_type="CARDINAL",
                start_property="max",
                min_distance=0,
                max_distance=2,
                # We could have set 'unit_of_measure' to the
                # preceding UOM just as well.
                end_type="UNIT_OF_MEASUREMENT",
                end_property="UNIT_OF_MEASUREMENT_2",
            ),
        ]

        # Create the phase.
        phase = SimpleExtractionPhase(
            relation_name="MinMax",
            regex_patterns=regex_patterns,
            chain=chain,
            verbose=False,
        )

        relations = phase.find_match(text, entity_annotations=entity_annotations)

        self.assertEqual([{
            'type': 'MinMax',
            'text': 'lower limit of 87 ft-lb Foot-pounds to upper limit of 92 ft-lb',
            'start': 0, 'end': 62,
            'AtLeast': 'lower limit',
            'min': '87',
            'unit_of_measure': 'ft-lb',
            'AtMost': 'upper limit',
            'max': '92',
            'UNIT_OF_MEASUREMENT_2': 'ft-lb',
        }], relations)


class TestOverlappingBug(unittest.TestCase):
    # Tests for the bug where non-overlapping re.finditer causes valid chains
    # to be missed.

    def test_loop0_overlapping_bug(self):
        # Pattern: 1 -> 1 -> 2, each immediately adjacent (distance 0).
        # Text "1 1 1 2": Loop 0 (One->One) non-overlapping re.finditer finds
        # the first 1+1 pair and skips the second. Loop 1 (One->Two) then
        # fails because a third 1 sits between that pair and 2. The fix:
        # overlapping candidate enumeration at Loop 0.
        # Expected chain: second_1 + third_1 + 2, text='1 1 2', start=2, end=7.
        phase = SimpleExtractionPhase(
            relation_name='TestRelation',
            regex_patterns={
                'One': RegexString(['1']),
                'Two': RegexString(['2']),
            },
            chain=[
                ChainLink('One', 'one_a', 0, 0, 'One', 'one_b'),
                ChainLink('One', 'one_b', 0, 0, 'Two', 'two'),
            ],
        )
        result = phase.find_match("1 1 1 2")
        self.assertEqual([{
            'type': 'TestRelation', 'text': '1 1 2', 'start': 2, 'end': 7,
            'one_a': '1', 'one_b': '1', 'two': '2',
        }], result)

    def test_intermediate_loop_overlapping_bug(self):
        # Pattern: 1 -> 2 -> 2 -> 3. Loop 0 (One->Two, distance 0) finds the
        # only valid 1+2 pair. Loop 1 (Two->Two, max distance 1) non-greedy
        # finds the first adjacent 2+2; Loop 2 then fails because a third 2
        # sits between that pair and 3. The fix must enumerate all candidates
        # at every loop level, not just Loop 0.
        # Expected chain: 1 + first_2 + third_2 + 3.
        phase = SimpleExtractionPhase(
            relation_name='TestRelation',
            regex_patterns={
                'One': RegexString(['1']),
                'Two': RegexString(['2']),
                'Three': RegexString(['3']),
            },
            chain=[
                ChainLink('One',   'one',   0, 0, 'Two',   'two_a'),
                ChainLink('Two',   'two_a', 0, 1, 'Two',   'two_b'),
                ChainLink('Two',   'two_b', 0, 0, 'Three', 'three'),
            ],
        )
        result = phase.find_match("1 2 2 2 3")
        self.assertEqual([{
            'type': 'TestRelation', 'text': '1 2 2 2 3', 'start': 0, 'end': 9,
            'one': '1', 'two_a': '2', 'two_b': '2', 'three': '3',
        }], result)

    def test_allow_overlapping_parameter(self):
        # Pattern: 1 -> 2 -> 3, where 1->2 allows up to 1 intervening token.
        # Text "1 1 2 3": both 1s can reach 2 within max_distance=1, producing
        # two overlapping chains (they share the 2 and 3 annotations).
        #
        # allow_overlapping=False (default): only the first chain is returned.
        # allow_overlapping=True: both chains are returned.
        regex_patterns = {
            'One':   RegexString(['1']),
            'Two':   RegexString(['2']),
            'Three': RegexString(['3']),
        }
        chain = [
            ChainLink('One',   'one',   0, 1, 'Two',   'two'),
            ChainLink('Two',   'two',   0, 0, 'Three', 'three'),
        ]

        phase_default = SimpleExtractionPhase(
            relation_name='TestRelation',
            regex_patterns=regex_patterns,
            chain=chain,
        )
        result = phase_default.find_match("1 1 2 3")
        self.assertEqual([{
            'type': 'TestRelation', 'text': '1 1 2 3', 'start': 0, 'end': 7,
            'one': '1', 'two': '2', 'three': '3',
        }], result)

        phase_overlap = SimpleExtractionPhase(
            relation_name='TestRelation',
            regex_patterns=regex_patterns,
            chain=chain,
            allow_overlapping=True,
        )
        result = phase_overlap.find_match("1 1 2 3")
        self.assertEqual([
            {'type': 'TestRelation', 'text': '1 1 2 3', 'start': 0, 'end': 7,
             'one': '1', 'two': '2', 'three': '3'},
            {'type': 'TestRelation', 'text': '1 2 3', 'start': 2, 'end': 7,
             'one': '1', 'two': '2', 'three': '3'},
        ], result)


class TestForbiddenGapType(unittest.TestCase):

    def test_forbidden_gap_type(self):
        phase = SimpleExtractionPhase(
            relation_name='TestRelation',
            regex_patterns={
                'One': RegexString(['1']),
                'Two': RegexString(['2']),
                'Conjunction': RegexString(['and']),
            },
            chain=[
                ChainLink('One', 'one', 0, 3, 'Two', 'two',
                          forbidden_gap_type='Conjunction'),
            ],
        )
        # Conjunction in the gap — should not match.
        result = phase.find_match("1 and 2")
        self.assertEqual([], result)

        # No Conjunction in the gap — should match.
        result = phase.find_match("1 x 2")
        self.assertEqual([{
            'type': 'TestRelation', 'text': '1 x 2', 'start': 0, 'end': 5,
            'one': '1', 'two': '2',
        }], result)

    def test_forbidden_gap_type_between_links(self):
        # forbidden_gap_type on the second link prevents matching when the
        # forbidden annotation appears between the two links (in the second
        # link's gap), even though the first link's gap is clean.
        phase = SimpleExtractionPhase(
            relation_name='TestRelation',
            regex_patterns={
                'One':         RegexString(['1']),
                'Two':         RegexString(['2']),
                'Three':       RegexString(['3']),
                'Conjunction': RegexString(['and']),
            },
            chain=[
                ChainLink('One', 'one', 0, 0, 'Two',   'two'),
                ChainLink('Two', 'two', 0, 2, 'Three', 'three',
                          forbidden_gap_type='Conjunction'),
            ],
        )
        # Conjunction between the two links — should not match.
        result = phase.find_match("1 2 and 3")
        self.assertEqual([], result)

        # No Conjunction between the links — should match.
        result = phase.find_match("1 2 3")
        self.assertEqual([{
            'type': 'TestRelation', 'text': '1 2 3', 'start': 0, 'end': 5,
            'one': '1', 'two': '2', 'three': '3',
        }], result)
