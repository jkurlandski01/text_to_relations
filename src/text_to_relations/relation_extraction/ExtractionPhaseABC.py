"""
Abstract base class for relation extraction--i.e., building
relations between previously-identified entities.
"""
import re
from abc import ABCMeta
from typing import Dict, List, Tuple

from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.Annotation import Annotation

class ExtractionPhaseABC(metaclass=ABCMeta):
    """
    Abstract base class of phases.
    """
    regexWhitespace = re.compile(r'\s+', re.IGNORECASE | re.DOTALL | re.MULTILINE)

    def __init__(self, doc_contents: str, verbose: bool = False):
        """
        Args:
            doc_contents (str): the normalized contents of the
                document being processed
            verbose (bool): if True, print internal state at each step.
        """
        if doc_contents is None or doc_contents == '':
            msg = "doc_contents is empty or None. "
            msg += "An extraction phase object requires a document to process."
            raise TypeError(msg)
        self.doc_contents = doc_contents
        self.verbose = verbose

    def run_phase(self) -> List[Annotation]:
        """
        Splits the document on blank lines and runs check_annotation_proximity()
        on each entry, returning the combined results.
        """
        entries = [e.strip() for e in re.split(r'\n\s*\n', self.doc_contents) if e.strip()]
        results = []
        for entry in entries:
            results.extend(self.check_annotation_proximity(entry))
        return results

    def check_annotation_proximity(self, text: str) -> List[Annotation]:
        """
        Given a single text entry, define the annotation regex patterns and
        proximity chain, then call self.run_chained_loops() and return its result.

        Subclasses that use the default run_phase() must override this method.
        Subclasses that override run_phase() directly do not need to.

        Args:
            text: a single document entry to process.

        Returns:
            List[Annotation]: newly created relation annotations.
        """
        raise NotImplementedError("Subclasses using the default run_phase() must implement check_annotation_proximity().")

    def run_chained_loops(self, text: str, result_ann_type: str,
                          regex_patterns: Dict[str, object],
                          chain: List[Tuple[str, Tuple[int, int], str]]) -> List[Annotation]:
        """
        Build annotations from regex_patterns, then run a chain of proximity
        loops and return the resulting relation annotations.

        Args:
            text: the document entry to process.
            result_ann_type: the annotation type name for newly created relations
                (e.g. 'StampDescription').
            regex_patterns: dict mapping annotation type name to RegexString.
            chain: list of (start_type, (min_dist, max_dist), end_type) tuples
                defining the proximity constraints between consecutive annotation
                types.

        Returns:
            List[Annotation]: newly created relation annotations.
        """
        from text_to_relations.relation_extraction.extraction_loop import (
            ExtractionLoop, run_loop, get_sorted_annotations_for_matching)

        anns = get_sorted_annotations_for_matching(text=text, regex_strs=regex_patterns, given_anns=[])
        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        def _determine_properties(match_triples, doc):
            properties = {}
            for triple in match_triples:
                for ann in ExtractionPhaseABC.merged_representation_to_Annotations(triple[0]):
                    if ann.type != 'Token':
                        properties[ann.type] = ann.normalizedContents
            return properties

        def _when_final_match_found(args):
            loop = args['loop']
            doc = args['doc']
            triple = args['triple']
            match_triples_list = args['match_triples_list']
            if loop.verbose:
                print(f"\n  In when_final_match_found(). Found final match. triple: {triple}")
            m0_anns = ExtractionPhaseABC.merged_representation_to_Annotations(match_triples_list[0][0])
            start = m0_anns[0].start_offset
            m_last_anns = ExtractionPhaseABC.merged_representation_to_Annotations(match_triples_list[-1][0])
            end = m_last_anns[-1].end_offset
            substr = doc[start:end]
            properties = loop.determine_new_annotation_properties(match_triples_list, doc)
            new_ann = Annotation(result_ann_type, substr, start, end, properties)
            if loop.verbose:
                print(f"  New annotation created: {new_ann}")
            return new_ann

        loops = []
        for i, (start_type, distance, end_type) in enumerate(chain):
            is_last = (i == len(chain) - 1)
            regex = TokenAnn.build_annotation_distance_regex(start_type, distance, None, end_type)
            loop = ExtractionLoop(
                regex_str=regex,
                last_ann_str=end_type,
                determine_new_annotation_properties=_determine_properties if is_last else None,
                verbose=self.verbose
            )
            if is_last:
                loop.when_final_match_found = _when_final_match_found
            loops.append(loop)

        return run_loop(
            annotation_view_text=annotation_view_str,
            doc=text,
            curr_loop=loops[0],
            loop_idx=0,
            loops_in_process=[],
            loop_list=loops,
            match_triples_list=[],
            new_annotations=[],
            verbose=self.verbose
        )

    @staticmethod
    def build_merged_representation(doc_contents: str,
                                    anns: List[Annotation],
                                    verbose: bool=False) -> str:
        """
        Create an Annotation-only representation of the document by
        merging the given bespoke annotations on it into a TokenAnn list
        for all the other tokens in the doc.
        Args:
            doc_contents (str): the normalized contents of the doc being
                processed
            anns (List[Annotation]): a list of bespoke annotations you want
                to appear merged into the doc
            verbose (bool, optional): Defaults to False.

        Raises:
            ValueError: If the process fails to insert any of the provided
                bespoke annotations into the final result

        Returns:
            str: a string representing all the annotations in the document,
                sorted by offset
        """
        contents = doc_contents.rstrip()

        # If this is empty after the process, something may be wrong.
        unconsumedAnnotations = anns

        result = ""
        lastPos = 0

        # Strategy: Tokenize the doc and iterate through all the tokens. If a token
        # is covered by an annotation, write that annotation to the output and advance
        # lastPos to the end of the annotation; otherwise, write the token to output
        # and continue.
        tokensObjs = TokenAnn.get_token_objects(contents, 0)

        for tokenObj in tokensObjs:

            if lastPos > tokenObj.start_offset:
                continue

            tempAnns = unconsumedAnnotations
            foundAnn = False
            for ann in tempAnns:
                if ann.start_offset <= tokenObj.start_offset:
                    # Write the annotation and remove it from the unconsumedAnnotations.
                    unconsumedAnnotations = unconsumedAnnotations[1:]
                    result += str(ann)
                    if verbose:
                        print(str(ann))
                    lastPos = ann.end_offset
                    foundAnn = True
                else:
                    break

            if foundAnn:
                continue

            # This token occurs in the document before the next unconsumed annotation. Write it to
            # output.
            result += str(tokenObj)

            lastPos = tokenObj.end_offset

        # Verify that all the annotations have been consumed.
        if len(unconsumedAnnotations) > 0:
            msg = "Final annotations in the anns parameter not inserted into the merged document."
            msg += f"  uncomsumed annotations: {unconsumedAnnotations}"
            raise ValueError(msg)

        return result


    @staticmethod
    def merged_representation_to_Annotations(rep: str,
                                    verbose: bool=False) -> List[Annotation]:
        """
        Essentially reverses build_merged_representation(). From a merged representation,
        or a subset thereof, create a list of Annotations.
        Args:
            rep (str): merged representation, e.g. a string looking like this
                (ignore the backslashes):
                    <'CARDINAL'(normalizedContents='80', start='92', end='94')> \
                    <'Token'(normalizedContents='to', start='95', end='97', kind='word')> \
                    <'CARDINAL'(normalizedContents='90', start='98', end='100')>
            verbose (bool, optional): Defaults to False.

        Returns:
            List[Annotation]:
        """
        # Each ann is contained within angle brackets--<>.
        incomplete_strs = rep.split('<')
        complete_strs = []
        for in_str in incomplete_strs:
            if not in_str:
                continue
            if verbose: print(f"in_str: {in_str}")
            complete_strs.append('<' + in_str)
        if verbose: print(f"complete_strs: {complete_strs}")
        anns = [Annotation.str_to_Annotation(c_str) for c_str in complete_strs]
        return anns
