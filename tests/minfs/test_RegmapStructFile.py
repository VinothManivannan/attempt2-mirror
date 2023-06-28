from builtins import str
import unittest
from os import path
from minfs.regmap_struct_file import *


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

    def test_8wire_axes(self):
        files = []

        regmap_params = path.join(PATH_TO_DATA, "8wire-params.json")
        regmap_file = path.join(
            PATH_TO_DATA, "shared-cml-lib-regmap-8wire_cmapsource.json")
        correct_file = path.join(PATH_TO_DATA, "8wire-params.bin")

        files.append(regmap_params)

        regmap_struct_packed = RegmapStructFile(
            files, regmap_file, "cml_params", "struct0")

        with open(correct_file, 'rb') as file_io:
            f_init = file_io.read()

        self.assertEqual(len(f_init), len(regmap_struct_packed.data))
        self.assertEqual(f_init, regmap_struct_packed.data,
                         "Files don't match")

    def test_2wire(self):
        files = []

        regmap_params = path.join(PATH_TO_DATA, "2wire-params.json")
        regmap_file = path.join(
            PATH_TO_DATA, "shared-cml-lib-regmap-2wire_cmapsource.json")
        correct_file = path.join(PATH_TO_DATA, "2wire-params.bin")

        files.append(regmap_params)

        regmap_struct_packed = RegmapStructFile(
            files, regmap_file, "cml_params", "struct0")

        with open(correct_file, 'rb') as file_io:
            f_init = file_io.read()

        self.assertEqual(f_init, regmap_struct_packed.data,
                         "Files don't match")

    def test_2wire_params_with_updated_regmap(self):
        files = []

        original_regmap_params = path.join(PATH_TO_DATA, "2wire-params.json")
        new_regmap_file = path.join(
            PATH_TO_DATA, "shared-cml-lib-regmap-2wire-with-gs_cmapsource.json")
        original_correct_file = path.join(PATH_TO_DATA, "2wire-params.bin")

        files.append(original_regmap_params)

        regmap_struct_packed = RegmapStructFile(
            files, new_regmap_file, "cml_params", "struct0")

        with open(original_correct_file, 'rb') as file_io:
            f_init = file_io.read()

        expected_length_diff = 24
        self.assertEqual(len(regmap_struct_packed.data) - len(f_init),
                         expected_length_diff, "Data lengths are not different by an expected amount")
        self.assertEqual(
            f_init, regmap_struct_packed.data[:-expected_length_diff], "Files don't match")

    def test_2wire_double_index(self):
        files = []

        new_regmap_params = path.join(PATH_TO_DATA, "2wire-params-1.json")
        new_regmap_file = path.join(
            PATH_TO_DATA, "shared-cml-lib-regmap-2wire-with-gs_cmapsource.json")
        new_correct_file = path.join(PATH_TO_DATA, "2wire-params-1.bin")

        files.append(new_regmap_params)

        regmap_struct_packed = RegmapStructFile(
            files, new_regmap_file, "cml_params", "struct0")

        with open(new_correct_file, 'rb') as file_io:
            f_init = file_io.read()

        # self.assertEqual(len(f_init), len(regmap_struct_packed.data))
        self.assertEqual(f_init, regmap_struct_packed.data,
                         "Files don't match")

    def test_8wire_thorough(self):
        files = []

        regmap_params = path.join(PATH_TO_DATA, "8wire-params-thorough.json")
        regmap_file = path.join(
            PATH_TO_DATA, "stm32_framework-8wire-thorough_cmapsource.json")
        correct_file = path.join(PATH_TO_DATA, "8wire-thorough.bin")

        files.append(regmap_params)

        regmap_struct_packed = RegmapStructFile(
            files, regmap_file, "eightwire_persist", "struct0")

        with open(correct_file, 'rb') as file_io:
            f_init = file_io.read()

        self.assertEqual(f_init, regmap_struct_packed.data,
                         "Files don't match")


if __name__ == '__main__':
    unittest.main()
