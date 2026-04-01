"""
Extract StampDescription relations from postage stamp description text.

A StampDescription links a stamp's ID, denomination, type numeral, and
perforation information together when all four fields are present in the
same stamp entry.  Stamps that lack any of the four fields are silently
skipped; in the main function, the sample data this means 3 of 7 entries
produce a result.
"""
import inspect
# from typing import List

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink


class StampDescriptionPhase(ExtractionPhaseABC):
    def __init__(self, verbose: bool = False):
        super().__init__(verbose=verbose)
        self.relation_name = 'StampDescription'

        # Step 1: Define all the RegexString objects which identify entities
        # to be extracted.

        # Stamp ID: e.g. '# 11A', '# 17', '# 62B'
        id_rs = RegexString(['#'], append=r'\s\d+(?:\w+)?')

        # Denomination: e.g. '3¢', '12c', '5c', '1c', '10c'
        cent_rs = RegexString(['c', '¢'], prepend=r'\d\d?')

        # Type phrase: e.g. 'type I', 'type II'
        type_markers_rs = RegexString(['type', 'Type'], whole_word=True)
        roman_nums_rs = RegexString(['I', 'II', 'III', 'IV', 'V'], whole_word=True)
        type_phrase_rs = RegexString.concat_with_word_distances(
            type_markers_rs, roman_nums_rs, min_nbr_words=0, max_nbr_words=0)

        # Perforation: 'imperf', 'imperforate', or 'perf NN'
        imperf_rs = RegexString(['imperforate', 'imperf'])
        perf_sized_rs = RegexString(['perf'], append=r'\s\d+')
        perf_combined_rs = RegexString.regex_to_RegexString(
            f'(?:{imperf_rs.get_regex_str()}|{perf_sized_rs.get_regex_str()})')

        self.regex_patterns = {
            'StampID':      id_rs,
            'Denomination': cent_rs,
            'TypePhrase':   type_phrase_rs,
            'Perforation':  perf_combined_rs,
        }

        # Step 2: Define the allowable distance between entities for
        # extractions of this particular relation.
        self.chain = [
            # Look for a StampID entity followed by a Denomination entity
            # within four tokens...
            ChainLink('StampID',      'StampID',      0, 4, 'Denomination', 'Denomination'),
            # ... which in turn is followed by a TypePhrase entity within
            # eight tokens...
            ChainLink('Denomination', 'Denomination', 0, 8, 'TypePhrase',   'TypePhrase'),
            # ... followed by a Perforation entity within two tokens
            ChainLink('TypePhrase',   'TypePhrase',   0, 2, 'Perforation',  'Perforation'),
        ]


if __name__ == '__main__':
    # Sample call:
    #   python -m examples.extract_stamp_description

    import re
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    verbose = args.verbose

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

    phase = StampDescriptionPhase(verbose=verbose)
    paragraphs = [e.strip() for e in re.split(r'\n\s*\n', input_text) if e.strip()]
    results = []
    for par in paragraphs:
        relations = phase.find_match(par)
        results.extend(relations)

    print(f'\n{len(results)} of 7 stamp descriptions extracted:\n')
    for ann in results:
        p = ann.properties
        print(f"  stamp_id='{p['StampID']}', denomination='{p['Denomination']}', "
              f"type='{p['TypePhrase']}', perforation_info='{p['Perforation']}'")

    expected = [
        "stamp_id='# 11A', denomination='3¢', type='type II', perforation_info='imperf'",
        "stamp_id='# 12', denomination='5c', type='type I', perforation_info='imperforate'",
        "stamp_id='# 18', denomination='1c', type='type I', perforation_info='perf 15'",
    ]
    print('\nExpected output:\n')
    for line in expected:
        print(f'  {line}')
