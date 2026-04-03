from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC, ChainLink
from text_to_relations.relation_extraction.RegexString import RegexString


class MinMaxPhase_3(ExtractionPhaseABC):
    def __init__(self, verbose: bool = False):
        """
        Identify MinMax ranges expressed as two noun phrases following this pattern:
            <at least> Number + UoM and <at most> Number + UoM
        Example:
            a minimum of 15 minutes and a maximum of 20 minutes
        """
        super().__init__(verbose=verbose)
        self.relation_name = 'MinMax'

        at_least_rs = RegexString(['at least', 'lower limit', 'minimum of', 'no less than'])
        at_most_rs = RegexString(['at most', 'upper limit', 'maximum of', 'no more than'])

        self.regex_patterns = {'AtLeast': at_least_rs, 'AtMost': at_most_rs}
        self.chain = [
            ChainLink(start_type='AtLeast', start_property='at_least',
                      min_distance=0, max_distance=3,
                      end_type='Number', end_property='min_number'),
            ChainLink(start_type='Number', start_property='min_number',
                      min_distance=0, max_distance=2,
                      end_type='Unit_of_Measure', end_property='min_unit'),
            ChainLink(start_type='Unit_of_Measure', start_property='min_unit',
                      min_distance=0, max_distance=5,
                      end_type='AtMost', end_property='at_most'),
            ChainLink(start_type='AtMost', start_property='at_most',
                      min_distance=0, max_distance=3,
                      end_type='Number', end_property='max_number'),
            ChainLink(start_type='Number', start_property='max_number',
                      min_distance=0, max_distance=2,
                      end_type='Unit_of_Measure', end_property='max_unit'),
        ]
