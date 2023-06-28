from builtins import str
import unittest
from os import path
from cmlpytools.minfs.regmap_struct_file import *


DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "data")


class TestRegmapStructFile(unittest.TestCase):

    def test_correct_config(self):
        files = []

        regmap_params = path.join(PATH_TO_DATA, "4wire-params.json")
        regmap_file = path.join(PATH_TO_DATA, "shared-cml-lib-regmap_cmapsource.json")
        correct_file = path.join(PATH_TO_DATA, "4wire-params.bin")

        files.append(regmap_params)

        regmap_struct_packed = RegmapStructFile(
            files, regmap_file, "cml_params", "struct0")

        with open(correct_file, 'rb') as file_io:
            f_init = file_io.read()

        packed_data = bytes(regmap_struct_packed.data)
        self.assertEqual(f_init, packed_data, "Files don't match")

    def test_multiple_files(self):
        files = []

        regmap_params1 = path.join(PATH_TO_DATA, "4wire-params-1.json")
        regmap_params2 = path.join(PATH_TO_DATA, "4wire-params-2.json")
        regmap_file = path.join(PATH_TO_DATA, "shared-cml-lib-regmap_cmapsource.json")
        correct_file = path.join(PATH_TO_DATA, "4wire-params.bin")

        files.append(regmap_params1)
        files.append(regmap_params2)

        regmap_struct_packed = RegmapStructFile(
            files, regmap_file, "cml_params", "struct0")

        with open(correct_file, 'rb') as file_io:
            f_init = file_io.read()

        self.assertEqual(f_init, regmap_struct_packed.data,
                         "Files don't match")

    def test_incorrect_config(self):
        files = []

        regmap_params = path.join(PATH_TO_DATA, "4wire-params-incorrect.json")
        regmap_file = path.join(PATH_TO_DATA, "shared-cml-lib-regmap_cmapsource.json")
        correct_file = path.join(PATH_TO_DATA, "4wire-params.bin")

        files.append(regmap_params)

        regmap_struct_packed = RegmapStructFile(
            files, regmap_file, "cml_params", "struct0")

        with open(correct_file, 'rb') as file_io:
            f_init = file_io.read()

        self.assertNotEqual(f_init, regmap_struct_packed.data, "Files match")

    def test_incorrect_struct(self):
        files = []

        regmap_params = path.join(PATH_TO_DATA, "4wire-params.json")
        regmap_file = path.join(PATH_TO_DATA, "shared-cml-lib-regmap_cmapsource.json")

        files.append(regmap_params)

        with self.assertRaises(Exception) as context:
            _ = RegmapStructFile(
                files, regmap_file, "incorrect_params", "struct0")

        self.assertIn('Structure not found', str(context.exception),
                      "The requested structure is not found")


if __name__ == '__main__':
    unittest.main()
