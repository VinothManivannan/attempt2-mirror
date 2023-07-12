import unittest
from cmlpytools.minfs.binary_data import *

FILE_TEMPLATE = """\
/*
 * This file has been generated by CML build tools.
 */

#ifndef __MINFS_FILE_H__
#define __MINFS_FILE_H__

/***************************************************************************************************
* Macro definitions
***************************************************************************************************/

/* MinFS data */
#define MINFS_FILE {\\
    %%BYTE_ARRAY%% \\
}

#endif /* __MINFS_FILE_H__ */
"""


class BinaryDataChild(BinaryData):

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, newdata):
        self._data = newdata


class TestBinaryData(unittest.TestCase):

    def test_tobin(self):
        DATA = bytearray([0xBA, 0xAD, 0xBE, 0xEF])

        binary_child = BinaryDataChild()
        binary_child.data = DATA
        binary_child.tobin("bin_test.bin")
        file = open("bin_test.bin", 'rb')
        file_ba = file.read()

        self.assertEqual(file_ba, DATA, "files are not identical")

    def test_tocheader(self):
        DATA = bytearray([0xBA, 0xAD, 0xBE, 0xEF])
        DATA_STR = "0xBA,0xAD,0xBE,0xEF,"

        header_data = FILE_TEMPLATE.replace("%%BYTE_ARRAY%%", DATA_STR)
        binary_child = BinaryDataChild()
        binary_child.data = DATA
        binary_child.tocheader("bin_header.h")
        file = open("bin_header.h", 'r', encoding="utf-8").read()

        self.assertEqual(file, header_data, "files are not identical")


if __name__ == '__main__':
    unittest.main()