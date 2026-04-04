from typing import List


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
    def text_to_sentence_anns(text: str) -> List['SentenceAnn']:
        """
        Split the given input text into sentences, and create a SentenceAnn
        on each one.
        Args:
            text (str): the text to split

        Returns:
            List[SentenceAnn]: a list of SentenceAnn annotations created on the
                given text
        """
        sentence_spans = spacy_model(text).sents
        sentence_strs = []
        for sentence in sentence_spans:
            sentence_strs.append(sentence.text.strip())

        result = []
        start_search_idx = 0
        for sent_str in sentence_strs:
            start_idx = text.find(sent_str, start_search_idx)
            end_idx = start_idx + len(sent_str)
            sent_ann = SentenceAnn(sent_str.strip(), start_idx, end_idx)
            result.append(sent_ann)
            start_search_idx = end_idx

        return result


if __name__ == '__main__':
    pass
