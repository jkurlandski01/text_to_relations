"""
"""
import re
from typing import List, Union, Tuple, Dict, Callable
from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC
from text_to_relations.relation_extraction.TokenAnn import TokenAnn


class ExtractionLoop():
    def __init__(self, 
                 regex_str: RegexString, 
                 last_ann_str: str,
                 determine_new_annotation_properties: Callable=None,
                 verbose :bool=False
                 ):
        self.regex_str = regex_str
        self.last_ann_str = last_ann_str
        self.when_final_match_found = when_final_match_found
        self.determine_new_annotation_properties = determine_new_annotation_properties
        self.verbose = verbose

        self.result = None

def when_final_match_found(args: Dict[str, object]) -> Annotation:
    loop: ExtractionLoop = args['loop']
    # text: str = args['text']
    doc: str = args['doc']
    triple: Tuple = args['triple']
    # loops_in_process: List[ExtractionLoop] = args['loops_in_process']
    match_triples_list: List[Tuple] = args['match_triples_list']
    if loop.verbose: print(f"\n  In when_final_match_found(). Found final match. triple: {triple}")

    # Get the starting position of the 1st match.
    text_matched = match_triples_list[0][0]
    if loop.verbose: 
        print(f"  text_matched: {text_matched}")
        print(f"  first's merged to annotations: {ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)}")
    m1_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
    start = m1_anns[0].start_offset

    # Get the ending position of the last annotation in the third match.
    text_matched = match_triples_list[-1][0]   # Ignore [1] and [2], the offsets.
    if loop.verbose: 
        print(f"  last's merged to annotations: {ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)}")
    m3_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
    end = m3_anns[-1].end_offset

    substr = doc[start:end]

    # Now invoke annotation-type specific functionality to determine the properties.
    properties = loop.determine_new_annotation_properties(match_triples_list, doc)

    # Finally we have everything we need for our new annotation.
    new_ann = Annotation('MinMax', substr, start, end, properties)

    if loop.verbose: print(f"  New annotation created: {new_ann}")

    return new_ann


