from typing import List

from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC
from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation


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
            ('AtLeast',         (0, 3), 'Number'),
            ('Number',          (0, 2), 'Unit_of_Measure'),
            ('Unit_of_Measure', (0, 5), 'AtMost'),
            ('AtMost',          (0, 3), 'Number'),
            ('Number',          (0, 2), 'Unit_of_Measure'),
        ]
