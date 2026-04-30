"""
Extract MinMax relations from text using externally-produced entity annotations.

This example demonstrates how to pass entity annotations produced by an external
tool to find_match() via its entity_annotations parameter.  The phase itself only
detects the Range entity ('between', 'within the range of', etc.).  Number
and Unit_of_Measure annotations are detected outside the phase and passed in.

In a real pipeline, Number and Unit_of_Measure entities would typically come from
a NER model or a gazetteer rather than the simple regex matching shown here.
"""
import inspect
import argparse

from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink


class MinMaxPhase(ExtractionPhaseABC):
    def __init__(self, verbose: bool = False):
        """
        Identify phrases like 'between 170 and 220 pounds' by looking for:
            Range + Number + Number + Unit_of_Measure

        Only Range is detected by this phase's own regex patterns.
        Number and Unit_of_Measure annotations must be supplied externally
        via find_match()'s entity_annotations parameter.
        """
        super().__init__(verbose=verbose)
        self.relation_name = 'MinMax'
        self.regex_patterns = {
            'Range': RegexString(['within the range of', 'between']),
        }
        self.chain = [
            ChainLink(start_type='Range', start_property='range_marker',
                      min_distance=0, max_distance=3,
                      end_type='Number', end_property='min_number'),
            ChainLink(start_type='Number', start_property='min_number',
                      min_distance=0, max_distance=2,
                      end_type='Number', end_property='max_number'),
            ChainLink(start_type='Number', start_property='max_number',
                      min_distance=0, max_distance=2,
                      end_type='Unit_of_Measure', end_property='unit'),
        ]


if __name__ == '__main__':
    # Sample call:
    #   python -m examples.extract_min_max

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    verbose = args.verbose

    input_text = inspect.cleandoc("""
        During those fraught times his weight ranged between 170 and 220 pounds.
        He visited the gym within the range of 3 to 5 times per week.
    """)

    # Step 1: Detect Number and Unit_of_Measure entities externally and wrap
    # them in Annotation objects for the library.  There is no need to sort
    # the list before passing it to find_match() -- the library sorts internally.
    number_rs = RegexString([r'\d+'], escape=False)
    uom_rs = RegexString(['pounds', 'times'])

    entity_annotations = []
    for text, start, end in number_rs.get_match_triples(input_text):
        entity_annotations.append(Annotation('Number', text, start, end))
    for text, start, end in uom_rs.get_match_triples(input_text):
        entity_annotations.append(Annotation('Unit_of_Measure', text, start, end))

    # Step 2: Instantiate the extraction phase and run it, passing in the
    # externally-produced annotations alongside the phase's own regex patterns.
    phase = MinMaxPhase(verbose=verbose)
    results = phase.find_match(input_text, entity_annotations=entity_annotations)

    print(f'\n{len(results)} MinMax relation(s) found:\n')
    for ann in results:
        p = ann.properties
        print(f"  range_marker='{p['range_marker']}', min='{p['min_number']}', "
              f"max='{p['max_number']}', unit='{p['unit']}'")

    expected = [
        "range_marker='between', min='170', max='220', unit='pounds'",
        "range_marker='within the range of', min='3', max='5', unit='times'",
    ]
    print('\nExpected output:\n')
    for line in expected:
        print(f'  {line}')
