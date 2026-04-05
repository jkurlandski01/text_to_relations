"""
Abstract base class for relation extraction--i.e., building
relations between previously-identified entities.
"""
import re
from abc import ABCMeta
from typing import Dict, List, Optional

from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.RegexString import RegexString


class ChainLink:
    """
    One step in a proximity chain, constraining how close two annotation
    types must be to be considered a match.

    Attributes:
        start_type: annotation type that begins this step (e.g. 'Number').
        start_property: key under which the start annotation's value will be
            stored in the resulting relation's properties (e.g. 'min_number').
        min_distance: minimum number of intervening tokens allowed (inclusive).
        max_distance: maximum number of intervening tokens allowed (inclusive).
        end_type: annotation type that ends this step (e.g. 'Magnitude').
        end_property: key under which the end annotation's value will be
            stored in the resulting relation's properties (e.g. 'max_number').
            For all links except the last, this should equal the start_property
            of the following link.

    Raises ValueError if min_distance > max_distance.
    """

    def __init__(self, start_type: str, start_property: str, min_distance: int,
                 max_distance: int, end_type: str, end_property: str):
        if min_distance > max_distance:
            raise ValueError(
                f"ChainLink min_distance ({min_distance}) must be <= max_distance ({max_distance})"
            )
        self.start_type = start_type
        self.start_property = start_property
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.end_type = end_type
        self.end_property = end_property


