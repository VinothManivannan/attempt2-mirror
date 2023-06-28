import unittest
from os import path
from minfs.file import *
from minfs.regmap_cfg_file import RegmapCfgFile
from minfs.calmap_file import CalmapFile
from minfs.file_system import FileSystem

DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "data")


class TestFileSystem(unittest.TestCase):

    def test_createfilesystem(self):

        files = []
        regmap_cfg_json_file = path.join(
            PATH_TO_DATA, "haptics_regmap_cfg_correct.json")
        regmap_file = path.join(PATH_TO_DATA, "haptics-regmap_cmapsource.json")
        calmap_json_file = path.join(PATH_TO_DATA, "calmap_file_valid.json")
        calmap_regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")
        binary_file = path.join(PATH_TO_DATA, "binary_regmap_file.bin")

        files.append(CalmapFile(calmap_regmap_file,
                     calmap_json_file, "calmap0"))
        files.append(RegmapCfgFile(
            regmap_cfg_json_file, regmap_file, "config1"))
        files.append(File(binary_file, "REGMAP_CFG", "config2"))

        _ = FileSystem(files)

    def test_createemptyfilesystem(self):

        files = []
        try:
            file_system = FileSystem(files)
        except:
            self.fail("Failed to create a file system")

        self.assertEqual(file_system.uid, "0x%x" % 0xffffffff, "Incorrect uid")
        self.assertEqual(len(file_system.data), 8, "Incorrect data size")


if __name__ == '__main__':
    unittest.main()
