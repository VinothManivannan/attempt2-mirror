"""
This program tests different combinations of json files to verify the correct functioning of tahini_add_json_info
Test 1 tests that fields can be added both on enums and regmap regardless of nesting
Test 2 tests that an "empty" additional json file will result in the output being the same as the input
Test 3 tests that every single field can be added and that if some fields are not included in the additional json
       file but are in the input_json these will remain in the output
"""
# pylint: disable=wrong-import-position
from os import path
import unittest
from cmlpytools.tahini.tahini_add_json_info import TahiniAddJsonInfo
from cmlpytools.tahini.input_json_schema import InputJson

PATH_TO_DATA = "./tests/tahini/data"

class TestCombiningJson(unittest.TestCase):
    """Test class for addjsoninfo tahini method
    """
    def test(self):
        """Test if input json file combined correctly with extra json info for different cases"""
        for i in range (1, 4):
            input_json_file = path.join(PATH_TO_DATA, "test_input_json_example.json")
            additional_json_file = path.join(PATH_TO_DATA, f"test_extra_regmap_info{i}.json")
            expected_combined_json_file = path.join(PATH_TO_DATA, f"test_expected_combined_json{i}.json")

            combined_json_output = TahiniAddJsonInfo.combine_json_files(input_json_file, additional_json_file)

            expected_combined_json_obj = InputJson.load_json(expected_combined_json_file)
            self.assertEqual(expected_combined_json_obj, combined_json_output,
                             f"Addjsoninfo test {i} failed, generated json file not equal to expected")
