import inspect
import re
import unittest

from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC
from examples.extract_stamp_description import StampDescriptionPhase


class TestStampDescriptionPhase(unittest.TestCase):

    def test_single_match(self):
        # A single entry with all four fields should produce one StampDescription.
        text = '# 11A - 1853-55 3¢ George Washington, dull red, type II, imperf'
        phase = StampDescriptionPhase()
        results = phase.find_match(text)

        self.assertEqual(1, len(results))
        self.assertEqual('StampDescription', results[0].type)
        p = results[0].properties
        self.assertEqual('# 11A', p['StampID'])
        self.assertEqual('3¢', p['Denomination'])
        self.assertEqual('type II', p['TypePhrase'])
        self.assertEqual('imperf', p['Perforation'])

    def test_missing_type_phrase(self):
        # An entry missing TypePhrase should produce no result.
        text = '# 17 - 1851 12c Washington imperforate, black'
        phase = StampDescriptionPhase()
        results = phase.find_match(text)

        self.assertEqual(0, len(results))

    def test_missing_all_optional_fields(self):
        # An entry with only a StampID should produce no result.
        text = '# 40 - 1875 1c Franklin, bright blue'
        phase = StampDescriptionPhase()
        results = phase.find_match(text)

        self.assertEqual(0, len(results))

    def test_multi_entry_extraction(self):
        # Processing each blank-line-separated entry independently should
        # yield 3 matches out of 7 entries.
        input_text = """
        # 11A - 1853-55 3¢ George Washington, dull red, type II, imperf

        # 17 - 1851 12c Washington imperforate, black

        # 12 - 1856 5c Jefferson, red brown, type I, imperforate

        # 18 - 1861 1c Franklin, type I, perf 15

        # 40 - 1875 1c Franklin, bright blue

        # 42 - 1875 5c Jefferson, orange brown

        # 62B - 1861 10c Washington, dark green
        """
        input_text = inspect.cleandoc(input_text)
        phase = StampDescriptionPhase()
        entries = [e.strip() for e in re.split(r'\n\s*\n', input_text) if e.strip()]
        results = []
        for entry in entries:
            results.extend(phase.find_match(entry))

        self.assertEqual(3, len(results))

    def test_correct_properties(self):
        # Verify the properties of each extracted relation.
        input_text = """
        # 11A - 1853-55 3¢ George Washington, dull red, type II, imperf

        # 12 - 1856 5c Jefferson, red brown, type I, imperforate

        # 18 - 1861 1c Franklin, type I, perf 15
        """
        input_text = inspect.cleandoc(input_text)
        phase = StampDescriptionPhase()
        entries = [e.strip() for e in re.split(r'\n\s*\n', input_text) if e.strip()]
        results = []
        for entry in entries:
            results.extend(phase.find_match(entry))

        self.assertEqual(3, len(results))

        p = results[0].properties
        self.assertEqual('# 11A', p['StampID'])
        self.assertEqual('3¢', p['Denomination'])
        self.assertEqual('type II', p['TypePhrase'])
        self.assertEqual('imperf', p['Perforation'])

        p = results[1].properties
        self.assertEqual('# 12', p['StampID'])
        self.assertEqual('5c', p['Denomination'])
        self.assertEqual('type I', p['TypePhrase'])
        self.assertEqual('imperforate', p['Perforation'])

        p = results[2].properties
        self.assertEqual('# 18', p['StampID'])
        self.assertEqual('1c', p['Denomination'])
        self.assertEqual('type I', p['TypePhrase'])
        self.assertEqual('perf 15', p['Perforation'])

    def test_find_match_requires_instance_vars(self):
        # A subclass that does not set relation_name, regex_patterns, and chain
        # should raise ValueError at construction time.
        class BarePhase(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()

        with self.assertRaises(ValueError):
            BarePhase()
