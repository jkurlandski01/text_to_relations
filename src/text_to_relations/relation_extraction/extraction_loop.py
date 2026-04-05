"""
Low-level machinery for chained proximity matching.

ExtractionLoop holds the configuration for one step in a chain, and
run_loop() recursively executes a list of ExtractionLoop objects against
an annotation-view string to produce relation Annotations.

Most callers should use ExtractionPhaseABC and its run_chained_loops()
method rather than calling these directly.
"""
import re
from typing import List, Union, Tuple, Dict, Callable, Optional
from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC


class ExtractionLoop():
    """
    Configuration object for one step in a chained proximity search.

    A relation is extracted by chaining multiple ExtractionLoop objects together
    and passing them to run_loop(). Each loop holds a regex that matches one
    entity-to-entity proximity pattern against the annotation-view string. When
    a loop matches, the end of its match becomes the starting point for the next
    loop's search. When the final loop matches, run_loop() assembles the result
    Annotation spanning all matched entities.

    All loops except the last must have determine_new_annotation_properties=None.
    The last loop must have determine_new_annotation_properties set.
    """
    def __init__(self,
                 regex_str: str,
                 last_ann_str: str,
                 determine_new_annotation_properties: Optional[Callable]=None,
                 verbose: bool = False
                 ):
        """
        Args:
            regex_str (str): Regular expression for this loop's match. If you have a
                RegexString object, pass regex_str.get_regex_str() instead.
            last_ann_str (str): The annotation type name that marks the
                end of this loop's match and the handoff point to the next loop.
            determine_new_annotation_properties (Callable, optional): A function that
                produces the properties dict for the new Annotation. Must be None for
                all loops except the last, and non-None for the last loop.
            verbose (bool, optional): Defaults to False.

        Raises:
            ValueError: If regex_str is not a str.
        """
        if not isinstance(regex_str, str):
            raise ValueError(
                "regex_str must be a str. If you have a RegexString object, "
                "pass regex_str.get_regex_str() instead."
            )
        self.regex_str = regex_str
        self.last_ann_str = last_ann_str
        self.determine_new_annotation_properties = determine_new_annotation_properties
        self.verbose = verbose
        self.result = None


