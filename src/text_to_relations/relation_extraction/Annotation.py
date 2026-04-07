import re
from typing import Dict, Collection, List, Optional

from text_to_relations.relation_extraction import StringUtils

class Annotation:
    """Represents a typed, offset-based annotation (entity mention) in a document."""
    regexQuote = r"['\"].*?['\"]"

    def __init__(self, ann_type: str, contents: str,
                 start_offset: int, end_offset: int,
                 properties: Optional[Dict[str, object]] = None):
        """

        Args:
            type (str): annotation (entity) type, e.g. Person, Currency, River
            contents (str): the mention in the doc, e.g. 'John Smith', 'Euros', 'Amazon'
            start_offset (int):
            end_offset (int):
            properties (Dict[str, object], optional): A free-form dict for
                adding attributes. Defaults to None.
        """
        if start_offset > end_offset:
            raise ValueError(
                f"Start offset cannot be greater than end offset. Start: {start_offset}; End: {end_offset}")

        if start_offset < 0 or end_offset < 0:
            raise ValueError(
                f"Start and end offset cannot be less than 0. Start: {start_offset}; End: {end_offset}")

        self.type = ann_type
        self.start_offset = start_offset
        self.end_offset = end_offset

        cleaned_contents = contents.replace('\n', ' ')
        # Contents with newlines replaced by spaces, multiple spaces collapsed,
        # and whitespace stripped.
        self.text = StringUtils.remove_multiple_spaces(cleaned_contents).strip()

        if properties is None:
            properties = {}
        self.properties = properties


    def to_dict(self) -> Dict[str, object]:
        """Return a dict representation with type, start, end, and text keys."""
        result = {'type': self.type,
                  'start': self.start_offset,
                  'end': self.end_offset,
                  'text': self.text}
        return result


    def __repr__(self):
        if self.properties == {}:
            result = (f"<'{self.type}'(text='{self.text}', "
                      f"start='{self.start_offset}', end='{self.end_offset}')>")
        else:
            features = ''
            for feature_name in self.properties:
                features += feature_name + "='" + self.properties[feature_name] + "', "
            # Remove last comma-space.
            features = features[0:-2]

            result = (f"<'{self.type}'(text='{self.text}', "
                      f"start='{self.start_offset}', end='{self.end_offset}', {features})>")

        return result

    def __eq__(self, other):
        if not isinstance(other, Annotation):
            return False
        if self is other:
            return True
        if self.properties != other.properties:
            return False
        if self.type == other.type and \
                self.start_offset == other.start_offset and \
                self.end_offset == other.end_offset and \
                self.text == other.text:
            return True
        return False

    def __hash__(self):
        return hash(self.__repr__())

    @staticmethod
    def sort(items: Collection['Annotation']) -> List['Annotation']:
        """
        Sort the in-coming collection of Annotations by starting and
        ending offset.
        Args:
            items (Collection['Annotation']):

        Returns:
            List['Annotation']:
        """
        anns = sorted(items, key=lambda p: (p.start_offset, p.end_offset), reverse=False)
        return anns

    @staticmethod
    def str_to_annotation(ann_str: str) -> 'Annotation':
        """
        Convert the output of __repr__ to an Annotation object.
        Assuming that the strings are in one of these two forms:
        - "<'AnnotationName'(text='...', start='m', end='n')>"
        - '<"AnnotationName"(text="...", start="m", end="n")>'

        Args:
            ann_str (str):

        Returns:
            'Annotation':
        """
        matches = re.findall(Annotation.regexQuote, ann_str)
        # We use '[1:-1]' to chop off the quote at either end.
        a_type = matches[0][1:-1]
        contents = matches[1][1:-1]
        start = int(matches[2][1:-1])
        end = int(matches[3][1:-1])
        ann = Annotation(a_type, contents, start, end)
        return ann


    @staticmethod
    def encloses(ann1: 'Annotation', ann2: 'Annotation') -> bool:
        """
        Does ann1 "enclose" ann2? I.e., is ann2 entirely contained within the bounds of ann1?
        Determination is made with starting and ending offsets only--the annotations'
        text properties are ignored.
        Args:
            ann1 ('Annotation'):
            ann2 ('Annotation'):

        Returns:
            bool:
        """
        if ann1.start_offset <= ann2.start_offset and ann1.end_offset >= ann2.end_offset:
            return True
        return False


    @staticmethod
    def get_enclosed(ann: 'Annotation', ann_list: List['Annotation']) -> List['Annotation']:
        """
        Return the subset of the annotations in the given list which are enclosed
        by the given annotation.
        Args:
            ann ('Annotation'):
            ann_list (List['Annotation']):

        Returns:
            List['Annotation']:
        """
        result = []
        for ann_element in ann_list:
            if Annotation.encloses(ann, ann_element):
                result.append(ann_element)

        return result


if __name__ == '__main__':
    pass