class ExtractionPhaseABC(metaclass=ABCMeta):
    """
    Abstract base class of phases.
    Valid subclasses must:
    1. Set self.relation_name, self.regex_patterns, and self.chain to non-None values.
    2. Ensure that for every link after the first, the link's start_type and
       start_property match the previous link's end_type and end_property.
    3. Ensure that all property names across the chain are unique (i.e. the
       resulting relation will have one attribute per chain node, with no
       two nodes sharing a property name).
    """
    regexWhitespace = re.compile(r'\s+', re.IGNORECASE | re.DOTALL | re.MULTILINE)

    def __init_subclass__(cls, **kwargs):
        """
        Automatically wrap every subclass's __init__ so that _validate() is
        called immediately after the subclass finishes constructing itself.
        This ensures that any invalid subclass fails at
        construction time with a clear error rather than later.
        """
        super().__init_subclass__(**kwargs)
        original_init = cls.__init__
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self._validate()
        cls.__init__ = new_init

    def __init__(self, verbose: bool = False):
        """
        Args:
            verbose (bool): if True, print internal state at each step.
        """
        self.verbose = verbose

        # Subclasses must assign all three of the following in their __init__.
        self.relation_name: Optional[str] = None
        self.regex_patterns: Optional[Dict[str, RegexString]] = None
        self.chain: Optional[List[ChainLink]] = None

    def _validate(self):
        """
        Verify that the subclass satisfies all three requirements documented
        on the class. Raises ValueError with a clear message for the first
        violation found.
        """
        # Requirement 1: all three instance variables must be assigned.
        missing = [name for name, val in [
            ('relation_name', self.relation_name),
            ('regex_patterns', self.regex_patterns),
            ('chain', self.chain),
        ] if val is None]
        if missing:
            raise ValueError(
                f"{type(self).__name__}.__init__ must assign: {', '.join(missing)}"
            )

        # Requirement 2: consecutive links must share their boundary annotation.
        for i in range(1, len(self.chain)):
            prev, curr = self.chain[i - 1], self.chain[i]
            if curr.start_type != prev.end_type or curr.start_property != prev.end_property:
                raise ValueError(
                    f"{type(self).__name__}: chain[{i}] start "
                    f"({curr.start_type!r}, {curr.start_property!r}) does not match "
                    f"chain[{i - 1}] end ({prev.end_type!r}, {prev.end_property!r})"
                )

        # Requirement 3: all property names must be unique across the chain.
        all_props = ([self.chain[0].start_property] if self.chain else []) + \
                    [link.end_property for link in self.chain]
        seen = set()
        for prop in all_props:
            if prop in seen:
                raise ValueError(
                    f"{type(self).__name__}: property name {prop!r} appears more than once "
                    f"in the chain"
                )
            seen.add(prop)

    def find_match(self, text: str,
                   entity_annotations: Optional[List[Annotation]] = None) -> List[Annotation]:
        """
        Process text input and return any extracted relation annotations.

        Uses self.relation_name, self.regex_patterns, and self.chain, which
        subclasses set in their __init__.

        Args:
            text: a single document entry to process.
            entity_annotations: annotations produced by external tools before
                relation extraction begins (e.g. Number, Unit_of_Measure),
                to be incorporated alongside those produced by regex_patterns
                during the relation extraction process.

        Returns:
            List[Annotation]: newly created relation annotations.
        """
        assert self.regex_patterns is not None
        assert self.chain is not None
        return self.run_chained_loops(text, self.regex_patterns, self.chain,
                                      entity_annotations=entity_annotations)

    def run_chained_loops(self, text: str,
                          regex_patterns: Dict[str, RegexString],
                          chain: List[ChainLink],
                          entity_annotations: Optional[List[Annotation]] = None) -> List[Annotation]:
        """
        Build annotations from regex_patterns, then run a chain of proximity
        loops and return the resulting relation annotations.

        Args:
            text: the document entry to process.
            regex_patterns: dict mapping annotation type name to RegexString.
            chain: list of ChainLinks defining the proximity constraints between
                consecutive annotation types.
            entity_annotations: annotations produced by external tools before
                relation extraction begins, to be incorporated alongside those
                produced by regex_patterns.

        Returns:
            List[Annotation]: newly created relation annotations.
        """
        # Imported here rather than at the top of the file to avoid a circular import:
        # extraction_loop imports ExtractionPhaseABC, so a top-level import would create a cycle.
        from text_to_relations.relation_extraction.extraction_loop import (
            ExtractionLoop, run_loop, get_sorted_annotations_for_matching)

        given_anns = list(entity_annotations) if entity_annotations else []
        anns = get_sorted_annotations_for_matching(
            text=text, regex_strs=regex_patterns, given_anns=given_anns)
        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        def _determine_properties(match_triples):
            # For each link i, the matched segment (triple[0]) contains the
            # start annotation followed by zero or more Token annotations
            # followed by the end annotation. Map the first non-Token annotation
            # to chain[i].start_property and the last to chain[i].end_property.
            # Consecutive links share an annotation (end of link i == start of
            # link i+1), so intermediate end_property/start_property pairs write
            # the same value under the same key, which is harmless.
            properties = {}
            for i, triple in enumerate(match_triples):
                non_token_anns = [a for a in
                                  ExtractionPhaseABC.merged_representation_to_annotations(triple[0])
                                  if a.type != 'Token']
                if non_token_anns:
                    properties[chain[i].start_property] = non_token_anns[0].normalizedContents
                    properties[chain[i].end_property] = non_token_anns[-1].normalizedContents
            return properties

        loops = []
        for i, link in enumerate(chain):
            is_last = i == len(chain) - 1
            regex = TokenAnn.build_annotation_distance_regex(
                link.start_type, (link.min_distance, link.max_distance), None, link.end_type)
            loop = ExtractionLoop(
                regex_str=regex,
                last_ann_str=link.end_type,
                determine_new_annotation_properties=_determine_properties if is_last else None,
                verbose=self.verbose
            )
            loops.append(loop)

        assert self.relation_name is not None
        result = run_loop(
            annotation_view_str=annotation_view_str,
            doc=text,
            relation_name=self.relation_name,
            curr_loop=loops[0],
            loop_idx=0,
            loops_in_process=[],
            loop_list=loops,
            match_triples_list=[],
            new_annotations=[],
            verbose=self.verbose
        )
        # run_loop() is recursive and its return type is Union[List[Annotation], Annotation, None]
        # to accommodate intermediate recursion levels. At the top-level call (loop_idx=0) it
        # always returns a list, so this assert narrows the type for mypy.
        assert isinstance(result, list)
        return result

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
        unconsumed_annotations = anns

        result = ""
        last_pos = 0

        # Strategy: Tokenize the doc and iterate through all the tokens. If a token
        # is covered by an annotation, write that annotation to the output and advance
        # last_pos to the end of the annotation; otherwise, write the token to output
        # and continue.
        token_objs = TokenAnn.get_token_objects(contents, 0)

        for token_obj in token_objs:

            if last_pos > token_obj.start_offset:
                continue

            temp_anns = unconsumed_annotations
            found_ann = False
            for ann in temp_anns:
                if ann.start_offset <= token_obj.start_offset:
                    # Write the annotation and remove it from the unconsumed_annotations.
                    unconsumed_annotations = unconsumed_annotations[1:]
                    result += str(ann)
                    if verbose:
                        print(str(ann))
                    last_pos = ann.end_offset
                    found_ann = True
                else:
                    break

            if found_ann:
                continue

            # This token occurs in the document before the next unconsumed annotation. Write it to
            # output.
            result += str(token_obj)

            last_pos = token_obj.end_offset

        # Verify that all the annotations have been consumed.
        if len(unconsumed_annotations) > 0:
            msg = "Final annotations in the anns parameter not inserted into the merged document."
            msg += f"  unconsumed annotations: {unconsumed_annotations}"
            raise ValueError(msg)

        return result


    @staticmethod
    def merged_representation_to_annotations(rep: str,
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
            if verbose:
                print(f"in_str: {in_str}")
            complete_strs.append('<' + in_str)
        if verbose:
            print(f"complete_strs: {complete_strs}")
        anns = [Annotation.str_to_annotation(c_str) for c_str in complete_strs]
        return anns


class SimpleExtractionPhase(ExtractionPhaseABC):
    """
    A ready-to-use concrete implementation of ExtractionPhaseABC for cases
    where no custom validation, matching, or loop behaviour is needed.

    Instead of subclassing ExtractionPhaseABC and assigning relation_name,
    regex_patterns, and chain in __init__, callers can instantiate this class
    directly:

        phase = SimpleExtractionPhase(
            relation_name='MyRelation',
            regex_patterns={'EntityA': rs_a, 'EntityB': rs_b},
            chain=[ChainLink(...)],
        )
        results = phase.find_match(text)

    For use cases that require overriding find_match(), run_chained_loops(),
    or _validate(), subclass ExtractionPhaseABC directly instead.
    """

    def __init__(self, relation_name: str, regex_patterns: Dict, chain: List[ChainLink],
                 verbose: bool = False):
        """
        Args:
            relation_name (str): type name assigned to each extracted relation
                Annotation (e.g. 'MinMax', 'StampDescription').
            regex_patterns (Dict[str, RegexString]): dict mapping annotation
                type name to RegexString, defining the entities to find.
            chain (List[ChainLink]): proximity constraints between consecutive
                annotation types.
            verbose (bool): if True, print internal state at each step.
        """
        super().__init__(verbose=verbose)
        self.relation_name = relation_name
        self.regex_patterns = regex_patterns
        self.chain = chain