def run_loop(annotation_view_str: str,
             doc: str,
             relation_name: str,
             curr_loop: ExtractionLoop,
             loop_idx: int,
             loops_in_process: List[ExtractionLoop],
             loop_list: List[ExtractionLoop],
             match_triples_list: List[Tuple],
             new_annotations: List[Annotation],
             verbose: bool=False) -> Union[List[Annotation], Annotation, None]:
    """
    Recursively execute a chain of ExtractionLoop objects against the
    annotation-view string, accumulating result Annotations.

    Each call attempts to match curr_loop's regex against annotation_view_str.
    For each match found, the function recurses into the next loop, starting
    the search from the end of the current match. When the final loop matches,
    a result Annotation is built spanning all matched entities and returned.
    Non-matching paths are backtracked; all successful matches at the top level
    (loop_idx == 0) are accumulated and returned together.

    Args:
        annotation_view_str (str): merged annotation-view of the input document,
            as produced by ExtractionPhaseABC.build_merged_representation().
        doc (str): the text as an ordinary string.
        relation_name (str): type name assigned to each successfully extracted
            relation Annotation (e.g. 'MinMax').
        curr_loop (ExtractionLoop): loop being processed
        loop_idx (int): which loopin loops_in_process we are processing
        loops_in_process (List[ExtractionLoop]): the loops which have been processed
            successfully to get this far in the recursion
        loop_list (List[ExtractionLoop]): all the loops which have been set up
        match_triples_list (List[Tuple]): matches found thus far for the loops processed
            thus far
        new_annotations (List[Tuple]): matches successfully found thus far
        verbose (bool, optional): Defaults to False.

    Raises:
        ValueError: For invalid input or unexpected results.
    Returns:
        Union[List[Annotation], Annotation, None]: A new match found or [] or None.
    """
    if verbose:
        print("Entering run_loop()")
        print(f"  annotation_view_str: {annotation_view_str}")
        print(f"  curr_loop.regex_str: {curr_loop.regex_str}")
        print(f"  curr_loop.last_ann_str: {curr_loop.last_ann_str}")
        print(f"  new_annotations: {new_annotations}")

    # Check loop_list to verify that only the last item has a non-None
    # determine_new_annotation_properties function.
    last_idx = len(loop_list) - 1
    for idx, loop in enumerate(loop_list):
        if loop.determine_new_annotation_properties:
            if idx < last_idx:
                msg = "Only last element of loop_list parameter can have "
                msg += "a non-None determine_new_annotation_properties "
                msg += f"attribute. Loop at index {idx} has "
                msg += f"{loop.determine_new_annotation_properties}() function."
                raise ValueError(msg)
        else:
            if idx == last_idx:
                msg = "The last element of loop_list parameter must have "
                msg += "a non-None determine_new_annotation_properties "
                msg += f"attribute. Loop at index {idx} has "
                msg += f"{loop.determine_new_annotation_properties}() function."
                raise ValueError(msg)

    if verbose:
        print("  Printing the match_triples list:")
        for trip in match_triples_list:
            print(f"    trip: {trip}")

    # Recursive functionality begins here.

    # Create a list of (substring, start_offset, end_offset) triples for the current loop's regex string.
    match_triples = [(m.group(), m.start(), m.end())
                     for m in re.finditer(curr_loop.regex_str, annotation_view_str)]

    for triple in match_triples:
        match_triples_list.append(triple)
        if verbose:
            print(f"\nFound match. triple: {triple}")
            print("  Printing the match_triples list:")
            for trip in match_triples_list:
                print(f"    trip: {trip}")

        if curr_loop.determine_new_annotation_properties:
            if verbose:
                print(f"\n  Found final match. triple: {triple}")
            m0_anns = ExtractionPhaseABC.merged_representation_to_annotations(
                match_triples_list[0][0])
            start = m0_anns[0].start_offset
            m_last_anns = ExtractionPhaseABC.merged_representation_to_annotations(
                match_triples_list[-1][0])
            end = m_last_anns[-1].end_offset
            substr = doc[start:end]
            properties = curr_loop.determine_new_annotation_properties(match_triples_list)
            result = Annotation(relation_name, substr, start, end, properties)
            if verbose:
                print(f"  New annotation created: {result}")
            return result

        match_end_offset = triple[2]
        ptrn = f"<'{curr_loop.last_ann_str}"
        last_ann_st_offset = annotation_view_str[0 : match_end_offset].rfind(ptrn)
        text_substring = annotation_view_str[last_ann_st_offset : ]

        loops_in_process.append(curr_loop)
        new_idx = loop_idx + 1
        next_loop = loop_list[new_idx]

        recursive_result = run_loop(annotation_view_str=text_substring,
                            doc=doc,
                            relation_name=relation_name,
                            curr_loop=next_loop, loop_idx=new_idx,
                            loops_in_process=loops_in_process,
                            loop_list=loop_list,
                            match_triples_list=match_triples_list,
                            new_annotations=new_annotations,
                            verbose=verbose)
        if verbose:
            print(f"\nrun_loop result: {recursive_result}\n")
        if recursive_result is None or recursive_result == []:
            del match_triples_list[-1]
            continue
        if isinstance(recursive_result, Annotation):
            if loop_idx == 0:
                new_annotations.append(recursive_result)
                # This next step results in non-overlapping annotations, and allows
                # the program to continue through the input, attempting additonal
                # matches.
                match_triples_list = []
                continue
            return recursive_result
        raise ValueError(f"Unexpected result: {recursive_result}")

    # Only the top-level call (loop_idx == 0) should return the accumulated results list.
    # Intermediate loops return [] to signal "no match found" to their caller; returning
    # new_annotations from an intermediate loop would pass the shared results list up the
    # call stack, where it would be mistaken for an unexpected result type and raise ValueError.
    return new_annotations if loop_idx == 0 else []

def get_sorted_annotations_for_matching(text: str,
                                        regex_strs: Dict[str, RegexString],
                                        given_anns: List[Annotation]) -> List[Annotation]:
    """
    Return a sorted list of annotations for the next matching phase.

    Args:
        text (str): the text being processed
        regex_strs (Dict[str, RegexString]): Dict whose key is the name of an
            annotation and whose value is a new RegexString needed for
            the next phase of matching. The RegexStrings create new annotations
            needed for this phase only.
        given_anns (List[Annotation]): List of annotations created before this
            phase began but needed by the phase.

    Returns:
        List[Annotation]: List of all the annotations needed for this phase, sorted
            by offset.
    """
    anns = given_anns

    for key in regex_strs.keys():
        regex_str = regex_strs[key]
        triples = regex_str.get_match_triples(text)
        for triple in triples:
            ann = Annotation(key, triple[0], triple[1], triple[2])
            anns.append(ann)

    anns = Annotation.sort(anns)

    return anns
