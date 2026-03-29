"""
Extract StampDescription relations from postage stamp description text.

A StampDescription links a stamp's ID, denomination, type numeral, and
perforation information together when all four fields are present in the
same stamp entry.  Stamps that lack any of the four fields are silently
skipped; in the main function, the sample data this means 3 of 7 entries 
produce a result.
"""
import inspect
from typing import List, Tuple, Dict

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC
from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.extraction_loop import (
    ExtractionLoop, run_loop, get_sorted_annotations_for_matching)


def when_final_match_found(args: Dict[str, object]) -> Annotation:
    """
    Called when all three loops match successfully. Creates a
    StampDescription annotation spanning from the StampID to the
    Perforation.
    """
    loop = args['loop']
    doc = args['doc']
    triple = args['triple']
    match_triples_list = args['match_triples_list']
    if loop.verbose:
        print(f"\n  In when_final_match_found(). Found final match. triple: {triple}")

    # Start offset: first annotation in the first loop's match.
    m0_anns = ExtractionPhaseABC.merged_representation_to_Annotations(match_triples_list[0][0])
    start = m0_anns[0].start_offset

    # End offset: last annotation in the last loop's match.
    m_last_anns = ExtractionPhaseABC.merged_representation_to_Annotations(match_triples_list[-1][0])
    end = m_last_anns[-1].end_offset

    substr = doc[start:end]
    properties = loop.determine_new_annotation_properties(match_triples_list, doc)
    new_ann = Annotation('StampDescription', substr, start, end, properties)
    if loop.verbose:
        print(f"  New annotation created: {new_ann}")
    return new_ann


def determine_new_annotation_properties(match_triples: List[Tuple], doc: str) -> Dict[str, str]:
    """
    Extract the four stamp fields from the matched annotation triples.

    Args:
        match_triples: one entry per loop — (matched_text, start, end) in
            annotation-view coordinates.
        doc: the original document string (unused here, included for
            interface compatibility).

    Returns:
        Dict with keys stamp_id, denomination, type, and perforation_info.
    """
    # Loop 1 match spans StampID through Denomination.
    m0_anns = ExtractionPhaseABC.merged_representation_to_Annotations(match_triples[0][0])
    stamp_id    = m0_anns[0].normalizedContents   # first annotation  = StampID
    denomination = m0_anns[-1].normalizedContents  # last annotation   = Denomination

    # Loop 2 match spans Denomination through TypePhrase.
    m1_anns = ExtractionPhaseABC.merged_representation_to_Annotations(match_triples[1][0])
    stamp_type = m1_anns[-1].normalizedContents    # last annotation   = TypePhrase

    # Loop 3 match spans TypePhrase through Perforation.
    m2_anns = ExtractionPhaseABC.merged_representation_to_Annotations(match_triples[2][0])
    perforation = m2_anns[-1].normalizedContents   # last annotation   = Perforation

    return {
        'stamp_id':       stamp_id,
        'denomination':   denomination,
        'type':           stamp_type,
        'perforation_info': perforation,
    }


class StampDescriptionPhase(ExtractionPhaseABC):
    def __init__(self, doc_contents: str, verbose: bool = False):
        """
        Args:
            doc_contents: the stamp description text to process.
            verbose: if True, print internal state at each step.
        """
        super().__init__(doc_contents)
        self.verbose = verbose

    def run_phase(self) -> List[Annotation]:
        """
        Extract StampDescription annotations from the document.

        Each stamp entry is processed independently (splitting on blank lines)
        to prevent the extraction loops from matching across entry boundaries.

        Returns:
            List[Annotation]: one StampDescription annotation for each
                stamp entry that contains all four fields (ID, denomination,
                type, perforation).
        """
        import re as _re
        entries = [e.strip() for e in _re.split(r'\n\s*\n', self.doc_contents) if e.strip()]
        results = []
        for entry in entries:
            results.extend(self._run_phase_for_entry(entry))
        return results

    def _run_phase_for_entry(self, text: str) -> List[Annotation]:
        """Process a single stamp entry."""
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

        regex_strs = {
            'StampID':     id_rs,
            'Denomination': cent_rs,
            'TypePhrase':  type_phrase_rs,
            'Perforation': perf_combined_rs,
        }
        anns = get_sorted_annotations_for_matching(
            text=text, regex_strs=regex_strs, given_anns=[])

        if self.verbose:
            print(f'\nEntry: {text!r}')
            print('Entity annotations:')
            for ann in anns:
                print(f'  {ann}')

        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        return self.check_annotation_proximity(annotation_view_str)

    def check_annotation_proximity(self, annotation_view_str: str) -> List[Annotation]:
        """
        Chain three ExtractionLoops to find the sequence
        StampID → Denomination → TypePhrase → Perforation.

        Token-distance limits are chosen to span the typical text between
        each pair of entities while staying within a single stamp entry:
          - StampID → Denomination: at most 3 tokens (e.g. '- 1853-55')
          - Denomination → TypePhrase: at most 8 tokens (e.g. 'George Washington, dull red,')
          - TypePhrase → Perforation: at most 2 tokens (typically just a comma)

        Args:
            annotation_view_str: the merged annotation-view string from
                build_merged_representation().

        Returns:
            List[Annotation]: newly created StampDescription annotations.
        """
        regex_1 = TokenAnn.build_annotation_distance_regex('StampID', (0, 4), None, 'Denomination')
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Denomination',
                                verbose=self.verbose)

        regex_2 = TokenAnn.build_annotation_distance_regex('Denomination', (0, 8), None, 'TypePhrase')
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='TypePhrase',
                                verbose=self.verbose)

        regex_3 = TokenAnn.build_annotation_distance_regex('TypePhrase', (0, 2), None, 'Perforation')
        loop_3 = ExtractionLoop(regex_str=regex_3, last_ann_str='Perforation',
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=self.verbose)
        loop_3.when_final_match_found = when_final_match_found

        loop_list = [loop_1, loop_2, loop_3]
        result = run_loop(
            annotation_view_text=annotation_view_str,
            doc=self.doc_contents,
            curr_loop=loop_1,
            loop_idx=0,
            loops_in_process=[],
            loop_list=loop_list,
            match_triples_list=[],
            new_annotations=[],
            verbose=self.verbose)
        return result


if __name__ == '__main__':
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

    phase = StampDescriptionPhase(input_text, verbose=verbose)
    results = phase.run_phase()

    print(f'\n{len(results)} of 7 stamp descriptions extracted:\n')
    for ann in results:
        p = ann.properties
        print(f"  stamp_id='{p['stamp_id']}', denomination='{p['denomination']}', "
              f"type='{p['type']}', perforation_info='{p['perforation_info']}'")
