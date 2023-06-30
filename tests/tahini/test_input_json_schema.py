"""
Import unittest module to test inputjson
"""
from os import path
import unittest
from cmlpytools.tahini.input_json_schema import InputJson
from cmlpytools.tahini.input_json_schema import InvalidInputEnumError

PATH_TO_DATA = "./tests/tahini/data"


class TestFilePath(unittest.TestCase):
    """Class that check if input json files used are valid
    """
    path_inputfile = path.join(PATH_TO_DATA, "test_fullregmap_inputjsonexample.json")
    path_basetype = path.join(PATH_TO_DATA, "test_inputjson_base_type.json")
    path_array_basetype = path.join(PATH_TO_DATA, "test_inputjson_array_base_type.json")
    path_structtype = path.join(PATH_TO_DATA, "test_inputjson_struct_type.json")
    path_uniontype_struct = path.join(PATH_TO_DATA, "test_inputjson_union_type_struct.json")
    path_uniontype_bitfields = path.join(PATH_TO_DATA, "test_inputjson_union_type_bitfields.json")
    path_invalid_enum_unique_value = path.join(PATH_TO_DATA, "test_inputjson_invalid_enum_unique_value.json")
    path_invalid_unique_name = path.join(PATH_TO_DATA, "test_inputjson_invalid_enum_unique_name.json")

    @staticmethod
    def read_json(json_path):
        """Read json files
        """
        with open(json_path, 'r', encoding='utf-8') as loadfile:
            data_open = loadfile.read()
        return data_open

    def test_path(self):
        """Check if the path is a valid string
        """
        self.read_json(self.path_inputfile)
        self.read_json(self.path_basetype)
        self.read_json(self.path_array_basetype)
        self.read_json(self.path_structtype)
        self.read_json(self.path_uniontype_struct)
        self.read_json(self.path_uniontype_bitfields)
        self.read_json(self.path_invalid_enum_unique_value)
        self.read_json(self.path_invalid_unique_name)


class TestInputJson(unittest.TestCase):
    """ Test class for the InputJson class
    """

    def test_valid_base_type(self):
        """Test if the base type properties of regmap are defined and converted correctly
        """
        data1 = InputJson.load_json(TestFilePath.path_basetype)
        data1_children = data1.regmap[0]
        self.assertEqual('ray', data1_children.name, "Required name is not matched")
        self.assertEqual('unsigned short', data1_children.type, "Required type is not matched")
        self.assertEqual(2048, data1_children.address, "Required address is not matched")
        self.assertEqual('private', data1_children.access.value, "Required visibility is not matched")
        self.assertEqual(True, data1_children.hif_access, "Required indirect access is not matched")

    def test_valid_array_base_type(self):
        """Test if the repeat for properties of regmap are defined and converted correctly
        """
        data1 = InputJson.load_json(TestFilePath.path_array_basetype)
        data1_children = data1.regmap[0]
        self.assertEqual(3, data1_children.array_count, "Array count is not matched")
        self.assertEqual(False, data1_children.hif_access, "Required indirect access is not matched")

    def test_valid_base_type_enum(self):
        """Test if the base type properties of enum are defined and converted correctly
        """
        data1 = InputJson.load_json(TestFilePath.path_basetype)
        data1_children = data1.enums[0]
        self.assertEqual('RAY_OFF', data1_children.enumerators[0].name, "Enumerated name is not matched")

    def test_struct_type(self):
        """Test if the struct type properties are defined and converted correctly
        """
        data1 = InputJson.load_json(TestFilePath.path_structtype)
        data1_children = data1.regmap[0].members[0]
        self.assertIn("Distance to get it", data1_children.brief, "Unable to read brief in struct")

    def test_union_type_struct(self):
        """Test if the union type properties are defined and converted correctly
        """
        data1 = InputJson.load_json(TestFilePath.path_uniontype_struct)
        data1_children = data1.regmap[0].members[1].members[0]
        self.assertEqual('red', data1_children.name, "Unable to read name in union struct")

    def test_union_type_bitfields(self):
        """Test if the bitfields type properties are defined and converted correctly
        """
        data1 = InputJson.load_json(TestFilePath.path_uniontype_bitfields)
        data1_children = data1.regmap[0].members[1].members[0]
        self.assertEqual('A', data1_children.name, "Unable to read bitfields name")

    def test_invalid_input_enum_unique(self):
        """Test if invalid unique checks in enum field can be raised correctly
        """
        with self.assertRaises(InvalidInputEnumError) as context:
            InputJson.load_json(TestFilePath.path_invalid_unique_name)
        self.assertEqual("States name should be unique", str(context.exception),
                         "Failed to catch an incorrect address")


if __name__ == '__main__':
    unittest.main()
