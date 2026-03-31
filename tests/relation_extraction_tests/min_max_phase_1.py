from typing import List

from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink
from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation


class MinMaxPhase_1(ExtractionPhaseABC):
    def __init__(self, verbose: bool = False):
        """
        Identify phrases like 'between 170 and 220 pounds' and
        'within the range of 60 to 90 points' by looking for:
            RangeMarker + Number + Number + Unit_of_Measure
        """
        super().__init__(verbose=verbose)
        self.relation_name = 'MinMax'

        range_markers = ['within the range of', 'within', 'between']
        range_marker_rs = RegexString(range_markers)

        self.regex_patterns = {'RangeMarker': range_marker_rs}
        self.chain = [
            ChainLink('RangeMarker', 'range_marker', 0, 3, 'Number',          'min_number'),
            ChainLink('Number',      'min_number',   0, 2, 'Number',          'max_number'),
            ChainLink('Number',      'max_number',   0, 2, 'Unit_of_Measure', 'unit'),
        ]
