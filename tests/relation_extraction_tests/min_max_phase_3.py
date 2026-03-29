"""
Module avoids repetitive lines of code with new recursive functionality offered in extraction_loop.py.
"""
import re

from typing import List, Tuple, Dict

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC
from text_to_relations.relation_extraction.TokenAnn import TokenAnn

from text_to_relations.relation_extraction.extraction_loop import (
    ExtractionLoop, run_loop, get_sorted_annotations_for_matching)


class MinMaxPhase_3(ExtractionPhaseABC):
    def __init__(self, doc_contents:str, 
                 given_annotations: List[Annotation],
                 verbose: bool=False):
        """
        Identify MinMax ranges expressed as two noun phrases following this pattern:
            <at least> Number + UoM and <at most> Number + Uom
        Example: 
            a minimum of 15 minutes and a maximum of 20 minutes
        Args:
            doc_contents (str): normalized contents of the document
                being processed
            given_annotations (List[Annotation]): list of annotations/
                entities which are going to be used to form new
                relations
            verbose (bool, optional): Defaults to False.
        """
        super().__init__(doc_contents)

        required_annotation_types = ['Number', 'Unit_of_Measure']
        self.given_annotations = []
        for ann in given_annotations:
            if ann.type not in required_annotation_types:
                continue
            self.given_annotations.append(ann)
        self.verbose = verbose

        if self.verbose:
            print(f"self.given_annotations: {self.given_annotations}")
        

    def run_phase(self) -> List[Annotation]:
        """
        Find MinMax entities for the given document and annotations.
        Returns:
            List[Annotation]: list of annotations whose type is 'MinMax'
        """
        # Use RegexString to create our own annotations (entities).
        at_least_markers = ['at least', 'lower limit', 'minimum of',
                            'no less than']
        at_least_rs = RegexString(at_least_markers)

        at_most_markers = ['at most', 'upper limit', 'maximum of',
                           'no more than']
        at_most_rs = RegexString(at_most_markers)

        regex_strs = {"AtLeast": at_least_rs, "AtMost": at_most_rs}
        anns = get_sorted_annotations_for_matching(text=self.doc_contents, 
                                                         regex_strs=regex_strs,
                                                         given_anns=self.given_annotations)

        if self.verbose: print(f"\nsorted anns: {anns}\n")
        
        # Replace the text document with a new representation in which every 
        # token is an element--except those tokens which are overlapped by
        # one of our previously-created annotations/entities.
        annotation_view_str = ExtractionPhaseABC.build_merged_representation(self.doc_contents, anns)

        # Display each token or annotation on its own line.
        if self.verbose:
            ann_list = ExtractionPhaseABC.merged_representation_to_Annotations(annotation_view_str)
            for ann in ann_list:
                print(f"ann: {ann}")

        new_annotations = self.check_annotation_proximity(annotation_view_str=annotation_view_str)
        return new_annotations

    def check_annotation_proximity(self, annotation_view_str: List[Annotation]) -> List[Annotation]:
        """
        Look for parts of the text where the annotations we are interested in are in close 
        proximity.
        
        Args:
            annotation_view_str (List[Annotation]): the annotation-only representation of the 
                input document

        Returns:
            List[Annotation]: a list of any new annotations created
        """
        if self.verbose: print(f"\nEntering check_annotation_proximity( ).")

        regex_1 = TokenAnn.build_annotation_distance_regex("AtLeast", (0, 3), None, "Number")
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Number', verbose=self.verbose)

        regex_2 = TokenAnn.build_annotation_distance_regex("Number", (0, 2), None, "Unit_of_Measure")
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Unit_of_Measure', 
                                verbose=self.verbose)

        regex_3 = TokenAnn.build_annotation_distance_regex("Unit_of_Measure", (0, 5), None, "AtMost")
        loop_3 = ExtractionLoop(regex_str=regex_3, last_ann_str='AtMost', 
                                verbose=self.verbose)

        regex_4 = TokenAnn.build_annotation_distance_regex("AtMost", (0, 3), None, "Number")
        loop_4 = ExtractionLoop(regex_str=regex_4, last_ann_str='Number', verbose=self.verbose)

        regex_5 = TokenAnn.build_annotation_distance_regex("Number", (0, 2), None, "Unit_of_Measure")
        loop_5 = ExtractionLoop(regex_str=regex_5, last_ann_str='Unit_of_Measure', 
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=self.verbose)

        loop_list = [loop_1, loop_2, loop_3, loop_4, loop_5]
        loops_in_process = []
        result = run_loop(annotation_view_text=annotation_view_str,
                        doc=self.doc_contents, 
                        curr_loop=loop_1, 
                        loop_idx=0, 
                        loops_in_process=loops_in_process,
                        loop_list=loop_list, 
                        match_triples_list=[],
                        new_annotations=[],
                        verbose=self.verbose)
        return result


def determine_new_annotation_properties(match_triples: List[Tuple], doc:str) -> Dict[str, object]:
    # Get the text of the first match.
    text_matched = match_triples[0][0]
    # Get the contents of the last annotation which the first match matched.
    m0_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
    min = m0_anns[-1].normalizedContents
    # max = m1_anns[-1].normalizedContents

    # Get the text of the fourth match.
    text_matched = match_triples[3][0]
    # Get the contents of the last annotation which the fourth match matched.
    m3_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
    max = m3_anns[-1].normalizedContents

    # The UoM can be obtained from either the third or the last match. We'll assume
    # the two are the same.
    # Get the text of the last match.
    text_matched = match_triples[-1][0]   # Ignore [1] and [2], the offsets.
    # Get the contents of the last annotation which this match matched.
    m5_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
    uom = m5_anns[-1].normalizedContents

    properties = {'min': min, 'max': max, 'unit_of_measure': uom}

    return properties

