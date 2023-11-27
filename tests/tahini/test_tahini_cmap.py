"""
Import unittest module to test InputToCMapSource
"""
import unittest
import warnings
from os import path
from cmlpytools.tahini.cmap_schema import FullRegmap as CmapFullRegmap
from cmlpytools.tahini.cmap_schema import Type as CmapType
from cmlpytools.tahini.cmap_schema import ArrayIndex as CmapArrayIndex
from cmlpytools.tahini.input_json_schema import (InputJsonParserError, InputJson, InputRegmap,
                                                 InputType, VisibilityOptions, InputEnum)
from cmlpytools.tahini.tahini_cmap import TahiniCmap, TahiniCmapError

PATH_TO_DATA = "./tests/tahini/data"

INPUTPATH = path.join(PATH_TO_DATA, "test_fullregmap_inputjsonexample.json")
INVALID_CMAP_PATH = path.join(PATH_TO_DATA, "test_cmapparser_tocmap.json")
CMAPPATH = path.join(PATH_TO_DATA, "test_fullregmap.json")
ENUM_PATH = path.join(PATH_TO_DATA, "test_tahini_cmap_enum.json")
EXTENDED_VERSION_INFO_PATH = path.join(PATH_TO_DATA, "test_extendedversion.info.json")


class TestToCMapSourceMethod(unittest.TestCase):
    """ Test class for the InputToCMapSource class
    """
    # pylint: disable=duplicate-code

    def test_convert_pass(self):
        """Test the conversion to cmapsource
        """
        data_obj = TahiniCmap.cmap_fullregmap_from_input_json_path(
            INPUTPATH, extended_version_info_path=EXTENDED_VERSION_INFO_PATH)
        data_cmap_str = CmapFullRegmap.load_json(CMAPPATH)
        self.assertEqual(data_obj, data_cmap_str, "The content of converted cmapsource file is not identical")

    def test_convert_fail_invalid_input_json(self):
        """Test if the conversion to cmapsource detects an invalid input json file
        """
        with self.assertRaises(InputJsonParserError):
            # The invalid input json will raise a deprecationwarning: RemovedInMarshmallow4Warning
            # which is caused by the verifications from InputJsonParserError and dataclass.
            # import warning method to ignore the warning.
            warnings.filterwarnings(action="ignore", category=DeprecationWarning)
            _ = TahiniCmap.cmap_regmap_from_input_json_path(INVALID_CMAP_PATH)
            warnings.filterwarnings(action="default", category=DeprecationWarning)

    def test_struct_children_inherit_access_params(self):
        """Check that the children of the FullRegmap correctly inherit access parameters.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=2,
                    type=InputType.STRUCT[0],
                    name="buz",
                    byte_size=8,
                    access=VisibilityOptions.PUBLIC,
                    hif_access=True,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="zoo",
                            byte_size=2,
                            byte_offset=0
                        ),
                        InputRegmap(
                            access=VisibilityOptions.PRIVATE,
                            hif_access=True,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="kah",
                            byte_size=2,
                            byte_offset=2
                        ),
                        InputRegmap(
                            access=VisibilityOptions.PUBLIC,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="ooz",
                            byte_size=2,
                            byte_offset=4
                        ),
                        InputRegmap(
                            hif_access=False,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="hak",
                            byte_size=2,
                            byte_offset=6
                        )
                    ]
                )
            ],
            enums=[]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("buz", cmap.children[0].name)

        self.assertEqual("zoo", cmap.children[0].struct.children[0].name)
        self.assertEqual(VisibilityOptions.PUBLIC, cmap.children[0].struct.children[0].access)
        self.assertEqual(True, cmap.children[0].struct.children[0].hif_access)

        self.assertEqual("kah", cmap.children[0].struct.children[1].name)
        self.assertEqual(VisibilityOptions.PRIVATE, cmap.children[0].struct.children[1].access)
        self.assertEqual(True, cmap.children[0].struct.children[1].hif_access)

        self.assertEqual("ooz", cmap.children[0].struct.children[2].name)
        self.assertEqual(VisibilityOptions.PUBLIC, cmap.children[0].struct.children[2].access)
        self.assertEqual(True, cmap.children[0].struct.children[2].hif_access)

        self.assertEqual("hak", cmap.children[0].struct.children[3].name)
        self.assertEqual(VisibilityOptions.PUBLIC, cmap.children[0].struct.children[3].access)
        self.assertEqual(False, cmap.children[0].struct.children[3].hif_access)
        self.assertEqual(None, cmap.children[0].struct.children[3].namespace)

    def test_struct_children_inherit_namespace(self):
        """Check that the children of the FullRegmap correctly inherit parent namespace.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    namespace="spaceman",
                    address=2,
                    type=InputType.STRUCT[0],
                    name="buz",
                    byte_size=8,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="foo",
                            byte_size=2,
                            byte_offset=0
                        ),
                        InputRegmap(
                            namespace="rocketman",
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            byte_size=2,
                            byte_offset=2
                        )
                    ]
                )
            ],
            enums=[]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("buz", cmap.children[0].name)
        self.assertEqual("spaceman", cmap.children[0].namespace)

        self.assertEqual("foo", cmap.children[0].struct.children[0].name)
        self.assertEqual(VisibilityOptions.PRIVATE, cmap.children[0].struct.children[0].access)
        self.assertEqual("spaceman", cmap.children[0].struct.children[0].namespace)

        self.assertEqual("bar", cmap.children[0].struct.children[1].name)
        self.assertEqual(VisibilityOptions.PRIVATE, cmap.children[0].struct.children[1].access)
        self.assertEqual("rocketman", cmap.children[0].struct.children[1].namespace)

    def test_regmap_children_are_sorted_by_address(self):
        """Check that the children of the FullRegmap are correctly sorted by address.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(address=0,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="foo",
                            byte_size=2),
                InputRegmap(address=4,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="zoo",
                            byte_size=2),
                InputRegmap(address=2,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            byte_size=2)
            ],
            enums=[]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("foo", cmap.children[0].name)
        self.assertEqual("bar", cmap.children[1].name)
        self.assertEqual("zoo", cmap.children[2].name)

    def test_register_states_are_sorted_by_value(self):
        """Check that register states are ordered by their value.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(address=0,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="foo",
                            byte_size=2,
                            value_enum="foo_values")
            ],
            enums=[
                InputEnum(name="foo_values", enumerators=[
                    InputEnum.InputEnumChild(name="B", value=2),
                    InputEnum.InputEnumChild(name="C", value=3),
                    InputEnum.InputEnumChild(name="A", value=1)
                ])
            ]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("a", cmap.children[0].register.states[0].name)
        self.assertEqual("b", cmap.children[0].register.states[1].name)
        self.assertEqual("c", cmap.children[0].register.states[2].name)

    def test_register_bitfields_are_sorted(self):
        """Check that bitfields and associated states are correctly ordered by their bit position or values.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(address=0,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="foo",
                            byte_size=2,
                            mask_enum="foo_masks")
            ],
            enums=[
                InputEnum(name="foo_masks", enumerators=[
                    InputEnum.InputEnumChild(name="B_MASK", value=0x02),
                    InputEnum.InputEnumChild(name="C_MASK", value=0xf0),
                    InputEnum.InputEnumChild(name="C_B", value=0x20),
                    InputEnum.InputEnumChild(name="C_C", value=0x30),
                    InputEnum.InputEnumChild(name="C_A", value=0x10),
                    InputEnum.InputEnumChild(name="A_MASK", value=0x01)
                ])
            ]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("a", cmap.children[0].register.bitfields[0].name)
        self.assertEqual("b", cmap.children[0].register.bitfields[1].name)
        self.assertEqual("c", cmap.children[0].register.bitfields[2].name)

        self.assertEqual("a", cmap.children[0].register.bitfields[2].states[0].name)
        self.assertEqual("b", cmap.children[0].register.bitfields[2].states[1].name)
        self.assertEqual("c", cmap.children[0].register.bitfields[2].states[2].name)

    def test_convert_array_enum(self):
        """Test if the conversion of array enum is correct
        """
        data = TahiniCmap.cmap_regmap_from_input_json_path(ENUM_PATH)
        data_aliases = data.children[0].repeat_for[0].aliases
        self.assertEqual(['rz', 'x', 'y'], data_aliases, "The name of enum is not correct")

    def test_convert_array_enum_is_case_insensitive(self):
        """Test if the conversion of array enum is not case sensitive
        """
        data = TahiniCmap.cmap_regmap_from_input_json_path(ENUM_PATH)
        data_aliases = data.children[1].repeat_for[0].aliases
        self.assertEqual(['rz', 'x', 'y'], data_aliases)

    def test_convert_enum_array_single_element(self):
        """Test that it is possible to declare a single register with the `array_enum` property.
        This feature is especially useful for the hbaf config:

            ```c
            // @regmap array_enum: "hbaf_dof"
            uint16_t rdelta_d; // Generate `rdelta_dz` in cmapsource
            ```
        """
        data = TahiniCmap.cmap_regmap_from_input_json_path(ENUM_PATH)
        data_aliases = data.children[2].repeat_for[0].aliases
        self.assertEqual(['z'], data_aliases)

    def test_convert_nested_array(self):
        """Check that nested arrays produce the expected index arrays
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.STRUCT[0],
                    name="foo",
                    byte_size=8,
                    array_enum="dofs",
                    array_count=2,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_SIGNED_SHORT[0],
                            name="bar",
                            byte_size=2,
                            byte_offset=0,
                            array_enum="wires",
                            array_count=4
                        )
                    ]
                )
            ],
            enums=[
                InputEnum(
                    name="dofs",
                    enumerators=[
                        InputEnum.InputEnumChild(name="X", value=0x00),
                        InputEnum.InputEnumChild(name="Y", value=0x01)
                    ]
                ),
                InputEnum(
                    name="wires",
                    enumerators=[
                        InputEnum.InputEnumChild(name="W0", value=0x00),
                        InputEnum.InputEnumChild(name="W1", value=0x01),
                        InputEnum.InputEnumChild(name="W2", value=0x02),
                        InputEnum.InputEnumChild(name="W3", value=0x03)
                    ]
                )
            ]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual(1, len(cmap.children[0].repeat_for),
                         "First nested element should have only 1 index.")
        self.assertEqual(2, len(cmap.children[0].struct.children[0].repeat_for),
                         "Second nested element should have 2 indexes.")
        self.assertEqual(CmapArrayIndex(count=2, aliases=["x", "y"], offset=8),
                         cmap.children[0].struct.children[0].repeat_for[0])
        self.assertEqual(CmapArrayIndex(count=4, aliases=["w0", "w1", "w2", "w3"], offset=2),
                         cmap.children[0].struct.children[0].repeat_for[1])

    def test_dw9787(self):
        """Test conversion of DW9787 input to cmap
        """
        _ = TahiniCmap.cmap_regmap_from_input_json_path('tests/tahini/data/dw9787.json')

    def test_convert_mask_enum_into_bitfields(self):
        """Check that mask enums can be converted into cmapsource
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(address=0,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            byte_size=2,
                            mask_enum="bar_states")
            ],
            enums=[
                InputEnum(
                    name="bar_states",
                    enumerators=[
                        InputEnum.InputEnumChild(name="FIELD_1_MASK", value=0x0f),
                        InputEnum.InputEnumChild(name="FIELD_1_VALUE_A", value=0x00),
                        InputEnum.InputEnumChild(name="FIELD_1_VALUE_B", value=0x01),
                        InputEnum.InputEnumChild(name="FIELD_2_MASK", value=0x30),
                        InputEnum.InputEnumChild(name="FIELD_2_VALUE_A", value=0x00),
                        InputEnum.InputEnumChild(name="FIELD_2_VALUE_B", value=0x10),
                        InputEnum.InputEnumChild(name="FIELD_2_VALUE_C", value=0x20),
                        InputEnum.InputEnumChild(name="FIELD_2_2_MASK", value=0x80),
                        InputEnum.InputEnumChild(name="FIELD_2_2_VALUE_A", value=0x00),
                        InputEnum.InputEnumChild(name="FIELD_2_2_VALUE_B", value=0x80)
                    ]
                )
            ]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual(1, len(cmap.children))
        self.assertEqual("bar", cmap.children[0].name)
        self.assertEqual(CmapType.REGISTER, cmap.children[0].type)
        self.assertEqual(3, len(cmap.children[0].register.bitfields))

        self.assertEqual("field_1", cmap.children[0].register.bitfields[0].name)
        self.assertEqual(2, len(cmap.children[0].register.bitfields[0].states))
        self.assertEqual("value_a", cmap.children[0].register.bitfields[0].states[0].name)
        self.assertEqual(0, cmap.children[0].register.bitfields[0].states[0].value)
        self.assertEqual("value_b", cmap.children[0].register.bitfields[0].states[1].name)
        self.assertEqual(1, cmap.children[0].register.bitfields[0].states[1].value)

        self.assertEqual("field_2", cmap.children[0].register.bitfields[1].name)
        self.assertEqual(3, len(cmap.children[0].register.bitfields[1].states))
        self.assertEqual("value_a", cmap.children[0].register.bitfields[1].states[0].name)
        self.assertEqual(0, cmap.children[0].register.bitfields[1].states[0].value)
        self.assertEqual("value_b", cmap.children[0].register.bitfields[1].states[1].name)
        self.assertEqual(1, cmap.children[0].register.bitfields[1].states[1].value)
        self.assertEqual("value_c", cmap.children[0].register.bitfields[1].states[2].name)
        self.assertEqual(2, cmap.children[0].register.bitfields[1].states[2].value)

        self.assertEqual("field_2_2", cmap.children[0].register.bitfields[2].name)
        self.assertEqual(2, len(cmap.children[0].register.bitfields[2].states))
        self.assertEqual("value_a", cmap.children[0].register.bitfields[2].states[0].name)
        self.assertEqual(0, cmap.children[0].register.bitfields[2].states[0].value)
        self.assertEqual("value_b", cmap.children[0].register.bitfields[2].states[1].name)
        self.assertEqual(1, cmap.children[0].register.bitfields[2].states[1].value)

    def test_convert_mask_enum_with_prefix(self):
        """Test if the conversion of a mask enum is correct and the prefix is correctly removed
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(address=0,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="foo",
                            byte_size=2,
                            mask_enum="bar")
            ],
            enums=[
                InputEnum(
                    name="bar",
                    enumerators=[
                        InputEnum.InputEnumChild(name="BAR_FIELD_1_MASK", value=0x0f),
                        InputEnum.InputEnumChild(name="BAR_FIELD_2_MASK", value=0xf0)
                    ]
                )
            ]
        )

        cmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual(2, len(cmap.children[0].register.bitfields))
        self.assertEqual("field_1", cmap.children[0].register.bitfields[0].name)
        self.assertEqual("field_2", cmap.children[0].register.bitfields[1].name)

    def test_inputs_with_visibility_none_are_skipped(self):
        """Check that registers containing the keyword "reserved" are not output to the cmapsource
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    access=VisibilityOptions.NONE,
                    address=0,
                    type=InputType.STRUCT[0],
                    name="foo",
                    byte_size=2,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            byte_size=2,
                            byte_offset=0
                        )
                    ]
                ),
                InputRegmap(
                    address=2,
                    type=InputType.STRUCT[0],
                    name="buz",
                    byte_size=2,
                    members=[
                        InputRegmap(
                            access=VisibilityOptions.NONE,
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="zoo",
                            byte_size=2,
                            byte_offset=0
                        )
                    ]
                )
            ],
            enums=[]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual(1, len(regmap.children))
        self.assertEqual("buz", regmap.children[0].name)
        self.assertEqual(0, len(regmap.children[0].struct.children))

    def test_use_cmap_name_instead_of_name(self):
        """Check that if "cmap_name" is defined, it is used to generate the cmap instead of the instance "name".
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.STRUCT[0],
                    name="foo",
                    byte_size=2,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            byte_size=2,
                            byte_offset=0
                        )
                    ]
                ),
                InputRegmap(
                    address=0,
                    type=InputType.STRUCT[0],
                    name="foo",
                    cmap_name="another_foo",
                    byte_size=2,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            cmap_name="another_bar",
                            byte_size=2,
                            byte_offset=0
                        )
                    ]
                )
            ],
            enums=[]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("another_foo", regmap.children[1].name)
        self.assertEqual("another_bar", regmap.children[1].struct.children[0].name)

    def test_cmap_must_use_lower_case(self):
        """Check that register names, aliases, states, and bitfields all use lower-case in cmap files.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.STRUCT[0],
                    name="FOO",
                    byte_size=2,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="BAR",
                            byte_size=2,
                            byte_offset=0,
                            array_count=1,
                            array_enum="DOF",
                            value_enum="WIRE"
                        )
                    ]
                ),
                InputRegmap(
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="ZOO",
                    byte_size=2,
                    address=0,
                    mask_enum="STATES"
                )
            ],
            enums=[
                InputEnum(
                    name="DOF",
                    enumerators=[InputEnum.InputEnumChild(name="DOF_X", value=0)]
                ),
                InputEnum(
                    name="WIRE",
                    enumerators=[InputEnum.InputEnumChild(name="WIRE0", value=0)]
                ),
                InputEnum(
                    name="STATES",
                    enumerators=[InputEnum.InputEnumChild(name="BIT0_MASK", value=0x01)]
                )
            ]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("foo", regmap.children[0].name)
        self.assertEqual("bar", regmap.children[0].struct.children[0].name)
        self.assertEqual("x", regmap.children[0].struct.children[0].repeat_for[0].aliases[0])
        self.assertEqual("wire0", regmap.children[0].struct.children[0].register.states[0].name)
        self.assertEqual("bit0", regmap.children[1].register.bitfields[0].name)

    def test_convert_value_enum_with_prefix(self):
        """Check that value_enum with prefix are converted correctly, and the prefix is correctly removed.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="foo",
                    byte_size=2,
                    value_enum="bar"
                )
            ],
            enums=[
                InputEnum(
                    name="bar",
                    enumerators=[
                        InputEnum.InputEnumChild(name="BAR_VALUE_A", value=0),
                        InputEnum.InputEnumChild(name="BAR_VALUE_B", value=1)
                    ]
                )
            ]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("value_a", regmap.children[0].register.states[0].name)
        self.assertEqual("value_b", regmap.children[0].register.states[1].name)

    def test_cref_are_resolved_correctly(self):
        """Check that if regmap input is defined with the keyword `cref` then it is replaced in the cmapsource file
        with the struct referenced by the field.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="foo_buf",
                    byte_size=2,
                    address=256,
                    array_count=10,
                    cref="foo"
                ),
                InputRegmap(
                    type=InputType.STRUCT[0],
                    name="foo",
                    byte_size=4,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            byte_size=2,
                            byte_offset=0
                        ),
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="zoo",
                            byte_size=2,
                            byte_offset=2
                        )
                    ]
                )
            ],
            enums=[]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual(1, len(regmap.children))
        self.assertEqual("foo", regmap.children[0].name)
        self.assertEqual(4, regmap.children[0].size)
        self.assertEqual(256, regmap.children[0].addr)
        self.assertEqual(2, len(regmap.children[0].struct.children))
        self.assertEqual("bar", regmap.children[0].struct.children[0].name)
        self.assertEqual("zoo", regmap.children[0].struct.children[1].name)

    def test_using_a_cref_struct_too_large_raises_error(self):
        """Check that if regmap input is defined with the keyword `cref` but the struct specified is too large
        to fit in the buffer, then an error is raised.
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="foo_buf",
                    byte_size=2,
                    byte_offset=0,
                    array_count=2,
                    cref="foo"
                ),
                InputRegmap(
                    type=InputType.STRUCT[0],
                    name="foo",
                    byte_size=4,
                    members=[
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="bar",
                            byte_size=2,
                            byte_offset=0
                        ),
                        InputRegmap(
                            type=InputType.CTYPE_UNSIGNED_SHORT[0],
                            name="zoo",
                            byte_size=2,
                            byte_offset=0
                        )
                    ]
                )
            ],
            enums=[]
        )

        with self.assertRaises(TahiniCmapError):
            _ = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

    def test_visibility_is_applied_correctly_to_states(self):
        """Check that visibility options are applied correctly to states
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="foo",
                    byte_size=2,
                    value_enum="bar",
                    access=VisibilityOptions.PUBLIC
                )
            ],
            enums=[
                InputEnum(
                    name="bar",
                    enumerators=[
                        InputEnum.InputEnumChild(name="BAR_VALUE1", value=0x01, access=VisibilityOptions.NONE),
                        InputEnum.InputEnumChild(name="BAR_VALUE2", value=0x02, access=VisibilityOptions.PUBLIC),
                        InputEnum.InputEnumChild(name="BAR_VALUE3", value=0x04, access=VisibilityOptions.PRIVATE),
                        InputEnum.InputEnumChild(name="BAR_VALUE4", value=0x08)
                    ]
                )
            ]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("value2", regmap.children[0].register.states[0].name)
        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.states[0].access)
        self.assertEqual("value3", regmap.children[0].register.states[1].name)
        self.assertEqual(VisibilityOptions.PRIVATE, regmap.children[0].register.states[1].access)
        self.assertEqual("value4", regmap.children[0].register.states[2].name)
        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.states[2].access)

    def test_visibility_is_applied_correctly_to_bitfields(self):
        """Check that visibility options are applied correctly to bitfields
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="foo",
                    byte_size=2,
                    mask_enum="bar",
                    access=VisibilityOptions.PUBLIC
                )
            ],
            enums=[
                InputEnum(
                    name="bar",
                    enumerators=[
                        InputEnum.InputEnumChild(name="FIELD1_MASK", value=0x0f, access=VisibilityOptions.NONE),
                        InputEnum.InputEnumChild(name="FIELD2_MASK", value=0xf0, access=VisibilityOptions.PRIVATE),
                        InputEnum.InputEnumChild(name="FIELD2_VALUE1", value=0x10, access=VisibilityOptions.NONE),
                        InputEnum.InputEnumChild(name="FIELD2_VALUE2", value=0x20, access=VisibilityOptions.PUBLIC),
                        InputEnum.InputEnumChild(name="FIELD2_VALUE3", value=0x30, access=VisibilityOptions.PRIVATE),
                        InputEnum.InputEnumChild(name="FIELD2_VALUE4", value=0x40),
                        InputEnum.InputEnumChild(name="FIELD3_MASK", value=0xf00, access=VisibilityOptions.PUBLIC),
                        InputEnum.InputEnumChild(name="FIELD3_VALUE1", value=0x100, access=VisibilityOptions.NONE),
                        InputEnum.InputEnumChild(name="FIELD3_VALUE2", value=0x200, access=VisibilityOptions.PUBLIC),
                        InputEnum.InputEnumChild(name="FIELD3_VALUE3", value=0x300, access=VisibilityOptions.PRIVATE),
                        InputEnum.InputEnumChild(name="FIELD3_VALUE4", value=0x400),
                        InputEnum.InputEnumChild(name="FIELD4_MASK", value=0xf000),
                        InputEnum.InputEnumChild(name="FIELD4_VALUE1", value=0x1000, access=VisibilityOptions.NONE),
                        InputEnum.InputEnumChild(name="FIELD4_VALUE2", value=0x2000, access=VisibilityOptions.PUBLIC),
                        InputEnum.InputEnumChild(name="FIELD4_VALUE3", value=0x3000, access=VisibilityOptions.PRIVATE),
                        InputEnum.InputEnumChild(name="FIELD4_VALUE4", value=0x4000),
                    ]
                )
            ]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual(VisibilityOptions.PRIVATE, regmap.children[0].register.bitfields[0].access)
        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.bitfields[0].states[0].access)
        self.assertEqual(VisibilityOptions.PRIVATE, regmap.children[0].register.bitfields[0].states[1].access)
        self.assertEqual(VisibilityOptions.PRIVATE, regmap.children[0].register.bitfields[0].states[2].access)

        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.bitfields[1].access)
        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.bitfields[1].states[0].access)
        self.assertEqual(VisibilityOptions.PRIVATE, regmap.children[0].register.bitfields[1].states[1].access)
        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.bitfields[1].states[2].access)

        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.bitfields[2].access)
        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.bitfields[2].states[0].access)
        self.assertEqual(VisibilityOptions.PRIVATE, regmap.children[0].register.bitfields[2].states[1].access)
        self.assertEqual(VisibilityOptions.PUBLIC, regmap.children[0].register.bitfields[2].states[2].access)

    def test_customer_alias_is_applied_correctly_to_states(self):
        """Check that the customer alias is applied correctly to states
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="foo",
                    byte_size=2,
                    value_enum="bar"
                )
            ],
            enums=[
                InputEnum(
                    name="bar",
                    enumerators=[
                        InputEnum.InputEnumChild(name="value1", value=0x02, customer_alias="value1_alias"),
                        InputEnum.InputEnumChild(name="value2", value=0x04)
                    ]
                )
            ]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("value1_alias", regmap.children[0].register.states[0].customer_alias)
        self.assertIsNone(regmap.children[0].register.states[1].customer_alias)

    def test_customer_alias_is_applied_correctly_to_bitfields(self):
        """Check that the customer alias is applied correctly to bitfields
        """
        input_regmap = InputJson(
            regmap=[
                InputRegmap(
                    address=0,
                    type=InputType.CTYPE_UNSIGNED_SHORT[0],
                    name="foo",
                    byte_size=2,
                    mask_enum="bar",
                    access=VisibilityOptions.PUBLIC
                )
            ],
            enums=[
                InputEnum(
                    name="bar",
                    enumerators=[
                        InputEnum.InputEnumChild(name="field1_mask", value=0x0f, customer_alias="field1_alias"),
                        InputEnum.InputEnumChild(name="field2_mask", value=0xf0),
                        InputEnum.InputEnumChild(name="field2_value1", value=0x10, customer_alias="value1_alias"),
                        InputEnum.InputEnumChild(name="field2_value2", value=0x20)
                    ]
                )
            ]
        )

        regmap = TahiniCmap.cmap_regmap_from_input_json(input_regmap)

        self.assertEqual("field1_alias", regmap.children[0].register.bitfields[0].customer_alias)
        self.assertIsNone(regmap.children[0].register.bitfields[1].customer_alias)
        self.assertEqual("value1_alias", regmap.children[0].register.bitfields[1].states[0].customer_alias)
        self.assertIsNone(regmap.children[0].register.bitfields[1].states[1].customer_alias)


    def test_overlapping_registers(self):
        """Check that overlapping registers are detected and error is raised"""
        overlapping_regmap = path.join(PATH_TO_DATA, "test_overlapping_regs_cmap.json")
        with self.assertRaises(TahiniCmapError):
            _ = TahiniCmap.cmap_fullregmap_from_input_json(overlapping_regmap, extended_version_info_path=EXTENDED_VERSION_INFO_PATH)

if __name__ == '__main__':
    unittest.main()
