

import re
import unittest

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.extract_min_max_relation import entities_to_relations


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
                    {'type': 'MinMax', 'start': 202, 'end': 237, 'text': 'within the range of 60 to 90 points'}]
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