def run_loop(annotation_view_text: str, 
             doc: str, 
             curr_loop: ExtractionLoop, 
             loop_idx: int, 
             loops_in_process: List[ExtractionLoop],
             loop_list: List[ExtractionLoop],
             match_triples_list: List[Tuple],
             new_annotations: List[Tuple],
             verbose: bool=False) -> Union[List[Annotation], Annotation, None]:
    """
    Args:
        annotation_view_text (str): A token- and annotation-view of the input where
            tokens we are not interested in appear as Tokens and annotations we
            are interested in appear as themselves. For example, 
                <'Token'(normalizedContents='for', start='99', end='101', kind='word')>
                <'CARDINAL'(normalizedContents='92', start='102', end='104')>
                <'UNIT_OF_MEASUREMENT'(normalizedContents='feet', start='111', end='115')>
            would represent "for 92 feet" if we have created annotations for Cardinal
            numbers and Units of Measurement.
        doc (str): the text as an ordinary string
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
        print(f"  annotation_view_text: {annotation_view_text}")
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
    match_triples = [(m.group(), m.start(), m.end()) for m in re.finditer(curr_loop.regex_str, annotation_view_text)]

    for triple in match_triples:
        match_triples_list.append(triple)
        if verbose: 
            print(f"\nFound match. triple: {triple}")
            print("  Printing the match_triples list:")
            for trip in match_triples_list:
                print(f"    trip: {trip}")

        if curr_loop.determine_new_annotation_properties:

            args_dict = {'loop': curr_loop, 'doc': doc, 'triple': triple, 
                            'match_triples_list': match_triples_list}
            result = curr_loop.when_final_match_found(args_dict)
            return result

        match_end_offset = triple[2]
        ptrn = f"<'{curr_loop.last_ann_str}"
        last_ann_st_offset = annotation_view_text[0 : match_end_offset].rfind(ptrn)
        text_substring = annotation_view_text[last_ann_st_offset : ]

        loops_in_process.append(curr_loop)
        new_idx = loop_idx + 1
        next_loop = loop_list[new_idx]

        result = run_loop(annotation_view_text=text_substring, 
                            doc=doc,
                            curr_loop=next_loop, loop_idx=new_idx, 
                            loops_in_process=loops_in_process, 
                            loop_list=loop_list,
                            match_triples_list=match_triples_list,
                            new_annotations=new_annotations,
                            verbose=verbose)
        if verbose: print(f"\nrun_loop result: {result}\n")
        if result is None or result == []:
            del match_triples_list[-1]
            continue
        elif type(result) == Annotation:
            if loop_idx == 0:
                new_annotations.append(result)
                # This next step results in non-overlapping annotations, and allows 
                # the program to continue through the input, attempting additonal
                # matches. 
                match_triples_list = []
                continue
            return result
        else:
            raise ValueError(f"Unexpected result: {result}")
        
        # Unreachable:
        # del match_triples_list[-1]

    return new_annotations

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
    # anns = []

    for key in regex_strs.keys():
        regex_str = regex_strs[key]
        triples = regex_str.get_match_triples(text)
        for triple in triples:
            ann = Annotation(key, triple[0], triple[1], triple[2])
            anns.append(ann)

    anns = Annotation.sort(anns)

    return anns

def determine_new_annotation_properties(match_triples: List[Tuple], doc:str) -> Dict[str, object]:
    # This is a function created specifically for the relation being extracted in
    # __main__.  It simply extracts the first and last character of the input text.

    # Commented out lines, however, show how to get specific information for the 
    # `match_triples` parameter which is passed into the function. Therefore,
    # DO NOT DELETE THE COMMENTED LINES.

    # Get the text of the first match.
    # text_matched = match_triples[0][0]

    # Get the contents of the first and last annotation which the first match matched.
    # m1_anns = ExtractionPhaseABC.merged_representation_to_Annotations(text_matched)
    # min = m1_anns[0].normalizedContents
    # max = m1_anns[-1].normalizedContents

    # Get the text of the last match.
    # text_matched = match_triples[-1][0]   # Ignore [1] and [2], the offsets.

    properties = {'first_character': doc[0], 'last_character': doc[-1]}

    return properties

if __name__ == '__main__':
    # You will probably have to `cd src` before you can run this script with
    #   python -m text_to_relations.relation_extraction.extraction_loo

    # Demo
    # Find the pattern "1...2...3" in text where no more than two tokens separate each digit.
    one_rs = RegexString(['1'])
    two_rs = RegexString(['2'])
    three_rs = RegexString(['3'])
    # regex_strs = [one_rs, two_rs, three_rs]
    regex_strs = {"One": one_rs, "Two": two_rs, "Three": three_rs}

    texts = [
        # matches 1 a 2 b 3
        "1 a 2 b 3",
        # matches 1 b 2 c d 3
        "1 a 1 b 2 c d 3",
        # matches 1 b 2 c 2 d 3
        "1 a 1 b 2 c 2 d 3",
        # matches 1 b 2 c 2 d 3
        "z 1 a 1 b 2 c 2 d 3 y",
        # Two matches 1 b 2 c 2 d 3, 1 2 3
        "z 1 a 1 b 2 c 2 d 3 y 1 2 3 x",
    ]

    output = []
    for text in texts:
        print("\n-----------------------\nStarting a new input text:\n")
        print(f"   {text}")
        anns = get_sorted_annotations_for_matching(text=text, regex_strs=regex_strs, given_anns=[])

        print(f"\nsorted anns: {anns}\n")

        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)
        print(f"annotation_view_str: {annotation_view_str}")

        regex_1 = TokenAnn.build_annotation_distance_regex("One", (0, 2), None, "Two")
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two', verbose=True)

        regex_2 = TokenAnn.build_annotation_distance_regex("Two", (0, 2), None, "Three")
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three', 
                                # when_final_match_found=when_final_match_found, 
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=True)

        print()
        loop_list = [loop_1, loop_2]
        loops_in_process = []
        result = run_loop(annotation_view_text=annotation_view_str,
                        doc=text, 
                        curr_loop=loop_1, 
                        loop_idx=0, 
                        loops_in_process=loops_in_process,
                        loop_list=loop_list, 
                        match_triples_list=[],
                        new_annotations=[],
                        verbose=True)

        output.append(result)

    for item in output:
        print(item)
