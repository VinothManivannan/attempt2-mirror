import unittest
from os import path
from minfs.calmap_file import CalmapFile
from minfs.calmap_file import CalmapParseError


DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "data")


class TestCalmapFile(unittest.TestCase):
    '''
    Test class for the CalmapFile class
    '''

    def test_correct_map_file(self):
        '''
        Testing that valid calmap and regmaps are correctly parsed by the calmap class
        '''
        calmap_json_file = path.join(PATH_TO_DATA, "calmap_file_valid.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        _ = CalmapFile(regmap_file, calmap_json_file)

    def test_invalid_register(self):
        '''
        Testing that a calmap register that doesn't exist in the regmap does not
        causes an exception
        '''
        calmap_json_file = path.join(
            PATH_TO_DATA, "calmap_invalid_register.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        with self.assertRaises(CalmapParseError) as context:
            calmap_file = CalmapFile(regmap_file, calmap_json_file)

    def test_invalid_persist(self):
        '''
        Testing that specifying a calmap persistent (param) struct that doesn't exist
        in the regmap causes an exception
        '''
        calmap_json_file = path.join(
            PATH_TO_DATA, "calmap_invalid_persist.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        with self.assertRaises(CalmapParseError) as context:
            calmap_file = CalmapFile(regmap_file, calmap_json_file)

    def test_invalid_fw_regs(self):
        '''
        Testing that specifying a calmap firware resgister struct that doesn't exist
        in the regmap causes an exception
        '''
        calmap_json_file = path.join(
            PATH_TO_DATA, "calmap_invalid_fw_regs.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        with self.assertRaises(CalmapParseError) as context:
            calmap_file = CalmapFile(regmap_file, calmap_json_file)

    def test_missing_type(self):
        '''
        Testing that a calmap register definition which is missing the 'type' member
        causes an exception
        '''
        calmap_json_file = path.join(PATH_TO_DATA, "calmap_missing_type.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        with self.assertRaises(CalmapParseError) as context:
            calmap_file = CalmapFile(regmap_file, calmap_json_file)

    def test_missing_bytes(self):
        '''
        Testing that a calmap register definition which is missing the 'bytes' member
        causes an exception
        '''
        calmap_json_file = path.join(PATH_TO_DATA, "calmap_missing_bytes.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        with self.assertRaises(CalmapParseError) as context:
            calmap_file = CalmapFile(regmap_file, calmap_json_file)

    def test_missing_validity_offset(self):
        '''
        Testing that a calmap register definition which is missing the 'valid_flag_offset' member
        causes an exception
        '''
        calmap_json_file = path.join(
            PATH_TO_DATA, "calmap_missing_valid_flag.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        with self.assertRaises(CalmapParseError) as context:
            calmap_file = CalmapFile(regmap_file, calmap_json_file)

    def test_missing_cal_buffer_offset(self):
        '''
        Testing that a calmap register definition which is missing the 'offset_in_cal_buffer' member
        causes an exception
        '''
        calmap_json_file = path.join(
            PATH_TO_DATA, "calmap_missing_offset.json")
        regmap_file = path.join(PATH_TO_DATA, "calmap_regmap_cmapsource.json")

        with self.assertRaises(CalmapParseError) as context:
            calmap_file = CalmapFile(regmap_file, calmap_json_file)


if __name__ == '__main__':
    unittest.main()
