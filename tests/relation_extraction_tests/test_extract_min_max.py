

import re
import unittest

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import SimpleExtractionPhase, ChainLink
from tests.relation_extraction_tests.extract_min_max_relation import entities_to_relations
from tests.relation_extraction_tests.min_max_phase_1 import MinMaxPhase_1
from tests.relation_extraction_tests.min_max_phase_3 import MinMaxPhase_3


class TestMinMax(unittest.TestCase):

    def test_simple(self):
        text = \
        """
        During those fraught times his weight ranged between 170 and 220 pounds.
        """

        entities = []

        # Write rules for two types of entities--Number and Unit_of_Measurement.
        number_rs = RegexString([r'\d+'], escape=False)
        matches = number_rs.get_match_triples(text)
        for match in matches:
            entity_dict = {
                'text': match[0],
                'start': match[1],
                'end': match[2],
                'type': 'Number'
            }
            entities.append(entity_dict)

        uom_rs = RegexString(['pounds'])
        matches = uom_rs.get_match_triples(text)
        for match in matches:
            entity_dict = {
                'text': match[0],
                'start': match[1],
                'end': match[2],
                'type': 'Unit_of_Measure'
            }
            entities.append(entity_dict)

        input_dict = {
            "text": text,
            "entities": entities
            }

        expected = [{'type': 'MinMax', 'start': 54, 'end': 80, 'text': 'between 170 and 220 pounds'}]
        relations = entities_to_relations(input_dict, verbose=False)

        self.assertEqual(relations, expected)

    def test_exception(self):
        # Test a condition that used to provoke an exception.
        text = \
        """
        During those fraught times his weight ranged between 170 and 220 pounds
        and, with the 30 to 40 drinks per week he was inclined to enjoy, his IQ
        varied almost as much--anywhere within the range of 60 to 90 points.
        """
        # Note: the code being invoked intentionally doesn't extract the min-max
        # relation in "30 to 40 drinks" above.

        entities = []

        # Write rules for two types of entities--Number and Unit_of_Measurement.
        number_rs = RegexString([r'\d+'], escape=False)
        matches = number_rs.get_match_triples(text)
        for match in matches:
            entity_dict = {
                'text': match[0],
                'start': match[1],
                'end': match[2],
                'type': 'Number'
            }
            entities.append(entity_dict)

        uom_rs = RegexString(['pounds', 'drinks', 'points'])
        matches = uom_rs.get_match_triples(text)
        for match in matches:
            entity_dict = {
                'text': match[0],
                'start': match[1],
                'end': match[2],
                'type': 'Unit_of_Measure'
            }
            entities.append(entity_dict)

        input_dict = {
            "text": text,
            "entities": entities
            }

        print()

        expected = [{'type': 'MinMax', 'start': 54, 'end': 80, 'text': 'between 170 and 220 pounds'},
                    {'type': 'MinMax', 'start': 103, 'end': 118, 'text': '30 to 40 drinks'},
                    {'type': 'MinMax', 'start': 201, 'end': 236, 'text': 'within the range of 60 to 90 points'}]
        relations = entities_to_relations(input_dict, verbose=False)
        self.assertEqual(relations, expected)



    def test_MinMax_lower_upper_nps(self):
        # Test ranges expressed as two noun phrases following this pattern:
        # <at least> Cardinal + UoM and <at most> Cardinal + Uom

        # lower limit, upper limit
        text = "When he began, it would take him a minimum of 15 minutes and a "
        text += "maximum of 20 minutes to run a mile."

        entities = []

        # Write rules for two types of entities--Number and Unit_of_Measurement.
        number_rs = RegexString([r'\d+'], escape=False)
        matches = number_rs.get_match_triples(text)
        for match in matches:
            entity_dict = {
                'text': match[0],
                'start': match[1],
                'end': match[2],
                'type': 'Number'
            }
            entities.append(entity_dict)

        uom_rs = RegexString(['minutes'])
        matches = uom_rs.get_match_triples(text)
        for match in matches:
            entity_dict = {
                'text': match[0],
                'start': match[1],
                'end': match[2],
                'type': 'Unit_of_Measure'
            }
            entities.append(entity_dict)

        input_dict = {
            "text": text,
            "entities": entities
            }

        expected = [{'type': 'MinMax',
                     'start': 35, 'end': 84,
                     'text': 'minimum of 15 minutes and a maximum of 20 minutes'}]
        relations = entities_to_relations(input_dict, verbose=False)

        self.assertEqual(relations, expected)


