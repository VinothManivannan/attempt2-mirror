"""
Import unittest and FullRegmap modules to test
"""
from os import path
import unittest
import marshmallow.exceptions
from tahini.cmap_schema import FullRegmap as CmapFullRegmap
from tahini.cmap_schema import Register as CmapRegister
from tahini.cmap_schema import State as CmapState
from tahini.cmap_schema import Bitfield as CmapBitfield
from tahini.cmap_schema import Type, VisibilityOptions, CType, InvalidBitfieldsError,\
    InvalidRegisterError, InvalidStatesError, InvalidRegisterStructError, InvalidRepeatForError

PATH_TO_DATA = "./tests/data"
FIELD_REGMAP_DATA = 'regmap'


class TestFilePath(unittest.TestCase):
    """Class that check if json files used are valid
    """
    path_fullregmap = path.join(PATH_TO_DATA, "test_fullregmap.json")
    path_fullregmap_children = path.join(PATH_TO_DATA, "test_fullregmap_children.json")
    path_valid_register = path.join(PATH_TO_DATA, "test_fullregmap_register.json")
    path_valid_bitfields = path.join(PATH_TO_DATA, "test_fullregmap_register_bitfields.json")
    path_valid_states = path.join(PATH_TO_DATA, "test_fullregmap_register_states.json")
    path_valid_struct = path.join(PATH_TO_DATA, "test_fullregmap_struct.json")
    path_valid_common = path.join(PATH_TO_DATA, "test_fullregmap_structreg_common.json")
    path_invalid_register_format = path.join(PATH_TO_DATA, "test_fullregmap_invalid_format.json")
    path_invalid_register_bitsize = path.join(PATH_TO_DATA, "test_fullregmap_invalid_format_ctype.json")
    path_invalid_register_max1 = path.join(PATH_TO_DATA, "test_fullregmap_invalid_unsigned_maxvalue.json")
    path_invalid_register_max2 = path.join(PATH_TO_DATA, "test_fullregmap_invalid_signed_maxvalue.json")
    path_invalid_register_min = path.join(PATH_TO_DATA, "test_fullregmap_invalid_min_max_exist.json")
    path_invalid_register_minmax = path.join(PATH_TO_DATA, "test_fullregmap_invalid_min_max_value.json")
    path_invalid_reg_min_unsigned = path.join(PATH_TO_DATA, "test_fullregmap_invalid_min_unsigned.json")
    path_invalid_bitfields_name = path.join(PATH_TO_DATA, "test_fullregmap_invalid_bitfields_name.json")
    path_invalid_bitfields_position = path.join(PATH_TO_DATA, "test_fullregmap_invalid_bitfields_position.json")
    path_invalid_bitfields_numbits = path.join(PATH_TO_DATA, "test_fullregmap_invalid_bitfields_numbits.json")
    path_invalid_bitfields_ctype = path.join(PATH_TO_DATA, "test_fullregmap_invalid_bitfields_ctype.json")
    path_invalid_bitfields_limit = path.join(PATH_TO_DATA, "test_fullregmap_invalid_bitfields_limit.json")
    path_invalid_bitfields_states = path.join(PATH_TO_DATA, "test_fullregmap_invalid_bitfields_states.json")
    path_invalid_bitfields_overlap = path.join(PATH_TO_DATA, "test_fullregmap_invalid_bitfields_overlap.json")
    path_invalid_states_unique = path.join(PATH_TO_DATA, "test_fullregmap_invalid_states_unique.json")
    path_invalid_states_unsigned = path.join(PATH_TO_DATA, "test_fullregmap_invalid_states_unsigned.json")
    path_invalid_states_signed = path.join(PATH_TO_DATA, "test_fullregmap_invalid_states_signed.json")
    path_invalid_states_bitlength = path.join(PATH_TO_DATA, "test_fullregmap_invalid_states_bitlength.json")
    path_invalid_states_minmax = path.join(PATH_TO_DATA, "test_fullregmap_invalid_states_minmax.json")
    path_invalid_common_addr = path.join(PATH_TO_DATA, "test_fullregmap_invalid_common_addr.json")
    path_invalid_common_nonfield = path.join(PATH_TO_DATA, "test_fullregmap_invalid_common_nonfield.json")
    path_invalid_common_existfield = path.join(PATH_TO_DATA, "test_fullregmap_invalid_common_existfield.json")
    path_invalid_repeat_for = path.join(PATH_TO_DATA, "test_fullregmap_invalid_repeat_for.json")
    path_invalid_repeat_for_aliases = path.join(PATH_TO_DATA, "test_fullregmap_invalid_repeat_for_aliases.json")
    path_invalid_duplicated_names = path.join(PATH_TO_DATA, "test_fullregmap_invalid_duplicated_registers.json")

    @staticmethod
    def read_json(json_path):
        """Read json files
        """
        with open(json_path, 'r', encoding='utf-8') as loadfile:
            data_open = loadfile.read()
        return data_open

    def test_path(self):
        """Check if the path is a valid string
        """
        self.read_json(self.path_fullregmap)
        self.read_json(self.path_fullregmap_children)
        self.read_json(self.path_valid_register)
        self.read_json(self.path_valid_bitfields)
        self.read_json(self.path_valid_states)
        self.read_json(self.path_valid_struct)
        self.read_json(self.path_valid_common)
        self.read_json(self.path_invalid_register_format)
        self.read_json(self.path_invalid_register_bitsize)
        self.read_json(self.path_invalid_register_max1)
        self.read_json(self.path_invalid_register_max2)
        self.read_json(self.path_invalid_register_min)
        self.read_json(self.path_invalid_register_minmax)
        self.read_json(self.path_invalid_reg_min_unsigned)
        self.read_json(self.path_invalid_bitfields_name)
        self.read_json(self.path_invalid_bitfields_position)
        self.read_json(self.path_invalid_bitfields_numbits)
        self.read_json(self.path_invalid_bitfields_ctype)
        self.read_json(self.path_invalid_bitfields_limit)
        self.read_json(self.path_invalid_bitfields_states)
        self.read_json(self.path_invalid_bitfields_overlap)
        self.read_json(self.path_invalid_states_unique)
        self.read_json(self.path_invalid_states_unsigned)
        self.read_json(self.path_invalid_states_signed)
        self.read_json(self.path_invalid_states_bitlength)
        self.read_json(self.path_invalid_states_minmax)
        self.read_json(self.path_invalid_common_addr)
        self.read_json(self.path_invalid_common_nonfield)
        self.read_json(self.path_invalid_common_existfield)
        self.read_json(self.path_invalid_repeat_for)
        self.read_json(self.path_invalid_repeat_for_aliases)
        self.read_json(self.path_invalid_duplicated_names)


