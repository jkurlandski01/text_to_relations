import re

from typing import List

from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC
from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.TokenAnn import TokenAnn

class MinMaxPhase_2(ExtractionPhaseABC):

    def __init__(self, doc_contents:str, 
                 given_annotations: List[Annotation],
                 verbose: bool=False):
        """
        Identify phrases like '30 to 40 drinks' by looking for:
            Number + ToMarker + Number + Unit_of_Measure

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
        to_markers = ['to', '-']
        regex_str = RegexString(to_markers)

        to_anns = []
        triples = regex_str.get_match_triples(self.doc_contents)
        for triple in triples:
            ann = Annotation('ToMarker', triple[0], triple[1], triple[2])
            to_anns.append(ann)

        if self.verbose: print(f"to_anns: {to_anns}")

        # Sort all annotations by offset.
        anns = self.given_annotations
        anns.extend(to_anns)
        anns = Annotation.sort(anns)
        if self.verbose: print(f"\nsorted anns: {anns}\n")
        
        # Replace the text document with a new representation in which every 
        # token is an element--except those tokens which are overlapped by
        # one of our previously-created annotations/entities.
        annotation_view_str = ExtractionPhaseABC.build_merged_representation(self.doc_contents, anns)

        if self.verbose:
            # Display each token or annotation on its own line.
            ann_list = ExtractionPhaseABC.merged_representation_to_Annotations(annotation_view_str)
            for ann in ann_list:
                print(f"ann: {ann}")

        new_annotations = self.check_annotation_proximity(annotation_view_str=annotation_view_str)
        return new_annotations

    def check_annotation_proximity(self, annotation_view_str: List[Annotation]) -> List[Annotation]:
        """
        Look for parts of the text where the annotations we are interested
        in are in close proximity.
        
        Args:
            annotation_view_str (List[Annotation]): the annotation-only representation of the 
                input document

        Returns:
            List[Annotation]: a list of any new annotations created
        """
        if self.verbose: print(f"\nEntering check_annotation_proximity( ).")

        new_annotations = []

        regex_1 = TokenAnn.build_annotation_distance_regex("Number", (0, 3), None, "ToMarker")

        # Create a list of (substring, start_offset, end_offset) triples for Number + ToMarker.
        match_1_triples = [(m.group(), m.start(), m.end()) for m in re.finditer(regex_1, annotation_view_str)]

        # Triple-nested for loop which tests for four annotations in the correct order and
        # in close proximity in order to form a MinMax relation. An annotation can belong
        # to only one relation, and no relations overlap.
        # This means that if a relation is created, we want to break from both Loop 3
        # and Loop 2, and continue on Loop 1. We implement this behavior using a
        # `breaking` flag. 
        # Moreover, for the sake of efficiency, when we continue with the outer loop
        # we don't want the restarted inner loops to iterate over annotations that 
        # precede the end of the previous loop's match. We implement this with checks at 
        # the start of the inner loops, e.g. "if m1_trip[1] > m2_trip[1]:"
        for m1_trip in match_1_triples:
            breaking = False
            if self.verbose: print(f"\nFound first match. m1_trip: {m1_trip}")

            regex_2 = TokenAnn.build_annotation_distance_regex("ToMarker", (0, 2), None, "Number")
            # Create a list of (substring, start_offset, end_offset) triples for ToMarker + Number.
            match_2_triples = [(m.group(), m.start(), m.end()) for m in re.finditer(regex_2, annotation_view_str)]

            for m2_trip in match_2_triples:
                if breaking is True:
                    break
                if self.verbose: print(f"\n  Found second match. m2_trip: {m2_trip}")

                if m1_trip[1] > m2_trip[1]:
                    continue

                regex_3 = TokenAnn.build_annotation_distance_regex("Number", (0, 2), None, "Unit_of_Measure")
                # Create a list of (substring, start_offset, end_offset) triples for Number + UoM.
                match_3_triples = [(m.group(), m.start(), m.end()) for m in re.finditer(regex_3, annotation_view_str)]

                for m3_trip in match_3_triples:
                    if self.verbose: print(f"\n    Found third match. m3_trip: {m3_trip}")

                    if m2_trip[1] > m3_trip[1]:
                        continue
                    # Create the new relation, which spans from the start of the first Number to the
                    # end of the Unit_of_Measurement.

                    # Get the starting position of the Number in the first match.
                    # Ignore [1] and [2], the offsets of the Number-ToMarker 
                    # match in the merged representation.
                    text_matched = m1_trip[0]   
                    m1_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
                    start = m1_anns[0].start_offset

                    # Get the ending position of the last annotation in the third match.
                    text_matched = m3_trip[0]   # Ignore [1] and [2], the offsets.
                    m3_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
                    end = m3_anns[1].end_offset

                    substr = self.doc_contents[start:end]

                    # Finally we have everything we need for our new annotation.
                    min_max = Annotation('MinMax', substr, start, end)

                    if self.verbose: print(f"New annotation created: {min_max}")

                    new_annotations.append(min_max)
                    breaking = True
                    break

        if self.verbose:
            print("\nNew annotations:")
            for new_ann in new_annotations:
                print(f"  {new_ann}")
            print()

        return new_annotations
