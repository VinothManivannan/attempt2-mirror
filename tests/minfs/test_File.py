from builtins import str
import unittest
from os import path
from cmlpytools.minfs.file import *

DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "data")


class TestFile(unittest.TestCase):

    def test_file_successfully(self):
        binary_file = path.join(PATH_TO_DATA, "binary_regmap_file.bin")

        try:
            file = File(binary_file, "REGMAP_CFG", "config")
        except:
            self.fail("Filed to export file")

    def test_usupported_type(self):
        binary_file = path.join(PATH_TO_DATA, "binary_regmap_file.bin")

        with self.assertRaises(Exception) as context:
            file = File(binary_file, "UNSUPPORTED", "config")

        self.assertIn('type is not supported', str(
            context.exception), "Failed to catch an incorrect type")


if __name__ == '__main__':
    unittest.main()
