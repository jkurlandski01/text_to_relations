import re
from typing import Dict, Self, Collection, List

from text_to_relations.relation_extraction import StringUtils

class Annotation(object):
    """"""
    regexQuote = r"['\"].*?['\"]"

    def __init__(self, type: str, contents: str, 
                 start_offset: int, end_offset: int, 
                 properties: Dict[str, object]=None):
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
            msg = "Start offset cannot be greater than end offset. Start: " + str(start_offset) + "; End: " + str(end_offset)
            raise ValueError(msg)

        if start_offset < 0 or end_offset < 0:
            msg = "Start and end offset cannot be less than 0. Start: " + str(start_offset) + "; End: " + str(end_offset)
            raise ValueError(msg)

        self.type = type
        self.start_offset = start_offset
        self.end_offset = end_offset

        cleanedContents = contents.replace('\n', ' ')
        self.normalizedContents = StringUtils.removeMultipleSpaces(cleanedContents).strip()

        if properties is None:
            properties = {}
        self.properties = properties
    

    def to_dict(self) -> Dict[str, str]:
        result = {'type': self.type, 
                  'start': self.start_offset, 
                  'end': self.end_offset, 
                  'text': self.normalizedContents}
        return result


    def __repr__(self):
        if self.properties == {}:
            result = "<'%s'(normalizedContents='%s', start='%s', end='%s')>" \
                     % (self.type, self.normalizedContents, self.start_offset, self.end_offset)
        else:
            features = ''
            for featureName in self.properties:
                features += featureName + "='" + self.properties[featureName] + "', "
            # Remove last comma-space.
            features = features[0:-2]
                
            result = "<'%s'(normalizedContents='%s', start='%s', end='%s', %s)>" \
                     % (self.type, self.normalizedContents, self.start_offset, self.end_offset, features)

        return result

    def __eq__(self, other):
        if not isinstance(other, Annotation):
            return False
        elif self is other:
            return True
        else:
            if self.properties != other.properties:
                return False
            
            if self.type == other.type and \
                        self.start_offset == other.start_offset and \
                        self.end_offset == other.end_offset and \
                        self.normalizedContents == other.normalizedContents:
                    return True

        return False
    
    def __hash__(self):
        return hash(self.__repr__())

    @staticmethod
    def sort(items: Collection[Self]) -> Collection[Self]:
        """
        Sort the in-coming collection of Annotations by starting and
        ending offset.
        Args:
            items (Collection[Self]): 

        Returns:
            Collection[Self]: 
        """
        anns = sorted(items, key=lambda p: (p.start_offset, p.end_offset), reverse=False)
        return anns

    @staticmethod
    def str_to_Annotation(annStr: str) -> Self:
        """
        Convert the output of __repr__ to an Annotation object.
        Assuming that the strings are in one of these two forms:
        - "<'AnnotationName'(normalizedContents='...', start='m', end='n')>"
        - '<"AnnotationName"(normalizedContents="...", start="m", end="n")>'

        Args:
            annStr (str): 

        Returns:
            Self: 
        """
        # TODO: Currently this method will not add any unexpected strings (i.e. features) into the properties.
        matches = re.findall(Annotation.regexQuote, annStr)
        # We use '[1:-1]' to chop off the quote at either end.
        aType = matches[0][1:-1]
        contents = matches[1][1:-1]
        start = int(matches[2][1:-1])
        end = int(matches[3][1:-1])
        ann = Annotation(aType, contents, start, end)
        return ann
    
    
    @staticmethod
    def encloses(ann1: Self, ann2: Self) -> bool:
        """
        Does ann1 "enclose" ann2? I.e., is ann2 entirely contained within the bounds of ann1?
        Determination is made with starting and ending offsets only--the annotations'
        normalizedContents properties are ignored.
        Args:
            ann1 (Self): 
            ann2 (Self): 

        Returns:
            bool: 
        """
        if ann1.start_offset <= ann2.start_offset and ann1.end_offset >= ann2.end_offset:
            return True
        return False
    
    
    @staticmethod
    def get_enclosed(ann: Self, ann_list: List[Self]) -> List[Self]:
        """
        Return the subset of the annotations in the given list which are enclosed
        by the given annotation.
        Args:
            ann (Self): 
            ann_list (List[Self]): 

        Returns:
            List[Self]: 
        """
        result = []
        for annElement in ann_list:
            if Annotation.encloses(ann, annElement):
                result.append(annElement)
        
        return result
    

if __name__ == '__main__':
    pass
