import unittest
from typing import List, Tuple, Dict

# from test.gazetteer import Gazetteer
from text_to_relations.relation_extraction.RegexString import RegexString
from text_to_relations.relation_extraction.Annotation import Annotation
from text_to_relations.relation_extraction.ExtractionPhaseABC import ExtractionPhaseABC
from text_to_relations.relation_extraction.TokenAnn import TokenAnn
from text_to_relations.relation_extraction.extraction_loop import ExtractionLoop, run_loop, get_sorted_annotations_for_matching

def determine_new_annotation_properties(match_triples: List[Tuple], doc:str) -> Dict[str, object]:
    # Function created specifically for this test.
    # Simply extracts the first and last character of the input text.
    properties = {'first_character': doc[0], 'last_character': doc[-1]}
    return properties


class TestExtractionLoop(unittest.TestCase):

    def test_invalid_loop_list(self):
        # Verify an exception is thrown if any but the last loop has 
        # a defined determine_new_annotation_properties.
        one_rs = RegexString(['1'])
        regex_strs = {"One": one_rs}

        # First test to test.
        text = "1 a 2 b 3"

        anns = get_sorted_annotations_for_matching(text=text, regex_strs=regex_strs, given_anns=[])

        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        regex_1 = TokenAnn.build_annotation_distance_regex("One", (0, 2), None, "Two")
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two', 
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=False)

        regex_2 = TokenAnn.build_annotation_distance_regex("Two", (0, 2), None, "Three")
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three', 
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=False)

        loop_list = [loop_1, loop_2]
        loops_in_process = []

        with self.assertRaises(ValueError):
            run_loop(annotation_view_text=annotation_view_str,
                doc=text, 
                curr_loop=loop_1, 
                loop_idx=0, 
                loops_in_process=loops_in_process,
                loop_list=loop_list, 
                match_triples_list=[],
                new_annotations=[],
                verbose=False)


        # Verify that an exception is thrown if the last loop does not
        # have a determine_new_annotation_properties defined.
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two', 
                                # determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=False)

        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three', 
                                # determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=False)
        loop_list = [loop_1, loop_2]
        with self.assertRaises(ValueError):
            run_loop(annotation_view_text=annotation_view_str,
                doc=text, 
                curr_loop=loop_1, 
                loop_idx=0, 
                loops_in_process=loops_in_process,
                loop_list=loop_list, 
                match_triples_list=[],
                new_annotations=[],
                verbose=False)            



    def test_failure(self):
        # Verify that the process fails gracefully if there are no matches.
        one_rs = RegexString(['1'])
        two_rs = RegexString(['2'])
        three_rs = RegexString(['3'])
        regex_strs = {"One": one_rs, "Two": two_rs, "Three": three_rs}

        # First text to test.
        # 1 is within two tokens of 2, but 2 is not within two tokens of 3.
        text = "1 a 2 b c d e f g h i 3"

        anns = get_sorted_annotations_for_matching(text=text, regex_strs=regex_strs, given_anns=[])

        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        regex_1 = TokenAnn.build_annotation_distance_regex("One", (0, 2), None, "Two")
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two', verbose=False)

        regex_2 = TokenAnn.build_annotation_distance_regex("Two", (0, 2), None, "Three")
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three', 
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=False)

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
                        verbose=False)
        
        self.assertEqual([], result)



    def test_two_loops(self):
        one_rs = RegexString(['1'])
        two_rs = RegexString(['2'])
        three_rs = RegexString(['3'])
        regex_strs = {"One": one_rs, "Two": two_rs, "Three": three_rs}

        # First test to test.
        text = "1 a 2 b 3"

        anns = get_sorted_annotations_for_matching(text=text, regex_strs=regex_strs, given_anns=[])

        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        regex_1 = TokenAnn.build_annotation_distance_regex("One", (0, 2), None, "Two")
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two', verbose=False)

        regex_2 = TokenAnn.build_annotation_distance_regex("Two", (0, 2), None, "Three")
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three', 
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=False)

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
                        verbose=False)

        properties = {'first_character': '1', 'last_character':'3'}
        ann = Annotation('MinMax', '1 a 2 b 3', 0, 9, properties)
        self.assertEqual([ann], result)

        # Second test to test.
        text = "z 1 a 1 b 2 c 2 d 3 y 1 2 3 x"

        anns = get_sorted_annotations_for_matching(text=text, regex_strs=regex_strs, given_anns=[])

        annotation_view_str = ExtractionPhaseABC.build_merged_representation(text, anns)

        regex_1 = TokenAnn.build_annotation_distance_regex("One", (0, 2), None, "Two")
        loop_1 = ExtractionLoop(regex_str=regex_1, last_ann_str='Two', verbose=False)

        regex_2 = TokenAnn.build_annotation_distance_regex("Two", (0, 2), None, "Three")
        loop_2 = ExtractionLoop(regex_str=regex_2, last_ann_str='Three', 
                                determine_new_annotation_properties=determine_new_annotation_properties,
                                verbose=False)

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
                        verbose=False)

        properties = {'first_character': 'z', 'last_character':'x'}
        ann1 = Annotation('MinMax', '1 b 2 c 2 d 3', 6, 19, properties)
        ann2 = Annotation('MinMax', '1 2 3', 22, 27, properties)
        self.assertEqual([ann1, ann2], result)

