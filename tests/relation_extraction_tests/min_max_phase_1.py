from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink
from text_to_relations.relation_extraction.RegexString import RegexString


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
            ChainLink(start_type='RangeMarker', start_property='range_marker',
                      min_distance=0, max_distance=3,
                      end_type='Number', end_property='min_number'),
            ChainLink(start_type='Number', start_property='min_number',
                      min_distance=0, max_distance=2,
                      end_type='Number', end_property='max_number'),
            ChainLink(start_type='Number', start_property='max_number',
                      min_distance=0, max_distance=2,
                      end_type='Unit_of_Measure', end_property='unit'),
        ]
