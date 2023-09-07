import unittest
import json
from os import path
from cmlpytools.minfs.regmap_namespace_merger import RegmapCfgMergeFile

DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "data")
FULL_REGMAP = path.join(PATH_TO_DATA, "test_fullregmap_dual_actl.cmapsource.json")

class TestRegmapCfgMergeFile(unittest.TestCase):
    def test_correct_merge(self):

        config_path = path.join(PATH_TO_DATA, "test_dual_act_correct_tl.json")
        correct_output = path.join(PATH_TO_DATA, "test_dual_act_output_correct.json")
        with open(correct_output, 'r') as f_json:
            json_config = json.loads(f_json.read())

        try:
            regmap_combined_cfg = RegmapCfgMergeFile(config_path, PATH_TO_DATA, FULL_REGMAP)
        except:
            self.fail("Failed to merge files")

        self.assertEqual(json_config, regmap_combined_cfg.merged_json, "Merge failed")

    def test_different_struct(self):

        config_path = path.join(PATH_TO_DATA, "test_dual_act_correct_tl_wrong_struct.json")

        with self.assertRaises(Exception) as context:
            _ = RegmapCfgMergeFile(config_path, PATH_TO_DATA, FULL_REGMAP)

        self.assertIn('It is only possible to merge configs with the same offset', str(
            context.exception), "Failed to catch different structs")
        
    def test_conflicting_commons(self):

        config_path = path.join(PATH_TO_DATA, "test_dual_act_correct_tl_conflicting_commons.json")

        with self.assertRaises(Exception) as context:
            _ = RegmapCfgMergeFile(config_path, PATH_TO_DATA, FULL_REGMAP)

        self.assertIn('config files contain different values', str(
            context.exception), "Failed to catch conflicting commons")

if __name__ == '__main__':
    unittest.main()