class TestFullRegmap(unittest.TestCase):
    """Test class for the FullRegmap class
    """

    def test_children_loadjson(self):
        """Test if json file can be loaded correctly
        Test:
            (Obj: Exception message)
            children field: Children field is not identical
        """
        data_schema_fullregmap = CmapFullRegmap.load_json(TestFilePath.path_fullregmap)
        data_fullregmap_children = CmapFullRegmap.load_json(TestFilePath.path_fullregmap_children)
        data_schema_dumps_fullregmap = data_schema_fullregmap.regmap.children[0]
        data_dumps_fullregmap_children = data_fullregmap_children.regmap.children[0]
        self.assertEqual(data_schema_dumps_fullregmap, data_dumps_fullregmap_children,
                         "Children field is not identical")

    def test_duplicate_names_trigger_exception(self):
        """Check that attempting to create a cmapsource files with duplicate struct or regs fails and
        cause an exception.
        """
        with self.assertRaises(InvalidRegisterStructError):
            CmapFullRegmap.load_json(TestFilePath.path_invalid_duplicated_names)

    def test_valid_register_property(self):
        """Test if properties in register part are defined correctly
        Test:
            (Obj: Exception message)
            ctype: Children field is not identical
            format: Required format value is not matched
            min: Required minimum value is not matched
            max: Required maximum value is not matched
            units: Required units value is not matched
        """
        data = CmapFullRegmap.load_json(TestFilePath.path_valid_register)
        data_children = data.regmap.children[0]
        self.assertEqual(CType.UINT16.value, data_children.register.ctype.value,
                         "Required ctype value is not matched")
        self.assertEqual("Q10.5", data_children.register.format,
                         "Required format value is not matched")
        self.assertEqual(10.0, data_children.register.min,
                         "Required minimum value is not matched")
        self.assertEqual(100.0, data_children.register.max,
                         "Required maximum value is not matched")
        self.assertEqual(None, data_children.register.units,
                         "Required units value is not matched")

    def test_valid_bitfields_property(self):
        """Test if properties in bitfields part are defined correctly
        Test:
            (Obj: Exception message)
            position: Required bitfields position value is not matched
            num_bits: Required bitfields num_bits value is not matched
        """
        data = CmapFullRegmap.load_json(TestFilePath.path_valid_bitfields)
        data_children = data.regmap.children[0]
        self.assertEqual(7, data_children.register.bitfields[0].position,
                         "Required bitfields position value is not matched")
        self.assertEqual(1, data_children.register.bitfields[0].num_bits,
                         "Required bitfields num_bits value is not matched")

    def test_valid_states_property(self):
        """Test if properties in states part are defined correctly
        Test:
            (Obj: Exception message)
            name: Required states name is not matched
            value: Required states value is not matched
        """
        data = CmapFullRegmap.load_json(TestFilePath.path_valid_states)
        data_children = data.regmap.children[0]
        self.assertEqual("ray_off", data_children.register.states[0].name,
                         "Required states name is not matched")
        self.assertEqual(0, data_children.register.states[0].value,
                         "Required states value is not matched")

    def test_valid_struct_property(self):
        """Test if properties in sub struct part are defined correctly
        Test:
            (Obj: Exception message)
            name: Required sub struct name is not matched
        """
        data = CmapFullRegmap.load_json(TestFilePath.path_valid_struct)
        data_children = data.regmap.children[0]
        self.assertEqual("fetched", data_children.struct.children[0].name,
                         "Required sub struct name is not matched")

    def test_valid_common_property(self):
        """Test if the common properties in struct and register parts are defined correctly
        Test:
            (Obj: Exception message)
            type: Required type is not matched
            name: Required name is not matched
            brief: Required name is not matched
            namespace: Required namespace is not matched
            access: Required visibility is not matched
            offset: Required offset is not matched
            addr: Required address is not matched
            count: Required aliases and count is not matched
        """
        data = CmapFullRegmap.load_json(TestFilePath.path_valid_common)
        data_children = data.regmap.children[0]
        self.assertEqual(Type.REGISTER.value, data_children.type.value, "Required type is not matched")
        self.assertEqual('me', data_children.name, "Required name is not matched")
        self.assertEqual("A name I call myself", data_children.brief, "Required brief is not matched")
        self.assertEqual('i', data_children.namespace, "Required namespace is not matched")
        self.assertEqual(VisibilityOptions.PRIVATE.value, data_children.access.value,
                         "Required visibility is not matched")
        self.assertEqual(0, data_children.offset, "Required offset is not matched")
        self.assertEqual(3072, data_children.addr, "Required address is not matched")
        self.assertEqual(2, data_children.size, "Required size is not matched")
        self.assertEqual(3, data_children.repeat_for[0].count, "Required aliases and count is not matched")

    def test_invalid_register_property(self):
        """Test if invalid checks in register field can be raised correctly
        """
        with self.assertRaises(InvalidRegisterError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_register_format)
        self.assertIn("Format is wrong which should be: Qn.m, Qn", str(context.exception),
                      "Failed to catch an incorrect format of register")

        with self.assertRaises(InvalidRegisterError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_register_bitsize)
        self.assertIn("The format is not support the ctype", str(context.exception),
                      "Failed to catch an incorrect ctype of register")

        with self.assertRaises(InvalidRegisterError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_register_max1)
        self.assertIn("The unsigned max value exceeds the limit of format", str(context.exception),
                      "Failed to catch an incorrect unsigned max value of register")

        with self.assertRaises(InvalidRegisterError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_register_max2)
        self.assertIn("The signed max value exceeds the limit of format", str(context.exception),
                      "Failed to catch an incorrect signed max value of register")

        with self.assertRaises(InvalidRegisterError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_register_min)
        self.assertIn("Minimum value is missing", str(context.exception),
                      "Failed to catch an incorrect missing minimum value of register")

        with self.assertRaises(InvalidRegisterError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_register_minmax)
        self.assertIn("Minimum value should be smaller than maximum value", str(context.exception),
                      "Failed to catch an incorrect min max value of register")

        with self.assertRaises(InvalidRegisterError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_reg_min_unsigned)
        self.assertIn("Minimum value should not be smaller than 0 in unsigned ctype", str(context.exception),
                      "Failed to catch an incorrect minimum value of register")

    def test_invalid_bitfields_property(self):
        """Test if invalid checks in bitfields field can be raised correctly
        """
        with self.assertRaises(InvalidBitfieldsError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_bitfields_name)
        self.assertIn("Invalid name", str(context.exception),
                      "Failed to catch an incorrect name of bitfields")

        with self.assertRaises(InvalidBitfieldsError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_bitfields_position)
        self.assertIn("Position value should not be lower than 0", str(context.exception),
                      "Failed to catch an incorrect position of bitfields")

        with self.assertRaises(InvalidBitfieldsError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_bitfields_numbits)
        self.assertIn("Num_bits value should not be lower than 1", str(context.exception),
                      "Failed to catch an incorrect num_bits of bitfields")

        with self.assertRaises(InvalidBitfieldsError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_bitfields_ctype)
        self.assertIn("Bitfields position or num_bits values exceed the limit of ctype", str(context.exception),
                      "Failed to catch an incorrect property in bitfields in terms of the ctype")

        with self.assertRaises(InvalidBitfieldsError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_bitfields_states)

        with self.assertRaises(InvalidBitfieldsError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_bitfields_limit)
        self.assertIn("Invalid position or num_bits to the ctype", str(context.exception),
                      "Failed to catch an incorrect bitfields to exceed the limit of ctype")

        with self.assertRaises(InvalidBitfieldsError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_bitfields_overlap)
        self.assertIn("Overlap bitfields detected", str(context.exception),
                      "Failed to catch an incorrect overlap of bitfields")

    def test_invalid_states_property(self):
        """Test if invalid checks in states field can be raised correctly
        """
        with self.assertRaises(InvalidStatesError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_states_unique)
        self.assertIn("States value should be unique", str(context.exception),
                      "Failed to catch an incorrect duplicate states")

        with self.assertRaises(InvalidStatesError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_states_unsigned)
        self.assertIn("Unsigned value should not be smaller than 0", str(context.exception),
                      "Failed to catch an incorrect unsigned value of states")

        with self.assertRaises(InvalidStatesError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_states_signed)
        self.assertIn("States value exceed the limit of signed ctype", str(context.exception),
                      "Failed to catch an incorrect signed value of signed")

        with self.assertRaises(InvalidStatesError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_states_bitlength)
        self.assertIn("States value exceed the limit of unsigned ctype", str(context.exception),
                      "Failed to catch an incorrect bitlength of states")

        with self.assertRaises(InvalidStatesError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_states_minmax)
        self.assertIn("States value should not be smaller than minimum value", str(context.exception),
                      "Failed to catch an incorrect bitlength of states")

    def test_invalid_common_property(self):
        """Test if invalid checks in common properties field can be raised correctly
        """
        with self.assertRaises(InvalidRegisterStructError):
            CmapFullRegmap.load_json(TestFilePath.path_invalid_common_addr)

        with self.assertRaises(InvalidRegisterStructError):
            CmapFullRegmap.load_json(TestFilePath.path_invalid_common_nonfield)

        with self.assertRaises(InvalidRegisterStructError):
            CmapFullRegmap.load_json(TestFilePath.path_invalid_common_existfield)

    def test_invalid_repeat_for_property(self):
        """Test if invalid checks in repeat_for field can be raised correctly
        """
        with self.assertRaises(InvalidRepeatForError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_repeat_for)
        self.assertIn("Count value in ArrayIndex should not be smaller than 1", str(context.exception),
                      "Failed to catch an incorrect count value in repeat_for field")

        with self.assertRaises(InvalidRepeatForError) as context:
            CmapFullRegmap.load_json(TestFilePath.path_invalid_repeat_for_aliases)
        self.assertIn("Count value should be the number of aliases list", str(context.exception),
                      "Failed to catch an incorrect count value in terms of aliases")

    def test_invalid_member_in_nested_class_throws_validation_error(self):
        """Test that if the json to be deserialised contains an invalid field
        in a nested dataclass, then an exception is thrown.
        """
        json_data = '{"regmap":{"i2c_addr": "100", "children":[]}}'  # Invalid unknown `i2c_addr` member

        with self.assertRaises(marshmallow.exceptions.ValidationError):
            print(CmapFullRegmap.from_json(json_data))

    def test_missing_non_optional_member_throws_validation_error(self):
        """Test that if the json to be deserialised misses non-optional member, then an exception is thrown.
        """
        json_data = '{"regmap":{}}'  # Missing `children` member
        with self.assertRaises(marshmallow.exceptions.ValidationError):
            print(CmapFullRegmap.from_json(json_data))


