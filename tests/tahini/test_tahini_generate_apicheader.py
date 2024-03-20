"""
Import unittest module to test GenerateTxt
"""
import unittest
from io import StringIO
import datetime
from cmlpytools.tahini.tahini_generate_api_cheader import GenerateApiCheader
from cmlpytools.tahini.cmap_schema import CType as CmapCtype
from cmlpytools.tahini.cmap_schema import Register as CmapRegister
from cmlpytools.tahini.cmap_schema import RegisterOrStruct as CmapRegisterOrStruct
from cmlpytools.tahini.cmap_schema import Regmap as CmapRegmap
from cmlpytools.tahini.cmap_schema import Struct as CmapStruct
from cmlpytools.tahini.cmap_schema import Type as CmapType
from cmlpytools.tahini.cmap_schema import VisibilityOptions as CmapVisibilityOptions
from cmlpytools.tahini.cmap_schema import Bitfield as CmapBitfield
from cmlpytools.tahini.cmap_schema import State as CmapState
from cmlpytools.tahini.cmap_schema import ArrayIndex as CmapArrayIndex
from cmlpytools.tahini.version_schema import ExtendedVersionInfo
from cmlpytools.tahini.version_schema import GitVersion
from cmlpytools.tahini.version_schema import LastTag

# pylint: disable=duplicate-code


class TestGenerateApiCHeader(unittest.TestCase):
    """ Test class for the GenerateTxt class
    """

    _EXPECTED_HEADER = \
        """/***************************************************************************************************
 * @brief CML CM8x4 register definitions.
 * @copyright Copyright (C) %%YEAR%% Cambridge Mechatronics Ltd. All rights reserved.
 * @par Disclaimer
 * This software is supplied by Cambridge Mechatronics Ltd. (CML) and is only intended for use with
 * CML products. No other uses are authorised. This software is owned by Cambridge Mechatronics
 * Ltd. and is protected under all applicable laws, including copyright laws.
 **************************************************************************************************/
 
/***************************************************************************************************
 * WARNING! THIS FILE IS AUTOGENERATED DO NOT EDIT MANUALY CHANGES MAY BE LOST!
 **************************************************************************************************/

#ifndef API_HEADER_H
#define API_HEADER_H

#ifdef __cplusplus
extern "C" {
#endif

""".replace("%%YEAR%%", str(datetime.date.today().year))

    _EXPECTED_FOOTER = """
#ifdef __cplusplus
}
#endif

#endif /* API_HEADER_H */
"""

    _GITVERSIONS = GitVersion(commit_id="abcd1234", last_tag=LastTag(major="1", minor="3", patch="2", branch_id="6789",
                                                                    release_num="1"))

    _VERSION = ExtendedVersionInfo(device_type="Don't Care", config_name="Don't Care", config_id="11",
                                   git_versions=[_GITVERSIONS])

    _EXPECTED_VERSION = """
/**************************************************************************************************
 * Firmware Version Information 
 *************************************************************************************************/
#define CML_FW_VERSION_MAJOR %%MAJOR_VERSION%%
#define CML_FW_VERSION_MINOR %%MINOR_VERSION%%
#define CML_FW_VERSION_PATCH %%PATCH_VERSION%%
#define CML_FW_SUBVERSION_MAJOR %%MAJOR_SUBVERSION%%
#define CML_FW_SUBVERSION_MINOR %%MINOR_SUBVERSION%%
#define CML_FW_UNIQUEID 0x%%UNIQUE_ID%%
#define CML_FW_BUILDCONFIGID %%BUILDCONFIG_ID%%

/**************************************************************************************************
 * Firmware Version Information 
 *************************************************************************************************/
""".replace("%%MAJOR_VERSION%%", str(_GITVERSIONS.last_tag.major))\
    .replace("%%MINOR_VERSION%%", str(_GITVERSIONS.last_tag.minor))\
    .replace("%%PATCH_VERSION%%", str(_GITVERSIONS.last_tag.patch))\
    .replace("%%MAJOR_SUBVERSION%%", str(_GITVERSIONS.last_tag.branch_id))\
    .replace("%%MINOR_SUBVERSION%%", str(_GITVERSIONS.last_tag.release_num))\
    .replace("%%UNIQUE_ID%%", str(_VERSION.git_versions[0].commit_id))\
    .replace("%%BUILDCONFIG_ID%%", str(_VERSION.config_id))

    def run_test(self, cmapsource: CmapRegmap, expected_body: str) -> None:
        """Run test to compare a cmapsource with expected body

        Args:
            cmapsource (CmapRegmap): Cmapsource object to be tested
            expected_body (str): Body of expected result
        """
        output = StringIO()
        GenerateApiCheader.from_cmapsource(cmapsource, output, "api_header.h", TestGenerateApiCHeader._VERSION)

        output.seek(0)
        self.compare_outputs(expected_body, output)

    def compare_outputs(self, expected_body: str, output: StringIO) -> None:
        """Compare 2 files and provide detailed information about the differences

        Args:
            expected_body (StringIO): Buffer or string containing expected output, without header or footer
            output (StringIO): Buffer or string containing actual output
        """
        lines = output.readlines()
        expected_lines = TestGenerateApiCHeader._EXPECTED_HEADER.splitlines()
        expected_lines.extend(TestGenerateApiCHeader._EXPECTED_VERSION.splitlines())
        expected_lines.extend(expected_body.splitlines())
        expected_lines.extend(TestGenerateApiCHeader._EXPECTED_FOOTER.splitlines())

        for line_num in range(min(len(expected_lines), len(lines))):
            self.assertEqual(expected_lines[line_num], lines[line_num].strip("\r\n"),
                             f"The comparison failed at line {line_num+1}.")

        self.assertEqual(len(expected_lines), len(lines), "The number of lines is not the same.")

    def test_register_simple(self):
        """Test that we can output a single register
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha",
                    type=CmapType.REGISTER,
                    addr=256,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define ALPHA                                                   0x100
"""
        self.run_test(cmapsource, expected_body)

    def test_register_with_hif_access(self):
        """Test that registers with hif access have the correct address
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha",
                    type=CmapType.REGISTER,
                    addr=0x24fc,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16
                    ),
                    access=CmapVisibilityOptions.PUBLIC,
                    hif_access=True
                ),
                CmapRegisterOrStruct(
                    name="beta",
                    type=CmapType.REGISTER,
                    addr=0x6b14,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16
                    ),
                    access=CmapVisibilityOptions.PUBLIC,
                    hif_access=True
                )
            ]
        )

        expected_body = """\
