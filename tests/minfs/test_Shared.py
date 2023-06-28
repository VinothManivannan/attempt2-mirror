from builtins import str
import unittest
from minfs.shared import *
from minfs.file_types import FileTypes

class TestSharedLibrary(unittest.TestCase):

    def test_AddEntrySuccesfully(self):
        MAX_FILES = 0x1
        ADDR = 0x1234
        DATA = bytearray([0xBA, 0xAD, 0xBE, 0xEF])
        
        try:
            whandle = RegmapFileWriter(MAX_FILES, len(DATA))
        except:
            self.fail("failed to allocate handle")
        
        try:
            whandle.add_entry(ADDR, DATA)
        except:
            self.fail("can't add entry")
            
    def test_AddEntryUnsuccesfully(self):
        """
        Try to add an entry larger than the buffer
        """
        MAX_FILES = 0x1
        ADDR = 0x1234
        DATA = bytearray([0xBA, 0xAD, 0xBE, 0xEF])
        
        whandle = RegmapFileWriter(MAX_FILES, len(DATA)-1)
        
        with self.assertRaises(Exception) as context:
            whandle.add_entry(ADDR, DATA)
            
        self.assertIn('Invalid buffer', str(context.exception), "Failed to return the correct error message")    

    def test_GetFile(self):
        """
        Read the file and check if the file size is correct
        """
        HEADER_SIZE = 8
        ENTRY_SIZE = 6
        MAX_FILES = 0x1
        ADDR = 0x1234
        DATA = bytearray([0xBA, 0xAD, 0xBE, 0xEF])
        
        whandle = RegmapFileWriter(MAX_FILES, len(DATA))
        whandle.add_entry(ADDR, DATA)
        
        try:
            file = whandle.get_file()
        except:
            self.fail("failed to getfile")
            
        self.assertEqual(HEADER_SIZE + ENTRY_SIZE + len(DATA), len(file), "Incorrect file size")
        
    def test_AddFile(self):
        """
        Read the file and check if the file size is correct
        """    
        HEADER_SIZE = 8
        ENTRY_SIZE = 6
        MAX_FILES = 0x1
        ADDR = 0x1234
        DATA = bytearray([0xBA, 0xAD, 0xBE, 0xEF])
        
        whandle = RegmapFileWriter(MAX_FILES, len(DATA))
        whandle.add_entry(ADDR, DATA)
        file = whandle.get_file()
        
        fs_size = HEADER_SIZE + ENTRY_SIZE + len(DATA)

        try:
            file_system = FileSystemWriter(1, fs_size*2)
        except:
            self.fail("failed to create a file system")             
        
        try:
            file_system.add_file("configf", FileTypes.REGMAP_CFG, file, 1)
        except:
            self.fail("failed to add file")

    def test_CalmapAddEntry(self):
        '''
        Test that a calmap entry can be added successfully
        '''
        MAX_ENTRIES = 1
        MAP_VER = 1
        ENTRY_TYPE = 3
        NUM_BYTES = 4
        VALIDITY_FLAG_OFFSET = 1
        CAL_BUFFER_OFFSET = 2
        REGMAP_OFFSET = 3

        try:
            whandle = CalmapFileWriter(MAX_ENTRIES, MAP_VER)
        except:
            self.fail("failed to allocate CalmapFileWriter handle")

        try:
            whandle.add_entry(ENTRY_TYPE, NUM_BYTES, VALIDITY_FLAG_OFFSET, CAL_BUFFER_OFFSET, REGMAP_OFFSET)
        except:
            self.fail("can't add calmap entry")

    def test_CalmapGetFile(self):
        """
        Read the calmap file and check if the file size is correct
        """
        HEADER_SIZE = 4
        ENTRY_SIZE = 8
        MAX_ENTRIES = 1
        MAP_VER = 1
        ENTRY_TYPE = 3
        NUM_BYTES = 4
        VALIDITY_FLAG_OFFSET = 1
        CAL_BUFFER_OFFSET = 2
        REGMAP_OFFSET = 3

        whandle = CalmapFileWriter(MAX_ENTRIES, MAP_VER)
        whandle.add_entry(ENTRY_TYPE, NUM_BYTES, VALIDITY_FLAG_OFFSET, CAL_BUFFER_OFFSET, REGMAP_OFFSET)

        try:
            calfile = whandle.get_file()
        except:
            self.fail("failed to get calmap file")

        self.assertEqual(HEADER_SIZE + (ENTRY_SIZE * MAX_ENTRIES), len(calfile), "Incorrect file size")

    def test_CalmapAddFile(self):
        """
        Test that a calmap file can be added to a filesystem
        """
        HEADER_SIZE = 4
        ENTRY_SIZE = 8
        MAX_ENTRIES = 1
        MAP_VER = 1
        ENTRY_TYPE = 3
        NUM_BYTES = 4
        VALIDITY_FLAG_OFFSET = 1
        CAL_BUFFER_OFFSET = 2
        REGMAP_OFFSET = 3

        whandle = CalmapFileWriter(MAX_ENTRIES, MAP_VER)
        whandle.add_entry(ENTRY_TYPE, NUM_BYTES, VALIDITY_FLAG_OFFSET, CAL_BUFFER_OFFSET, REGMAP_OFFSET)
        calfile = whandle.get_file()

        fs_size = HEADER_SIZE + (ENTRY_SIZE * MAX_ENTRIES)

        try:
            file_system = FileSystemWriter(1, fs_size)
        except:
            self.fail("failed to create a file system")

        try:
            file_system.add_file("calmap0", FileTypes.CALMAP, calfile, 2)
        except:
            self.fail("failed to add file")

if __name__ == '__main__':
    unittest.main()
