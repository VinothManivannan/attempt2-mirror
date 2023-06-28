import unittest
from os import path
from cmlpytools.minfs.file import *
from cmlpytools.minfs.regmap_cfg_file import RegmapCfgFile
from cmlpytools.minfs.calmap_file import CalmapFile
from cmlpytools.minfs.file_system import FileSystem

DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "data")


class TestFileSystem(unittest.TestCase):
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
