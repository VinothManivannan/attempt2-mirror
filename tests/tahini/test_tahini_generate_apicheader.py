"""
Import unittest module to test GenerateTxt
"""
import unittest
from io import StringIO
import datetime
from cmlpytools.tahini.tahini_generate_api_cheader import GenerateApiCheader
from cmlpytools.tahini.cmap_schema import ArrayIndex as CmapArrayIndex
from cmlpytools.tahini.cmap_schema import CType as CmapCtype
from cmlpytools.tahini.cmap_schema import Register as CmapRegister
from cmlpytools.tahini.cmap_schema import RegisterOrStruct as CmapRegisterOrStruct
from cmlpytools.tahini.cmap_schema import Regmap as CmapRegmap
from cmlpytools.tahini.cmap_schema import Struct as CmapStruct
from cmlpytools.tahini.cmap_schema import Type as CmapType
from cmlpytools.tahini.cmap_schema import VisibilityOptions as CmapVisibilityOptions
from cmlpytools.tahini.cmap_schema import Bitfield as CmapBitfield
from cmlpytools.tahini.cmap_schema import State as CmapState


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

    def run_test(self, cmapsource: CmapRegmap, expected_body: str) -> None:
        """Run test to compare a cmapsource with expected body

        Args:
            cmapsource (CmapRegmap): Cmapsource object to be tested
            expected_body (str): Body of expected result
        """
        output = StringIO()
        GenerateApiCheader.from_cmapsource(cmapsource, output, "api_header.h")

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
        expected_lines.extend(expected_body.splitlines())
        expected_lines.extend(TestGenerateApiCHeader._EXPECTED_FOOTER.splitlines())

        for line_num in range(min(len(expected_lines), len(lines))):
            self.assertEqual(expected_lines[line_num], lines[line_num].strip("\r\n"),
                             f"The comparison failed at line {line_num+1}.")

        self.assertEqual(len(expected_lines), len(lines), "The number of lines is not the same.")

    def test_simple_register(self):
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
#define ALPHA                               0x100
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
#define BETA                                0x200
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
                                value=0x123
                            )
                        ]
                    ),
                    access=CmapVisibilityOptions.PUBLIC
                )
            ]
        )

        expected_body = """\
#define ALPHA_REGISTER                      0x100
    #define BETA_STATE                          0x123 /* State */
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
                                states=[
                                    CmapState(
                                        name="gamma_state",
                                        value=1
                                    ),
                                    CmapState(
                                        name="delta_state",
                                        value=2
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
#define ALPHA_REGISTER                      0x100
    #define BETA_BITFIELD                        0xf0 /* Bitfield */
        #define GAMMA_STATE                          0x10 /* Bitfield state */
        #define DELTA_STATE                          0x20 /* Bitfield state */
"""

        self.run_test(cmapsource, expected_body)