class TestDataPacking(unittest.TestCase):
    """Test class for the FullRegmap class
    """

    def test_pack_value(self):
        """Check pack_value() function works as expected
        """
        self.assertEqual(bytes([0x12]), CmapRegister(ctype=CType.UINT8).pack_value(0x12))
        self.assertEqual(bytes([0x34, 0x12]), CmapRegister(ctype=CType.UINT16).pack_value(0x1234))
        self.assertEqual(bytes([0x78, 0x56, 0x34, 0x12]), CmapRegister(ctype=CType.UINT32).pack_value(0x12345678))
        self.assertEqual(bytes([0xFE]), CmapRegister(ctype=CType.INT8).pack_value(-2))
        self.assertEqual(bytes([0xFE, 0xFF]), CmapRegister(ctype=CType.INT16).pack_value(-2))
        self.assertEqual(bytes([0xFE, 0xFF, 0xFF, 0xFF]), CmapRegister(ctype=CType.INT32).pack_value(-2))
        self.assertEqual(bytes([0xCD, 0xCC, 0xCC, 0x3D]), CmapRegister(ctype=CType.FLOAT).pack_value(0.1))

    def test_pack_value_by_state(self):
        """Check pack_value_by_state() function works as expected
        """
        reg = CmapRegister(
            ctype=CType.UINT16,
            states=[
                CmapState(name="one", value=1),
                CmapState(name="sixteen", value=16)
            ]
        )

        self.assertEqual(bytes([0x01, 0x00]), reg.pack_value_by_state("one"))
        self.assertEqual(bytes([0x10, 0x00]), reg.pack_value_by_state("sixteen"))

    def test_pack_value_by_bitfields(self):
        """Check pack_value_by_state() function works as expected
        """
        reg = CmapRegister(
            ctype=CType.UINT8,
            bitfields=[
                CmapBitfield(
                    name="field_0_3",
                    position=0,
                    num_bits=4
                ),
                CmapBitfield(
                    name="field_4_7",
                    position=4,
                    num_bits=4
                ),
            ]
        )

        self.assertEqual(bytes([0x81]), reg.pack_value_by_bitfields({"field_0_3": 1, "field_4_7": 8}))


if __name__ == '__main__':
    unittest.main()
