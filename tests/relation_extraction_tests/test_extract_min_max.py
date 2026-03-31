

import re
import unittest

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
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
        number_rs = RegexString.regex_to_RegexString('(\d+)')
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
        number_rs = RegexString.regex_to_RegexString('(\d+)')
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
        number_rs = RegexString.regex_to_RegexString('(\d+)')
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


# class TestMinMaxProperties(unittest.TestCase):
#     """
#     These tests expose a property-naming collision that occurs when the same
#     annotation type (e.g. 'Number') appears more than once in a chain.
#     _determine_properties() keys properties by type name, so the second
#     occurrence silently overwrites the first. Until the naming scheme is
#     changed to '{type}_{position:02d}', these tests are expected to FAIL.
#     """

#     def _make_entity_annotations(self, text, number_pattern=r'(\d+)', uom_words=None):
#         anns = []
#         number_rs = RegexString.regex_to_RegexString(number_pattern)
#         for match in number_rs.get_match_triples(text):
#             anns.append(Annotation('Number', match[0], match[1], match[2]))
#         if uom_words:
#             uom_rs = RegexString(uom_words)
#             for match in uom_rs.get_match_triples(text):
#                 anns.append(Annotation('Unit_of_Measure', match[0], match[1], match[2]))
#         return anns

#     def test_phase3_min_number_not_overwritten(self):
#         # MinMaxPhase_3 chain: AtLeast -> Number -> Unit_of_Measure -> AtMost -> Number -> Unit_of_Measure
#         # 'Number' appears twice; the min value ('15') should be accessible in properties.
#         # Currently _determine_properties() stores properties['Number'] = '20' (max overwrites min).
#         text = "a minimum of 15 minutes and a maximum of 20 minutes"
#         anns = self._make_entity_annotations(text, uom_words=['minutes'])

#         phase = MinMaxPhase_3()
#         results = phase.find_match(text, anns)

#         self.assertEqual(len(results), 1)
#         props = results[0].properties
#         # The min and max Numbers must be stored under distinct keys.
#         # With the current implementation this fails because only one 'Number' key exists.
#         self.assertIn('Number_01', props, "min Number should be stored as 'Number_01'")
#         self.assertIn('Number_02', props, "max Number should be stored as 'Number_02'")
#         self.assertEqual(props['Number_01'], '15')
#         self.assertEqual(props['Number_02'], '20')

#     def test_phase1_both_numbers_in_properties(self):
#         # MinMaxPhase_1 chain: RangeMarker -> Number -> Number -> Unit_of_Measure
#         # 'Number' appears twice; both values should be independently accessible.
#         # Currently _determine_properties() stores only the last Number seen.
#         text = "between 170 and 220 pounds"
#         anns = self._make_entity_annotations(text, uom_words=['pounds'])

#         phase = MinMaxPhase_1()
#         results = phase.find_match(text, anns)

#         self.assertEqual(len(results), 1)
#         props = results[0].properties
#         self.assertIn('Number_01', props, "first Number should be stored as 'Number_01'")
#         self.assertIn('Number_02', props, "second Number should be stored as 'Number_02'")
#         self.assertEqual(props['Number_01'], '170')
#         self.assertEqual(props['Number_02'], '220')