class TestMinMaxProperties(unittest.TestCase):
    """
    Verify that when the same annotation type (e.g. 'Number') appears more
    than once in a chain, both values are accessible in the relation's
    properties under distinct keys. The fix is to assign meaningful property
    names in each ChainLink rather than keying by annotation type.
    """

    def _make_entity_annotations(self, text, number_pattern=r'(\d+)', uom_words=None):
        anns = []
        number_rs = RegexString.from_regex(number_pattern)
        for match in number_rs.get_match_triples(text):
            anns.append(Annotation('Number', match[0], match[1], match[2]))
        if uom_words:
            uom_rs = RegexString(uom_words)
            for match in uom_rs.get_match_triples(text):
                anns.append(Annotation('Unit_of_Measure', match[0], match[1], match[2]))
        return anns

    def test_phase3_min_number_not_overwritten(self):
        # MinMaxPhase_3 chain: AtLeast -> Number -> Unit_of_Measure -> AtMost -> Number -> Unit_of_Measure
        # 'Number' appears twice; both values must be accessible under distinct keys.
        text = "a minimum of 15 minutes and a maximum of 20 minutes"
        anns = self._make_entity_annotations(text, uom_words=['minutes'])

        phase = MinMaxPhase_3()
        results = phase.find_match(text, anns)

        self.assertEqual(len(results), 1)
        props = results[0].properties
        self.assertEqual(props['min_number'], '15')
        self.assertEqual(props['max_number'], '20')

    def test_phase1_both_numbers_in_properties(self):
        # MinMaxPhase_1 chain: Range -> Number -> Number -> Unit_of_Measure
        # 'Number' appears twice; both values must be accessible under distinct keys.
        text = "between 170 and 220 pounds"
        anns = self._make_entity_annotations(text, uom_words=['pounds'])

        phase = MinMaxPhase_1()
        results = phase.find_match(text, anns)

        self.assertEqual(len(results), 1)
        props = results[0].properties
        self.assertEqual(props['min_number'], '170')
        self.assertEqual(props['max_number'], '220')

    def test_unsorted_entity_annotations_two_uom(self):
        # Chain: Range -> Number -> Unit_of_Measure -> Number -> Unit_of_Measure
        # Two Unit_of_Measure annotations of the same type appear in the chain.
        # Entity annotations are passed in reverse text order to verify the library
        # sorts internally and produces the same result regardless of input order.
        text = "between 170 pounds and 200 pounds"

        range_rs = RegexString(['between'])
        chain = [
            ChainLink(start_type='Range', start_property='range_phrase',
                      min_distance=0, max_distance=3,
                      end_type='Number', end_property='min_number'),
            ChainLink(start_type='Number', start_property='min_number',
                      min_distance=0, max_distance=2,
                      end_type='Unit_of_Measure', end_property='min_unit'),
            ChainLink(start_type='Unit_of_Measure', start_property='min_unit',
                      min_distance=0, max_distance=3,
                      end_type='Number', end_property='max_number'),
            ChainLink(start_type='Number', start_property='max_number',
                      min_distance=0, max_distance=2,
                      end_type='Unit_of_Measure', end_property='max_unit'),
        ]
        phase = SimpleExtractionPhase(
            relation_name='MinMax',
            regex_patterns={'Range': range_rs},
            chain=chain,
        )

        # Deliberately pass in reverse text order: second pair first.
        entity_annotations = [
            Annotation('Number', '200', 23, 26),
            Annotation('Unit_of_Measure', 'pounds', 27, 33),
            Annotation('Number', '170', 8, 11),
            Annotation('Unit_of_Measure', 'pounds', 12, 18),
        ]

        results = phase.find_match(text, entity_annotations)

        self.assertEqual(len(results), 1)
        props = results[0].properties
        self.assertEqual(props['min_number'], '170')
        self.assertEqual(props['min_unit'], 'pounds')
        self.assertEqual(props['max_number'], '200')
        self.assertEqual(props['max_unit'], 'pounds')
