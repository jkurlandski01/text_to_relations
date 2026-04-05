"""
Convert entity information into specific pre-determined relations
between those entities.
"""

from typing import Dict, List
import inspect

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from tests.relation_extraction_tests.min_max_phase_1 import MinMaxPhase_1
from tests.relation_extraction_tests.min_max_phase_2 import MinMaxPhase_2
from tests.relation_extraction_tests.min_max_phase_3 import MinMaxPhase_3


def update_annotation_list(prev_anns: List[Annotation],
                           new_anns: List[Annotation]) -> List[Annotation]:
    """
    Remove from the list of previous annotations any which form part of the
    new annotations. This prevents the next set of MinMax rules from
    matching on the "consumed" annotations.

    Args:
        prev_anns (List[Annotation]): The annotation list used to form
            a previous MinMax extraction.
        new_anns (List[Annotation]): The output of the previous MinMax
            extraction, which consumed some of the prev_anns annotations.

    Returns:
        List[Annotation]: prev_anns - new_anns
    """
    # Remove from the input annotations any which form part of the new
    # MinMax annotations.
    enclosed = []
    for mm_ann in new_anns:
        enclosed.extend(Annotation.get_enclosed(mm_ann, prev_anns))
    remaining_annotations = [x for x in prev_anns if x not in enclosed]

    # After this, remaining_annotations will contain the newly-found MinMax annotations
    # plus any unconsumed Cardinal and Unit_of_Measure annotations.
    remaining_annotations.extend(new_anns)

    return remaining_annotations




def run_extraction_phases(input: str,
                          anns: List[Annotation],
                          verbose: bool=False) -> List[Annotation]:
    if verbose: print(f"\nEntering run_extraction_phases(). anns: {anns}\n")

    phase_1 = MinMaxPhase_1(verbose=verbose)
    minmax_anns_1 = phase_1.find_match(input, anns)
    if verbose:
        msg = f"\nReturned to run_extraction_phases(). minmax_anns: {minmax_anns_1}"
        print(msg)

    # Filter from the previous annotation list any which are consumed
    # by the newly-found MinMax relations.
    anns_2 = update_annotation_list(prev_anns=anns, new_anns=minmax_anns_1)

    if verbose: print(f"  Filtered anns_2 annotations: {anns_2}\n")

    phase_2 = MinMaxPhase_2(verbose=verbose)
    minmax_anns_2 = phase_2.find_match(input, anns_2)

    anns_3 = update_annotation_list(prev_anns=anns_2, new_anns=minmax_anns_2)

    phase_3 = MinMaxPhase_3(verbose=verbose)
    minmax_anns_3 = phase_3.find_match(input, anns_3)

    result = minmax_anns_1 + minmax_anns_2 + minmax_anns_3
    return Annotation.sort(result)



def entities_to_annotations(entities: List[Dict[str, str]]) -> List[Annotation]:
    annotations = []
    for entity in entities:
        type = entity['type']
        start = entity['start']
        end = entity['end']
        text = entity['text']
        ann = Annotation(type, text, start, end)

        annotations.append(ann)

    return annotations

def entities_to_relations(input_dict: Dict[str, object],
                          verbose: bool=False) -> List[Dict[str, str]]:
    input_text = input_dict["text"]

    annotations = entities_to_annotations(input_dict["entities"])
    if verbose: print(f"Annotations created: {annotations}")

    new_anns = run_extraction_phases(input_text, annotations, verbose=verbose)

    if verbose:
        print(f"\nannotations: {annotations}")
        print(f"new_anns: {new_anns}\n")

    result = [x.to_dict() for x in new_anns]

    return result


if __name__ == '__main__':

    text = \
    """
    During those fraught times his weight ranged between 170 and 220 pounds
    and, with the 30 to 40 drinks per week he was inclined to enjoy, his IQ
    varied almost as much--anywhere within the range of 60 to 90 points. It
    would take him a minimum of 15 minutes and a maximum of 20 minutes to
    run a mile.
    """
    input = inspect.cleandoc(text)

    entities = []

    # Write rules for two types of entities--Number and Unit_of_Measurement.
    number_rs = RegexString.from_regex('(\d+)')
    matches = number_rs.get_match_triples(text)
    print("\nNumbers and offsets:")
    for match in matches:
        entity_dict = {
            'text': match[0],
            'start': match[1],
            'end': match[2],
            'type': 'Number'
        }
        entities.append(entity_dict)
        print(entity_dict)

    uom_rs = RegexString(['pounds', 'drinks', 'points', 'minutes'])
    matches = uom_rs.get_match_triples(text)
    print("\nUnits of measure and offsets:")
    for match in matches:
        entity_dict = {
            'text': match[0],
            'start': match[1],
            'end': match[2],
            'type': 'Unit_of_Measure'
        }
        entities.append(entity_dict)
        print(entity_dict)

    input_dict = {
        "text": text,
        "entities": entities
        }

    print()

    relations = entities_to_relations(input_dict, verbose=True)

    print(f"\nPrinting final output...")
    print(relations)
