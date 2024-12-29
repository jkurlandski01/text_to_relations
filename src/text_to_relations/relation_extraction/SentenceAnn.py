from typing import List, Self

from text_to_relations.relation_extraction.Annotation import Annotation
import spacy

spacy_model = spacy.load('en_core_web_lg', disable=["tagger", "ner", "lemmatizer"])
spacy_model.add_pipe('sentencizer')

class SentenceAnn(Annotation):
    """
    An Annotation object covering an entire sentence in a document
    """
    
    def __init__(self, contents: str, start_offset: int, end_offset: int):
        """
        Args:
            contents (str): sentence text
            start_offset (int): start offset of the sentence in the doc
            end_offset (int): end offset in the doc
        """
        super().__init__('Sentence', contents, start_offset, end_offset)
    
    
    @staticmethod
    def text_to_SentenceAnns(input: str) -> List[Self]:
        """
        Split the given input text into sentences, and create a SentenceAnn
        on each one.
        Args:
            input (str): the text to split

        Returns:
            List[Self]: a list of SentenceAnn annotations created on the 
                given text
        """
        sentenceSpans = spacy_model(input).sents
        sentenceStrs = []
        for sentence in sentenceSpans:
            sentenceStrs.append(sentence.text.strip())
        
        result = []
        startSearchIdx = 0
        for sentence in sentenceStrs:
            startIdx = input.find(sentence, startSearchIdx)
            endIdx = startIdx + len(sentence)
            sentAnn = SentenceAnn(sentence.strip(), startIdx, endIdx)
            result.append(sentAnn)
            startSearchIdx = endIdx

        return result
    

if __name__ == '__main__':
    pass
