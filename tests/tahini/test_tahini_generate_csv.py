"""
Import unittest module to test GenerateAppnoteCSV
"""
import unittest
from tahini.tahini_generate_appnote_csv import GenerateAppnoteCSV

OUTPUTPATH = "./tests/output_tahini_generate_csv.csv"
REFPATH = "./tests/data/test_tahini_generate_csv.csv"
CMAPPATH = "./tests/data/test_tahini_generate_csv.json"


class TestGenerateCSV(unittest.TestCase):
    """ Test class for the GenerateAppnoteCSV class
    """

    def test_generate_appnote_csv(self):
        """Test that appnote csv file generated is identical to reference sample
        """
        GenerateAppnoteCSV.create_csv_from_cmap_path(CMAPPATH, OUTPUTPATH)

        with open(OUTPUTPATH, 'r', encoding='utf-8') as output:
            output_data = output.read()

        with open(REFPATH, 'r', encoding='utf-8') as ref:
            ref_data = ref.read()

        self.assertEqual(ref_data, output_data)
