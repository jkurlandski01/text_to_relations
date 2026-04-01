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
            ChainLink('Number',   'min_number', 0, 3, 'ToMarker',        'to_marker'),
            ChainLink('ToMarker', 'to_marker',  0, 2, 'Number',          'max_number'),
            ChainLink('Number',   'max_number', 0, 2, 'Unit_of_Measure', 'unit'),
        ]
