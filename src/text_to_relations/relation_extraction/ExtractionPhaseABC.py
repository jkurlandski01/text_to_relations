"""
Abstract base class for relation extraction--i.e., building
relations between previously-identified entities.
"""
import re
from abc import ABCMeta, abstractmethod
from typing import List

from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.Annotation import Annotation

class ExtractionPhaseABC(metaclass=ABCMeta):
    """
    Abstract base class of phases.
    """
    regexWhitespace = re.compile(r'\s+', re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @abstractmethod
    def run_phase(self):
        """
        Runs this extraction phase object.
        """
        pass

    def __init__(self, doc_contents: str):
        """

        Args:
            doc_contents (str): the normalized contents of the 
                document being processed
        """
        if doc_contents is None or doc_contents == '':
            msg = "doc_contents is empty or None. "
            msg += "An extraction phase object requires a document to process."
            raise TypeError(msg)
        self.doc_contents = doc_contents

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
