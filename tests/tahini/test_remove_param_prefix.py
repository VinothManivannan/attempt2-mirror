"""
This program tests if Param prefix is eliminated regardless of whether register is in struct
and ensures param is not eliminated and nothing else changes
"""
# pylint: disable=wrong-import-position
from os import path
import unittest
from cmlpytools.tahini.tahini_remove_param_prefix import TahiniRemoveParamPrefix
from cmlpytools.tahini.input_json_schema import InputJson

PATH_TO_DATA = "./tests/tahini/data"

class TestRemoveParamPrefix(unittest.TestCase):
    """Test class for addjsoninfo tahini method
    """
    def test(self):
        """Test if Param prefix removed as expected"""
        input_json_file = path.join(PATH_TO_DATA, "test_remove_param_prefix.json")
        output_json_file = path.join(PATH_TO_DATA, "test_remove_param_prefix_result.json")

        json_result = TahiniRemoveParamPrefix.remove_param_prefix(input_json_file)

        print("something")

        expected_json_result = InputJson.load_json(output_json_file)
        self.assertEqual(expected_json_result, json_result,
                            "removeparamprefix test failed, generated json not equal to expected")