#define ALPHA                                                 0x404fc
#define BETA                                               0x40006b14
"""
        self.run_test(cmapsource, expected_body)

    def test_register_with_customer_alias(self):
        """Test that we can output a single register
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha",
                    type=CmapType.REGISTER,
                    addr=256,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16
                    ),
                    access=CmapVisibilityOptions.PUBLIC,
                    customer_alias="beta"
                )
            ]
        )

        expected_body = """\
#define BETA                                                    0x100
"""
        self.run_test(cmapsource, expected_body)

    def test_private_register_is_not_output(self):
        """Test that private registers are not included in the output
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha",
                    type=CmapType.REGISTER,
                    addr=256,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16
                    ),
                    access=CmapVisibilityOptions.PRIVATE
                )
            ]
        )

        expected_body = """\
"""
        self.run_test(cmapsource, expected_body)

    def test_register_nested_in_private_struct(self):
        """Test we can output a public register nested in a private struct
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha",
                    type=CmapType.STRUCT,
                    addr=512,
                    size=2,
                    struct=CmapStruct(
                        children=[
                            CmapRegisterOrStruct(
                                name="beta",
                                type=CmapType.REGISTER,
                                addr=512,
                                size=2,
                                register=CmapRegister(
                                    ctype=CmapCtype.UINT16,
                                ),
                                access=CmapVisibilityOptions.PUBLIC
                            )
                        ]
                    ),
                    access=CmapVisibilityOptions.PRIVATE
                )
            ]
        )

        expected_body = """\
#define BETA                                                    0x200
"""

        self.run_test(cmapsource, expected_body)
        
    def test_repeated_register(self):
        """Test we can output a public register that is repeated
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="beta",
                    type=CmapType.REGISTER,
                    addr=512,
                    size=1,
                    repeat_for=[
                        CmapArrayIndex(
                            count=4,
                            offset=1
                        )
                    ],
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16,
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define BETA_0                                                  0x200
#define BETA_1                                                  0x201
#define BETA_2                                                  0x202
#define BETA_3                                                  0x203
"""

        self.run_test(cmapsource, expected_body)
        
    def test_repeated_register_aliased(self):
        """Test we can output a public register that is repeated and aliased
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="beta",
                    type=CmapType.REGISTER,
                    addr=512,
                    size=1,
                    repeat_for=[
                        CmapArrayIndex(
                            count=3,
                            offset=1,
                            aliases=["x", "y", "z"]
                        )
                    ],
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16,
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define BETA_X                                                  0x200
#define BETA_Y                                                  0x201
#define BETA_Z                                                  0x202
"""

        self.run_test(cmapsource, expected_body)

    def test_state_in_register(self):
        """Test we can output a state nested in a register
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha_register",
                    type=CmapType.REGISTER,
                    addr=256,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16,
                        states=[
                            CmapState(
                                name="beta_state",
                                value=0x123,
                                access=CmapVisibilityOptions.PUBLIC
                            )
                        ]
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define ALPHA_REGISTER                                          0x100
    #define ALPHA_REGISTER_BETA_STATE                               0x123 /* State */
"""

        self.run_test(cmapsource, expected_body)

    def test_state_in_bitfield_in_register(self):
        """Test we can output a state nested in a bitfield nested in a register
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha_register",
                    type=CmapType.REGISTER,
                    addr=256,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16,
                        bitfields=[
                            CmapBitfield(
                                name="beta_bitfield",
                                num_bits=4,
                                position=4,
                                access=CmapVisibilityOptions.PUBLIC,
                                states=[
                                    CmapState(
                                        name="gamma_state",
                                        value=1,
                                        access=CmapVisibilityOptions.PUBLIC
                                    ),
                                    CmapState(
                                        name="delta_state",
                                        value=2,
                                        access=CmapVisibilityOptions.PUBLIC
                                    )
                                ]
                            )
                        ]
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define ALPHA_REGISTER                                          0x100
    #define ALPHA_REGISTER_BETA_BITFIELD                             0xf0 /* Bitfield */
        #define ALPHA_REGISTER_BETA_BITFIELD_GAMMA_STATE                 0x10 /* Bitfield state */
        #define ALPHA_REGISTER_BETA_BITFIELD_DELTA_STATE                 0x20 /* Bitfield state */
"""

        self.run_test(cmapsource, expected_body)

    def test_state_with_customer_alias(self):
        """Test customer aliases are used as expected when outputing states
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha_register",
                    type=CmapType.REGISTER,
                    addr=256,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16,
                        states=[
                            CmapState(
                                name="beta_state",
                                value=0x123,
                                customer_alias="alias_beta_state",
                                access=CmapVisibilityOptions.PUBLIC
                            )
                        ]
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define ALPHA_REGISTER                                          0x100
    #define ALPHA_REGISTER_ALIAS_BETA_STATE                         0x123 /* State */
"""

        self.run_test(cmapsource, expected_body)

    def test_bitfield_with_customer_alias(self):
        """Test customer aliases are used as expected when outputing bitfields
        """
        cmapsource = CmapRegmap(
            children=[
                CmapRegisterOrStruct(
                    name="alpha_register",
                    type=CmapType.REGISTER,
                    addr=256,
                    size=2,
                    register=CmapRegister(
                        ctype=CmapCtype.UINT16,
                        bitfields=[
                            CmapBitfield(
                                name="beta_bitfield",
                                customer_alias="beta_bitfield_alias",
                                num_bits=4,
                                position=4,
                                access=CmapVisibilityOptions.PUBLIC,
                                states=[
                                    CmapState(
                                        name="gamma_state",
                                        value=1,
                                        customer_alias="gamma_state_alias",
                                        access=CmapVisibilityOptions.PUBLIC
                                    )
                                ]
                            )
                        ]
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define ALPHA_REGISTER                                          0x100
    #define ALPHA_REGISTER_BETA_BITFIELD_ALIAS                       0xf0 /* Bitfield */
        #define ALPHA_REGISTER_BETA_BITFIELD_ALIAS_GAMMA_STATE_ALIAS       0x10 /* Bitfield state */
"""

        self.run_test(cmapsource, expected_body)
