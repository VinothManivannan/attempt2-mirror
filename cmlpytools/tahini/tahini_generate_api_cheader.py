"""Generate C header files used in customer api code
"""
from io import TextIOWrapper
import datetime
import os
from .cmap_schema import FullRegmap as CmapFullRegmap
from .cmap_schema import Regmap as CmapRegmap
from .cmap_schema import Type as CmapType
from .cmap_schema import RegisterOrStruct as CmapRegisterOrStruct
from .cmap_schema import VisibilityOptions as CmapVisibilityOptions


HEADER_TEMPLATE = \
    """/***************************************************************************************************
 * @brief CML CM8x4 register definitions.
 * @copyright Copyright (C) %%YEAR%% Cambridge Mechatronics Ltd. All rights reserved.
 * @par Disclaimer
 * This software is supplied by Cambridge Mechatronics Ltd. (CML) and is only intended for use with
 * CML products. No other uses are authorised. This software is owned by Cambridge Mechatronics
 * Ltd. and is protected under all applicable laws, including copyright laws.
 **************************************************************************************************/

#ifndef %%HEADER_GUARD%%
#define %%HEADER_GUARD%%

#ifdef __cplusplus
extern "C" {
#endif

"""

FOOTER_TEMPLATE = """
#ifdef __cplusplus
}
#endif

#endif /* %%HEADER_GUARD%% */
"""


class GenerateApiCheader():
    """Class for generating C header files used in customer Api code
    """

    @staticmethod
    def _output_register_or_struct(register_or_struct: CmapRegisterOrStruct, output: TextIOWrapper) -> None:
        """ Generate c header content for a register or struct object
        """
        if register_or_struct.type is CmapType.REGISTER:
            GenerateApiCheader._output_register(register_or_struct, output)
        elif register_or_struct.type is CmapType.STRUCT:
            for child in register_or_struct.struct.children:
                GenerateApiCheader._output_register_or_struct(child, output)

    @staticmethod
    def _output_register(register: CmapRegisterOrStruct, output: TextIOWrapper) -> None:
        """ Generate c header content for a register object
        """
        if register.access is not CmapVisibilityOptions.PUBLIC:
            return

        # Output register address
        addr = register.addr
        if register.hif_access:
            # For registers with indirect access on CM8x4, we output the expected CPU address instead
            if addr < 0x6000:
                addr = addr + 0x3e000
            else:
                addr = addr + 0x40000000
        output.write(f"#define {register.get_customer_name().upper():<30} {addr:>#10x}\n")

        # Output register states
        if register.register.states:
            for state in register.register.states:
                output.write(f"    #define {state.get_customer_name().upper():<30} {state.value:>#10x} /* State */\n")

        # Output register bitfields
        if register.register.bitfields:
            for bitfield in register.register.bitfields:
                bitfield_name = bitfield.get_customer_name().upper()
                output.write(
                    f"    #define {bitfield_name:<30} {bitfield.get_mask():>#10x} /* Bitfield */\n")

                # Output states associated to this bitfield
                if bitfield.states:
                    for state in bitfield.states:
                        state_mask = state.value << bitfield.position
                        state_name = state.get_customer_name().upper()
                        output.write(
                            f"        #define {state_name:<30} {state_mask:>#10x} /* Bitfield state */\n")

    @staticmethod
    def from_cmapsource_path(cmapsource_path: str, output_txt_path: str) -> None:
        """Create txt output file from cmapsource file path

        Args:
            cmapsource_path (str): Cmapsource file path to process
            output_txt_path (str): Output file path
        """

        cmapsource = CmapFullRegmap.load_json(cmapsource_path)

        with open(output_txt_path, 'w', encoding='utf-8') as output:
            GenerateApiCheader.from_cmapsource(cmapsource.regmap, output, os.path.basename(output_txt_path))

    @staticmethod
    def from_cmapsource(cmapsource: CmapRegmap, output: TextIOWrapper, filename: str) -> None:
        """Create txt output file from cmapsource file path

        Args:
            cmapsource (CmapFullRegmap): Cmapsource object to be converted
            output (TextIOWrapper): Text IO handle to write the output to. It must already be opened.
            filename (str): Name of the file to be created
        """
        year = datetime.date.today().year
        header_guard = filename.replace(".", "_").replace("-", "_").upper()
        header = HEADER_TEMPLATE.replace("%%YEAR%%", str(year)).replace("%%HEADER_GUARD%%", header_guard)
        footer = FOOTER_TEMPLATE.replace("%%HEADER_GUARD%%", header_guard)

        output.write(header)

        for register_or_struct in cmapsource.children:
            GenerateApiCheader._output_register_or_struct(register_or_struct, output)

        output.write(footer)