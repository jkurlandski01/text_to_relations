from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink
from text_to_relations.relation_extraction.RegexString import RegexString


class MinMaxPhase_2(ExtractionPhaseABC):
    def __init__(self, verbose: bool = False):
        """
        Identify phrases like '30 to 40 drinks' by looking for:
            Number + ToMarker + Number + Unit_of_Measure
        """
        super().__init__(verbose=verbose)
        self.relation_name = 'MinMax'

        to_markers = ['to', '-']
        to_marker_rs = RegexString(to_markers)

        self.regex_patterns = {'ToMarker': to_marker_rs}
        self.chain = [
            ChainLink(start_type='Number', start_property='min_number',
                      min_distance=0, max_distance=3,
                      end_type='ToMarker', end_property='to_marker'),
            ChainLink(start_type='ToMarker', start_property='to_marker',
                      min_distance=0, max_distance=2,
                      end_type='Number', end_property='max_number'),
            ChainLink(start_type='Number', start_property='max_number',
                      min_distance=0, max_distance=2,
                      end_type='Unit_of_Measure', end_property='unit'),
        ]
