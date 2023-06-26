"""Tests to check the conversion from cmapsource to legacy regmap
"""

import unittest
import sys
from os import path
from typing import Optional
import clr
from cmlpytools.tahini.tahini_cmap import TahiniCmap
from cmlpytools.tahini.tahini_generate_legacy_regmap import GenerateLegacyRegmap
from cmlpytools.tahini.legacy_regmap_schema import LegacyRegmap
from cmlpytools.tahini.cmap_schema import CType, State
from cmlpytools.tahini.input_json_schema import InputJson, InputEnum, InputRegmap, InputType

sys.path.append(path.dirname(path.realpath(__file__)))
clr.AddReference("SERVALib")

# pylint:disable = wrong-import-position, wrong-import-order
from Encryption_Module import JSON_Serialisation  # nopep8
# pylint:enable = wrong-import-position, wrong-import-order

VERSION_INFO_PATH = "./tests/tahini/data/test_version.info.json"
EXTENDED_VERSION_INFO_PATH = "./tests/tahini/data/test_extendedversion.info.json"
INPUT_JSON_PATH = "./tests/tahini/data/test_fullregmap_inputjsonexample.json"


class TestLegacyRegmap(unittest.TestCase):
    """Tests used to check that the legacy regmap generation works as expected
    """

    def setUp(self):
        """Run the legacy regmap converter and then decrypt the resulting file so it is possible to check
        the output using unittests.
        """
        cmap = TahiniCmap.cmap_fullregmap_from_input_json_path(input_json_path=INPUT_JSON_PATH,
                                                               extended_version_info_path=EXTENDED_VERSION_INFO_PATH)
        encrypted_regmap = GenerateLegacyRegmap.create_legacy_regmap(cmap=cmap)

        decrypted_regmap_json = JSON_Serialisation.Decrypt_JSON_string(
            encrypted_regmap)

        self.decrypted_regmap_obj = LegacyRegmap.from_json(
            decrypted_regmap_json)

        self.cmap_source_obj = TahiniCmap.cmap_fullregmap_from_input_json_path(
            INPUT_JSON_PATH,
            extended_version_info_path=EXTENDED_VERSION_INFO_PATH)

    def test_registers_address(self):
        """Verify register addresses match
        """

        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[0].Address,
            self.cmap_source_obj.regmap.children[0].addr)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[1].Address,
            self.cmap_source_obj.regmap.children[1].addr)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[2].Address,
            self.cmap_source_obj.regmap.children[2].addr)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[3].Address,
            self.cmap_source_obj.regmap.children[2].addr +
            CType.get_bit_size(
                self.cmap_source_obj.regmap.children[2].register.ctype) / 8)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[4].Address,
            self.cmap_source_obj.regmap.children[2].addr + 2 * CType.get_bit_size(
                self.cmap_source_obj.regmap.children[2].register.ctype) / 8)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[5].Address,
            self.cmap_source_obj.regmap.children[3].struct.children[0].addr)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[6].Address,
            self.cmap_source_obj.regmap.children[3].struct.children[1].addr)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[7].Address,
            self.cmap_source_obj.regmap.children[4].struct.children[0].addr)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[8].Address,
            self.cmap_source_obj.regmap.children[4].struct.children[0].addr +
            CType.get_bit_size(self.cmap_source_obj.regmap.children[4].struct.children[0].register.ctype) / 8)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[9].Address,
            self.cmap_source_obj.regmap.children[4].struct.children[0].addr +
            2 * CType.get_bit_size(self.cmap_source_obj.regmap.children[4].struct.children[0].register.ctype) / 8)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[10].Address,
            self.cmap_source_obj.regmap.children[4].struct.children[1].struct.children[0].addr)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[11].Address,
            self.cmap_source_obj.regmap.children[4].struct.children[1].struct.children[1].addr)

    def test_registers_names(self):
        """Verify register names match
        """

        self.assertEqual(self.decrypted_regmap_obj.Secure.Versions,
                         self.cmap_source_obj.version.git_versions)

        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[0].Name, self.cmap_source_obj.regmap.children[0].name.upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[1].Name, self.cmap_source_obj.regmap.children[1].name.upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[2].Name,
            self.cmap_source_obj.regmap.children[2].name.upper() + "0")
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[3].Name,
            self.cmap_source_obj.regmap.children[2].name.upper() + "1")
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[4].Name,
            self.cmap_source_obj.regmap.children[2].name.upper() + "2")
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[5].Name,
            self.cmap_source_obj.regmap.children[3].struct.children[0].name.upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[6].Name,
            self.cmap_source_obj.regmap.children[3].struct.children[1].name.upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[7].Name,
            self.cmap_source_obj.regmap.children[4].struct.children[0].name.upper() +
            self.cmap_source_obj.regmap.children[4].struct.children[0].repeat_for[0].aliases[0].upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[8].Name,
            self.cmap_source_obj.regmap.children[4].struct.children[0].name.upper() +
            self.cmap_source_obj.regmap.children[4].struct.children[0].repeat_for[0].aliases[1].upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[9].Name,
            self.cmap_source_obj.regmap.children[4].struct.children[0].name.upper() +
            self.cmap_source_obj.regmap.children[4].struct.children[0].repeat_for[0].aliases[2].upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[10].Name,
            self.cmap_source_obj.regmap.children[4].struct.children[1].struct.children[0].name.upper())
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[11].Name,
            self.cmap_source_obj.regmap.children[4].struct.children[1].struct.children[1].name.upper())

    def test_registers_type(self):
        """Verify register types match
        """
        def assert_types(legacy_type: str, ctype: CType) -> None:
            """Check that legacy type is correct
            """
            if ctype == CType.UINT8:
                self.assertEqual("byte", legacy_type)
            elif ctype == CType.INT8:
                self.assertEqual("sbyte", legacy_type)
            else:
                self.assertEqual(ctype.value, legacy_type)

        assert_types(
            self.decrypted_regmap_obj.Secure.Registers[0].Type, self.cmap_source_obj.regmap.children[0].register.ctype)
        assert_types(
            self.decrypted_regmap_obj.Secure.Registers[1].Type, self.cmap_source_obj.regmap.children[1].register.ctype)
        assert_types(
            self.decrypted_regmap_obj.Secure.Registers[2].Type, self.cmap_source_obj.regmap.children[2].register.ctype)
        assert_types(
            self.decrypted_regmap_obj.Secure.Registers[5].Type,
            self.cmap_source_obj.regmap.children[3].struct.children[0].register.ctype)
        assert_types(
            self.decrypted_regmap_obj.Secure.Registers[7].Type,
            self.cmap_source_obj.regmap.children[4].struct.children[0].register.ctype)
        assert_types(
            self.decrypted_regmap_obj.Secure.Registers[10].Type,
            self.cmap_source_obj.regmap.children[4].struct.children[1].struct.children[0].register.ctype)

    def test_registers_states(self):
        """Verify register states, where they exist, match
        """

        def assert_same_states(cmap_states: Optional[list[State]], legacy_states: Optional[dict[str, int]]) -> None:
            """Check that states found in a legacy file are the same as the ones from the cmapsource file.
            """
            if cmap_states is None:
                self.assertIsNone(legacy_states)
            else:
                self.assertEqual(len(cmap_states), len(legacy_states))
                for state in cmap_states:
                    self.assertIn(state.name.upper(), legacy_states)
                    self.assertEqual(state.value, legacy_states[state.name.upper()])

        assert_same_states(
            self.cmap_source_obj.regmap.children[0].register.states,
            self.decrypted_regmap_obj.Secure.Registers[0].States)

        assert_same_states(
            self.cmap_source_obj.regmap.children[1].register.states,
            self.decrypted_regmap_obj.Secure.Registers[1].States)

        assert_same_states(
            self.cmap_source_obj.regmap.children[1].register.states,
            self.decrypted_regmap_obj.Secure.Registers[1].States)

        assert_same_states(
            self.cmap_source_obj.regmap.children[1].register.states,
            self.decrypted_regmap_obj.Secure.Registers[1].States)

    def test_registers_flags(self):
        """Verify that register flags generated in the legacy regmap are correct
        """
        # Check register "note" which has flags "A" (bit 7) "B" (bit 6) ... "G" (bit 1)
        note_flags = self.decrypted_regmap_obj.Secure.Registers[16].Flags
        self.assertEqual(7, len(note_flags))
        self.assertIn("C", note_flags)
        self.assertEqual(5, note_flags["C"])

    def test_registers_access(self):
        """Verify register access match
        """
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[0].Access, self.cmap_source_obj.regmap.children[0].access)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[1].Access, self.cmap_source_obj.regmap.children[1].access)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[2].Access, self.cmap_source_obj.regmap.children[2].access)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[5].Access,
            self.cmap_source_obj.regmap.children[3].struct.children[0].access)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[7].Access,
            self.cmap_source_obj.regmap.children[4].struct.children[0].access)
        self.assertEqual(
            self.decrypted_regmap_obj.Secure.Registers[10].Access,
            self.cmap_source_obj.regmap.children[4].struct.children[1].struct.children[0].access)

    def test_registers_in_nested_arrays(self):
        """Check that cmapsource registers in nested arrays produce the correct legacy regmap output
        """
        input_json = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.STRUCT[0],
                    name="foo",
                    byte_size=8,
                    array_enum="fourwire_dof",
                    array_count=2,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_SIGNED_SHORT[0],
                            name="bar_d",
                            byte_size=2,
                            byte_offset=0,
                            array_count=4
                        )
                    ]
                )
            ],
            enums=[
                InputEnum(
                    name="fourwire_dof",
                    enumerators=[
                        InputEnum.InputEnumChild(name="X", value=0x00),
                        InputEnum.InputEnumChild(name="Y", value=0x01)
                    ]
                )
            ]
        )

        cmap = TahiniCmap.cmap_fullregmap_from_input_json(input_json=input_json,
                                                          extended_version_info_path=EXTENDED_VERSION_INFO_PATH)
        encrypted_regmap = GenerateLegacyRegmap.create_legacy_regmap(cmap=cmap)
        decrypted_regmap = LegacyRegmap.from_json(JSON_Serialisation.Decrypt_JSON_string(encrypted_regmap))

        self.assertEqual("BAR_DX_0", decrypted_regmap.Secure.Registers[0].Name)
        self.assertEqual(0, decrypted_regmap.Secure.Registers[0].Address)
        self.assertEqual("BAR_DX_1", decrypted_regmap.Secure.Registers[1].Name)
        self.assertEqual(2, decrypted_regmap.Secure.Registers[1].Address)
        self.assertEqual("BAR_DX_2", decrypted_regmap.Secure.Registers[2].Name)
        self.assertEqual(4, decrypted_regmap.Secure.Registers[2].Address)
        self.assertEqual("BAR_DX_3", decrypted_regmap.Secure.Registers[3].Name)
        self.assertEqual(6, decrypted_regmap.Secure.Registers[3].Address)
        self.assertEqual("BAR_DY_0", decrypted_regmap.Secure.Registers[4].Name)
        self.assertEqual(8, decrypted_regmap.Secure.Registers[4].Address)
        self.assertEqual("BAR_DY_1", decrypted_regmap.Secure.Registers[5].Name)
        self.assertEqual(10, decrypted_regmap.Secure.Registers[5].Address)
        self.assertEqual("BAR_DY_2", decrypted_regmap.Secure.Registers[6].Name)
        self.assertEqual(12, decrypted_regmap.Secure.Registers[6].Address)
        self.assertEqual("BAR_DY_3", decrypted_regmap.Secure.Registers[7].Name)
        self.assertEqual(14, decrypted_regmap.Secure.Registers[7].Address)
