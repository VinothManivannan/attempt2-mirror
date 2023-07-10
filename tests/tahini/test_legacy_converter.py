"""
Tests for the search function
"""
import unittest
from os import path
from cmlpytools.tahini import legacy_json_to_input_regmap, TahiniCmap, search, CmapType, InputJson

DIR_PATH = path.dirname(path.realpath(__file__))
PATH_TO_DATA = path.join(DIR_PATH, "legacy_jsons")


class TestLegacyConverter(unittest.TestCase):
    """Tests used to verify the legacy json to input regmap converter
    """

    def import_legacy_json(self, filename: str) -> InputJson:
        """Open a legacy json file from the samples folder, and convert into InputJson
        """
        return legacy_json_to_input_regmap(path.join(PATH_TO_DATA, filename))

    def test_export_legacy_to_json(self):
        """Check that the conversion from legacy to input regmap does not raise any exception.
        """
        input_json = self.import_legacy_json("test_example_legacy.json")
        _ = input_json.to_json()

    def test_convert_input_to_cmap(self):
        """Check that the input regmap produced from the legacy json can be converted
        into a cmapsource without raising any exception.
        """
        input_json = self.import_legacy_json("test_example_legacy.json")

        TahiniCmap.cmap_regmap_from_input_json(input_json)

    def test_reg_byte_size_is_correct(self):
        """Check that the register size is calculated correctly
        """
        input_json = self.import_legacy_json("test_example_legacy.json")
        self.assertEqual(4, input_json.regmap[0].members[0].byte_size,
                         "Size of register PWM_FREQUENCY is not correct")
        self.assertEqual(1, input_json.regmap[0].members[1].byte_size,
                         "Size of register reserved_cml_params is not correct")
        self.assertEqual(2, input_json.regmap[0].members[2].members[0].members[0].members[0].members[0].byte_size,
                         "Size of register TEMPEST_OFFSET is not correct")

    def test_byte_offset_is_correct(self):
        """Check that the byte offset is calculated correctly.
        """
        input_json = self.import_legacy_json("test_example_legacy.json")
        self.assertEqual(None, input_json.regmap[0].byte_offset,
                         "Parent should not have a byte offset")
        self.assertEqual(0, input_json.regmap[0].members[0].byte_offset,
                         "Offset of PWM_FREQUENCY is not correct")
        self.assertEqual(4, input_json.regmap[0].members[1].byte_offset,
                         "Offset of reserved_cml_params is not correct")
        self.assertEqual(32, input_json.regmap[0].members[2].byte_offset,
                         "Offset of ssl_params is not correct")
        self.assertEqual(0, input_json.regmap[0].members[2].members[0].byte_offset,
                         "Offset of fourwire_persist is not correct")

    def test_struct_size_is_correct(self):
        """Check that the size of the struct is calculated correctly
        """
        input_json = self.import_legacy_json("test_example_legacy.json")
        self.assertEqual(4, input_json.regmap[0].members[2].members[0].members[0].members[0].byte_size,
                         "Size of struct tempest_params is not correct")
        self.assertEqual(38, input_json.regmap[0].members[2].members[0].members[0].byte_size,
                         "Size of struct fourwire_persist_public is not correct")

    def test_flag_are_converted_into_bitfields(self):
        """Check that flags are converted into bitfields as expected
        """
        input_json = self.import_legacy_json("test_example_legacy.json")
        cmap = TahiniCmap.cmap_regmap_from_input_json(input_json)

        match = search("CTRL_FEATURES", CmapType.REGISTER, cmap)
        self.assertIsNotNone(match)

        ctrl_features = match.result

        self.assertIsNotNone(ctrl_features.register)
        self.assertIsNotNone(ctrl_features.register.bitfields)
        self.assertEqual(12, len(ctrl_features.register.bitfields))
        self.assertEqual(0, ctrl_features.register.bitfields[0].position)
        self.assertEqual(1, ctrl_features.register.bitfields[0].num_bits)
        self.assertEqual("auto_limiting", ctrl_features.register.bitfields[0].name)
        self.assertEqual(1, ctrl_features.register.bitfields[1].position)
        self.assertEqual(1, ctrl_features.register.bitfields[1].num_bits)
        self.assertEqual("auto_centring", ctrl_features.register.bitfields[1].name)

    def test_states_are_converted(self):
        """Check that register states
        """
        input_json = self.import_legacy_json("test_example_legacy.json")
        cmap = TahiniCmap.cmap_regmap_from_input_json(input_json)

        match = search("CENTRING_MODE", CmapType.REGISTER, cmap)
        self.assertIsNotNone(match)

        centring_mode = match.result

        self.assertIsNotNone(centring_mode.register)
        self.assertIsNotNone(centring_mode.register.states)
        self.assertEqual(3, len(centring_mode.register.states))
        self.assertEqual("power_centre", centring_mode.register.states[0].name)
        self.assertEqual(0, centring_mode.register.states[0].value)
        self.assertEqual("abs_resistance_centre", centring_mode.register.states[1].name)
        self.assertEqual(1, centring_mode.register.states[1].value)

    def test_simple_structs_and_regs(self):
        """Example with simple struct and regs 
        """
        input_json = self.import_legacy_json("bias_model.caef.json")

        _ = TahiniCmap.cmap_regmap_from_input_json(input_json)

        self.assertEqual("btm_params", input_json.regmap[0].name)
        self.assertEqual("btm_base", input_json.regmap[0].members[0].name)

    def test_enums_for_flags_and_arrays(self):
        """Example with many enums for flags and arrays
        """
        input_json = self.import_legacy_json("sma_control_common.caef.json")

        _ = TahiniCmap.cmap_regmap_from_input_json(input_json)

        self.assertEqual("Ctrl8WsParamsDof", input_json.enums[0].name)
        self.assertEqual("CtrlFeatures8WsFlags", input_json.enums[1].name)

    def test_host_access_and_reserved_regs(self):
        """Example with many enums for flags and arrays
        """
        input_json = self.import_legacy_json("input_common.caef.json")

        _ = TahiniCmap.cmap_regmap_from_input_json(input_json)

        self.assertEqual(False, input_json.regmap[0].hif_access)
        self.assertEqual(True, input_json.regmap[0].members[0].hif_access)
        self.assertEqual("input_ctrl_pad", input_json.regmap[0].members[1].name)
        self.assertEqual("none", input_json.regmap[0].members[1].access)

    def test_briefs_are_populated_for_flags_and_states(self):
        """Example with many enums for flags and arrays
        """
        input_json = self.import_legacy_json("sma_control_common.caef.json")

        _ = TahiniCmap.cmap_regmap_from_input_json(input_json)

        self.assertEqual("Wire 0 is enabled", input_json.enums[5].enumerators[0].brief)
        self.assertEqual("Servo is off, actuator is idle", input_json.enums[32].enumerators[0].brief)

    def test_public_private_is_populated(self):
        """Example to check that private and public registers are marked as expected
        """
        input_json = self.import_legacy_json("temperature_estimation_model.caef.json")

        _ = TahiniCmap.cmap_regmap_from_input_json(input_json)

        self.assertEqual("public", input_json.regmap[0].members[0].access)
        self.assertEqual(None, input_json.regmap[0].members[1].access)
        self.assertEqual("private", input_json.regmap[1].members[2].access)
