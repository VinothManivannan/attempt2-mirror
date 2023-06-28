from builtins import str
from builtins import range
import unittest
from os import path
from minfs.regmap_cfg_file import *


DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "data")


class TestRegmapCfgFile(unittest.TestCase):

    def test_correct_config(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "haptics_regmap_cfg_correct.json")
        regmap_file = path.join(PATH_TO_DATA, "haptics-regmap_cmapsource.json")

        _ = RegmapCfgFile(regmap_cfg_json_file, regmap_file)

    def test_incorrect_flag(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "haptics_regmap_cfg_incorrect_flag.json")
        regmap_file = path.join(PATH_TO_DATA, "haptics-regmap_cmapsource.json")

        with self.assertRaises(RegmapCfgParseError) as context:
            _ = RegmapCfgFile(regmap_cfg_json_file, regmap_file)

    def test_incorrect_register(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "haptics_regmap_cfg_incorrect_register.json")
        regmap_file = path.join(PATH_TO_DATA, "haptics-regmap_cmapsource.json")

        with self.assertRaises(RegmapCfgParseError) as context:
            _ = RegmapCfgFile(regmap_cfg_json_file, regmap_file)

    def test_incorrect_member(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "haptics_regmap_cfg_incorrect_member.json")
        regmap_file = path.join(PATH_TO_DATA, "haptics-regmap_cmapsource.json")

        with self.assertRaises(RegmapCfgParseError):
            _ = RegmapCfgFile(regmap_cfg_json_file, regmap_file)

    def test_incorrect_state(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "stm32_config_state_incorrect.json")
        regmap_file = path.join(PATH_TO_DATA, "stm32_framework_cmapsource.json")

        with self.assertRaises(RegmapCfgParseError) as context:
            _ = RegmapCfgFile(regmap_cfg_json_file, regmap_file)

    def test_correct_state(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "stm32_config_state_correct.json")
        regmap_file = path.join(PATH_TO_DATA, "stm32_framework_cmapsource.json")

        _ = RegmapCfgFile(regmap_cfg_json_file, regmap_file)

    def test_correct_compression_mode(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "stm32_config_state_correct.json")
        regmap_file = path.join(PATH_TO_DATA, "stm32_framework_cmapsource.json")

        num_modes = 3  # Only values 0,1, and 2 are valid compression modes
        for i in range(num_modes):
            _ = RegmapCfgFile(regmap_cfg_json_file, regmap_file, "config0",
                              compressed=i)

    def test_incorrect_compression_mode(self):
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "stm32_config_state_correct.json")
        regmap_file = path.join(PATH_TO_DATA, "stm32_framework_cmapsource.json")

        with self.assertRaises(RegmapCfgParseError) as context:
            _ = RegmapCfgFile(
                regmap_cfg_json_file, regmap_file, "config0", 3)

    def test_distances_of_compression_modes(self):
        # haptics_regmap_distances.json file contains 8 registers:
        # - ACTION_EVENTID0", "ACTION_WAVEFORMID0", "ACTION_ACTUATORID0" are contiguous
        # - 9 bytes gap
        # - ACTION_EVENTID1", "ACTION_WAVEFORMID1", "ACTION_ACTUATORID1" are contiguous
        # - 70 bytes gap
        # - WF_PULSES0
        # - 2 bytes gap
        # - WF_DELAY0_0
        #
        # Mode 0 should produce 8 entries
        # Mode 1 should produce 4 entries
        # Mode 2 should produce 3 entries
        #
        # The number of etries is stored in the third byte of the byte array of the generated file.

        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "haptics_regmap_distances.json")
        regmap_file = path.join(PATH_TO_DATA, "haptics-regmap_cmapsource.json")

        regmap_cfg_file = RegmapCfgFile(
            regmap_cfg_json_file, regmap_file, "config0", 0)
        num_entries = regmap_cfg_file.data[2]
        self.assertEqual(num_entries, 8)

        regmap_cfg_file = RegmapCfgFile(
            regmap_cfg_json_file, regmap_file, "config0", 1)
        num_entries = regmap_cfg_file.data[2]
        self.assertEqual(num_entries, 4)

        regmap_cfg_file = RegmapCfgFile(
            regmap_cfg_json_file, regmap_file, "config0", 2)
        num_entries = regmap_cfg_file.data[2]
        self.assertEqual(num_entries, 3)


if __name__ == '__main__':
    unittest.main()
