"""
Convert entity information into specific pre-determined relations
between those entities.
"""

from typing import Dict, List
from pathlib import Path
import sys

import inspect

# All project imports must occur after we have updated the path.
path = Path(__file__).absolute()
path = path.parent.parent.parent
print(f"Appending to system path: {str(path)}")
sys.path.append(str(path))

from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.min_max_phase_1 import MinMaxPhase_1
from text_to_relations.relation_extraction.min_max_phase_2 import MinMaxPhase_2


def run_extraction_phases(input: str, 
                          anns: List[Annotation],
                          verbose: bool=False) -> List[Annotation]:
    if verbose: print(f"\nEntering run_extraction_phases(). anns: {anns}\n")
    extraction_phase_1 = MinMaxPhase_1(input, anns, verbose=verbose)
    minmax_anns_1 = extraction_phase_1.run_phase()
    if verbose: 
        msg = f"\nReturned to run_extraction_phases(). minmax_anns: {minmax_anns_1}"
        print(msg)

    # Remove from the input annotations any which form part of the new
    # MinMax annotations. This prevents the next set of MinMax rules from
    # matching on those annotations.
    enclosed = []
    for mm_ann in minmax_anns_1:
        enclosed.extend(Annotation.get_enclosed(mm_ann, anns))
    anns_2 = [x for x in anns if x not in enclosed]
    
    # After this, anns_2 will contain the newly-found MinMax annotations
    # plus any unconsumed Number and Unit_of_Measure annotations.
    anns_2.extend(minmax_anns_1)
    if verbose: print(f"  Filtered anns_2 annotations: {anns}\n")

    extraction_phase_2 = MinMaxPhase_2(input, anns_2, verbose=verbose)
    minmax_anns_2 = extraction_phase_2.run_phase()
    result = minmax_anns_1 + minmax_anns_2

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
    varied almost as much--anywhere within the range of 60 to 90 points. 
    """
    input = inspect.cleandoc(text)

    entities = []

    # Write rules for two types of entities--Number and Unit_of_Measurement.
    number_rs = RegexString.regex_to_RegexString('(\d+)')
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

    uom_rs = RegexString(['pounds', 'drinks', 'points'])
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
