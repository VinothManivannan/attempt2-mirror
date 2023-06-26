"""
Import unittest module to test GenerateTxt
"""
import unittest
from tahini.tahini_generate_txt import GenerateTxt

CMAP_PATH = "./tests/data/test_tahini_generate_txt.json"
OUTPUT_PATH = "./tests/output_generate_txt.txt"
COMPARE_PATH = "./tests/data/test_tahini_generate_txt.txt"

TEST_CMAP_PATH = "./tests/data/test_cmap_generate_txt.json"
TEST_OUTPUT_PATH = "./tests/data/output_test_generate_txt.txt"
TEST_BITFIELDS_STATES_PATH = "./tests/data/test_tahini_generate_txt_bitfields_state.json"
TEST_COMPARE_BITFIELDS_STATES_PATH = "./tests/data/test_tahini_generate_txt_bitfields_state.txt"
TEST_OUTPUT_BITFIELDS_STATES_PATH = "./tests/output_generate_txt_bitfields_state.txt"


class TestGenerateFlat(unittest.TestCase):
    """ Test class for the GenerateTxt class
    """

    def test_generate_txt(self):
        """Test if the txt file is generated as expected
        """
        _ = GenerateTxt.create_txt_from_cmap_path(CMAP_PATH, OUTPUT_PATH)
        with open(OUTPUT_PATH, 'r', encoding='utf-8') as read_txt:
            with open(COMPARE_PATH, 'r', encoding='utf-8') as txt:
                self.assertEqual(read_txt.read(), txt.read(),
                                 "Cannot output txt file correctly")

    def test_generate_txt_states_bitfields(self):
        """Test if states in bitfields in txt output file can be generate correctly
        """
        # states of bitfields
        _ = GenerateTxt.create_txt_from_cmap_path(TEST_BITFIELDS_STATES_PATH, TEST_OUTPUT_BITFIELDS_STATES_PATH)
        with open(TEST_OUTPUT_BITFIELDS_STATES_PATH, 'r', encoding='utf-8') as read_state:
            with open(TEST_COMPARE_BITFIELDS_STATES_PATH, 'r', encoding='utf-8') as state:
                self.assertEqual(read_state.read(), state.read(),
                                 "Cannot output states info in bitfields correctly")
