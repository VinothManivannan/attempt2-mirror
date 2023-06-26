"""
Import unittest module to test GenerateFlatTxt
"""
import unittest
from cmlpytools.tahini.tahini_generate_flat_txt import GenerateFlatTxt, TahiniGenerateFlatError

CMAPPATH = "./tests/tahini/data/test_cmap_generate_flat.json"
FLATPATH = "./tests/tahini/data/test_cmap_generate_flat.txt"
OUTPUTPATH = "./tests/tahini/data/output_flat.txt"
INVALIDPATH = "./tests/tahini/invalid_path/invalid"


class TestGenerateFlat(unittest.TestCase):
    """ Test class for the GenerateFlatTxt class
    """

    def test_generate_flat_txt(self):
        """Test if the flat txt file is generated as expected
        """
        _ = GenerateFlatTxt.create_flat_from_cmap_path(CMAPPATH, OUTPUTPATH)
        with open(OUTPUTPATH, 'r', encoding='utf-8') as read_flat:
            with open(FLATPATH, 'r', encoding='utf-8') as flat:
                self.assertEqual(read_flat.read(), flat.read(),
                                 "Cannot output flat txt file correctly")

    def test_invalid_generate_flat_txt(self):
        """Test if invalid path can be detected when generating flat txt file
        """
        with self.assertRaises(TahiniGenerateFlatError):
            _ = GenerateFlatTxt.create_flat_from_cmap_path(CMAPPATH, INVALIDPATH)
