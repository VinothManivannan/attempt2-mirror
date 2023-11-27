"""
This program tests different combinations of json files to verify the correct functioning of tahini_add_json_info
Test 1 tests that fields can be added both on enums and regmap regardless of nesting
Test 2 tests that an "empty" additional json file will result in the output being the same as the input
Test 3 tests that every single field can be added and that if some fields are not included in the additional json
       file but are in the input_json these will remain in the output
"""
# pylint: disable=wrong-import-position
from os import path
import sys
import unittest
sys.path.append('../')
from cmlpytools.tahini.tahini_add_json_info import TahiniAddJsonInfo
from cmlpytools.tahini.input_json_schema import InputJson

PATH_TO_DATA = "./tests/tahini/data"

class TestCombiningJson(unittest.TestCase):
    """Test class for addjsoninfo tahini method
    """
    def test(self):
        """Entry point for tests"""
        for i in range (1, 4):
            input_json_file = path.join(PATH_TO_DATA, "data/test_input_json_example.json")
            additional_json_file = path.join(PATH_TO_DATA, f"test_extra_regmap_info{i}.json")
            combined_json_file = path.join(PATH_TO_DATA, "test_combined_json_output.json")
            expected_combined_json_file = path.join(PATH_TO_DATA, f"test_expected_combined_json{i}.json")

            combined_json_output = TahiniAddJsonInfo.combine_json_files(input_json_file, additional_json_file)

            # pylint: disable=consider-using-with
            stdout = sys.stdout
            if combined_json_file is not None:
                sys.stdout = open(combined_json_file, "w", encoding="UTF-8")

            sys.stdout.write(combined_json_output.to_json(indent=4))

            if combined_json_file is not None:
                sys.stdout.close()
            sys.stdout = stdout
            # pylint: enable=consider-using-with

            combined_json_obj = InputJson.load_json(combined_json_file)
            expected_combined_json_obj = InputJson.load_json(expected_combined_json_file)
            self.assertEqual(expected_combined_json_obj, combined_json_obj,
                             f"Addjsoninfo test {i} failed, generated json file not equal to expected")
