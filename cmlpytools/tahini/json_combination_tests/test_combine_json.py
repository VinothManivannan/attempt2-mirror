"""
This program tests different combinations of json files to verify the correct functioning of tahini_add_json_info
Test 1 tests that fields can be added both on enums and regmap regardless of nesting
Test 2 tests that an "empty" additional json file will result in the output being the same as the input
Test 3 tests that every single field can be added and that if some fields are not included in the additional json
       file but are in the input_json these will remain in the output
"""
# pylint: disable=wrong-import-position
import os
import sys
sys.path.append('../')
from tahini_add_json_info import CombineJsonFiles
from input_json_schema import InputJson

def main():
    """Entry point for tests"""
    passed_tests = True
    for i in range (1,2):
        input_json_file = os.path.join(os.getcwd(), "input_json_example.json")
        additional_json_file = os.path.join(os.getcwd(), f"extra_regmap_info{i}.json")
        combined_json_file = os.path.join(os.getcwd(), "combined_json_output.json")
        expected_combined_json_file = os.path.join(os.getcwd(), f"expected_combined_json{i}.json")

        CombineJsonFiles.combine_json_files(input_json_file, additional_json_file, combined_json_file)

        combined_json_obj = InputJson.load_json(combined_json_file)
        expected_combined_json_obj = InputJson.load_json(expected_combined_json_file)
        if combined_json_obj != expected_combined_json_obj:
            passed_tests = False
            print(f"Test {i} failed")

    if passed_tests is True:
        print("Tests passed")

if __name__ == "__main__":
    main()
