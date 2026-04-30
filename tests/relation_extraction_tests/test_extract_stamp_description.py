import inspect
import re
import unittest

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, SimpleExtractionPhase, ChainLink


def _make_phase(verbose: bool = False) -> SimpleExtractionPhase:
    id_rs = RegexString(['#'], append=r'\s\d+(?:\w+)?')
    cent_rs = RegexString(['c', '¢'], prepend=r'\d\d?')
    type_markers_rs = RegexString(['type', 'Type'], whole_word=True)
    roman_nums_rs = RegexString(['I', 'II', 'III', 'IV', 'V'], whole_word=True)
    type_phrase_rs = RegexString.concat_with_word_distances(
        type_markers_rs, roman_nums_rs, min_nbr_words=0, max_nbr_words=0)
    imperf_rs = RegexString(['imperforate', 'imperf'])
    perf_sized_rs = RegexString(['perf'], append=r'\s\d+')
    perf_combined_rs = RegexString.from_regex(
        f'(?:{imperf_rs.get_regex_str()}|{perf_sized_rs.get_regex_str()})')

    return SimpleExtractionPhase(
        relation_name='StampDescription',
        regex_patterns={
            'StampID':      id_rs,
            'Denomination': cent_rs,
            'TypePhrase':   type_phrase_rs,
            'Perforation':  perf_combined_rs,
        },
        chain=[
            ChainLink(start_type='StampID', start_property='StampID',
                      min_distance=0, max_distance=4,
                      end_type='Denomination', end_property='Denomination'),
            ChainLink(start_type='Denomination', start_property='Denomination',
                      min_distance=0, max_distance=8,
                      end_type='TypePhrase', end_property='TypePhrase'),
            ChainLink(start_type='TypePhrase', start_property='TypePhrase',
                      min_distance=0, max_distance=2,
                      end_type='Perforation', end_property='Perforation'),
        ],
        verbose=verbose,
    )


class TestStampDescriptionPhase(unittest.TestCase):

    def test_single_match(self):
        # A single entry with all four fields should produce one StampDescription.
        text = '# 11A - 1853-55 3¢ George Washington, dull red, type II, imperf'
        phase = _make_phase()
        results = phase.find_match(text)

        self.assertEqual(1, len(results))
        self.assertEqual('StampDescription', results[0]['type'])
        self.assertEqual('# 11A', results[0]['StampID'])
        self.assertEqual('3¢', results[0]['Denomination'])
        self.assertEqual('type II', results[0]['TypePhrase'])
        self.assertEqual('imperf', results[0]['Perforation'])

    def test_missing_type_phrase(self):
        # An entry missing TypePhrase should produce no result.
        text = '# 17 - 1851 12c Washington imperforate, black'
        phase = _make_phase()
        results = phase.find_match(text)

        self.assertEqual(0, len(results))

    def test_missing_all_optional_fields(self):
        # An entry with only a StampID should produce no result.
        text = '# 40 - 1875 1c Franklin, bright blue'
        phase = _make_phase()
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
        phase = _make_phase()
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
        phase = _make_phase()
        entries = [e.strip() for e in re.split(r'\n\s*\n', input_text) if e.strip()]
        results = []
        for entry in entries:
            results.extend(phase.find_match(entry))

        self.assertEqual(3, len(results))

        self.assertEqual('# 11A', results[0]['StampID'])
        self.assertEqual('3¢', results[0]['Denomination'])
        self.assertEqual('type II', results[0]['TypePhrase'])
        self.assertEqual('imperf', results[0]['Perforation'])

        self.assertEqual('# 12', results[1]['StampID'])
        self.assertEqual('5c', results[1]['Denomination'])
        self.assertEqual('type I', results[1]['TypePhrase'])
        self.assertEqual('imperforate', results[1]['Perforation'])

        self.assertEqual('# 18', results[2]['StampID'])
        self.assertEqual('1c', results[2]['Denomination'])
        self.assertEqual('type I', results[2]['TypePhrase'])
        self.assertEqual('perf 15', results[2]['Perforation'])

    def test_find_match_requires_instance_vars(self):
        # A subclass that does not set relation_name, regex_patterns, and chain
        # should raise ValueError at construction time.
        class BarePhase(ExtractionPhaseABC):
            def __init__(self):
                super().__init__()

        with self.assertRaises(ValueError):
            BarePhase()
