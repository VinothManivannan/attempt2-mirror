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
from .version_schema import ExtendedVersionInfo


HEADER_TEMPLATE = \
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

VERSION_TEMPLATE = """
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
"""

def prepend_namespaces(register: CmapRegisterOrStruct, inst_name: str):
    """
    If the input register has a namespace property then prepend it to the string name

    Args:
        register (CmapRegisterOrStruct): Cmap register or struct to process
        inst_name (str): register, bitfield or state name
    """
    if register.namespace is not None:
        new_name = register.namespace.upper() + "_" + inst_name
    else:
        new_name = inst_name
    return new_name

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

        if register.repeat_for is None:
            # Output register address
            addr = register.addr
            if register.hif_access:
                # For registers with indirect access on CM8x4, we output the expected CPU address instead
                if addr < 0x6000:
                    addr = addr + 0x3e000
                else:
                    addr = addr + 0x40000000
            instance_name = prepend_namespaces(register, register.get_customer_name().upper())
            output.write(f"#define {instance_name:<50} {addr:>#10x}\n")
        else:
            for instance in register.get_instances():
                # Output register address
                addr = instance.addr
                if register.hif_access:
                    # For registers with indirect access on CM8x4, we output the expected CPU address instead
                    if addr < 0x6000:
                        addr = addr + 0x3e000
                    else:
                        addr = addr + 0x40000000
                instance_name = register.get_customer_name() + instance.get_legacy_suffix()
                instance_name = prepend_namespaces(register, instance_name)
                output.write(f"#define {instance_name.upper():<50} {addr:>#10x}\n")

        # Output register states
        if register.register.states:
            for state in register.register.states:
                if state.access is CmapVisibilityOptions.PUBLIC:
                    state_name = register.get_customer_name().upper() + "_" + state.get_customer_name().upper()
                    state_name = prepend_namespaces(register, state_name)
                    output.write(f"    #define {state_name:<50} {state.value:>#10x} /* State */\n")

        # Output register bitfields
        if register.register.bitfields:
            for bitfield in register.register.bitfields:
                if bitfield.access is CmapVisibilityOptions.PUBLIC:
                    bitfield_name = register.get_customer_name().upper() + "_" + bitfield.get_customer_name().upper()
                    bitfield_name = prepend_namespaces(register, bitfield_name)
                    output.write(
                        f"    #define {bitfield_name:<50} {bitfield.get_mask():>#10x} /* Bitfield */\n")

                # Output states associated to this bitfield
                if bitfield.states:
                    for state in bitfield.states:
                        if state.access is CmapVisibilityOptions.PUBLIC:
                            state_mask = state.value << bitfield.position
                            # Bitfield state name is prefixed with the Bitfield name for uniqueness
                            state_name = bitfield_name + "_" + state.get_customer_name().upper()
                            state_name = prepend_namespaces(register, state_name)
                            output.write(
                                f"        #define {state_name:<50} {state_mask:>#10x} /* Bitfield state */\n")

    @staticmethod
    def from_cmapsource_path(cmapsource_path: str, output_txt_path: str) -> None:
        """Create txt output file from cmapsource file path

        Args:
            cmapsource_path (str): Cmapsource file path to process
            output_txt_path (str): Output file path
        """

        cmapsource = CmapFullRegmap.load_json(cmapsource_path)

        with open(output_txt_path, 'w', encoding='utf-8') as output:
            GenerateApiCheader.from_cmapsource(cmapsource.regmap, output, os.path.basename(output_txt_path),
                                               cmapsource.version)

    @staticmethod
    def from_cmapsource(cmapsource: CmapRegmap, output: TextIOWrapper, filename: str,
                        version: ExtendedVersionInfo) -> None:
        """Create txt output file from cmapsource file path

        Args:
            cmapsource (CmapFullRegmap): Cmapsource object to be converted
            output (TextIOWrapper): Text IO handle to write the output to. It must already be opened.
            filename (str): Name of the file to be created
            version (ExtendedVersionInfo): firmware git tag and commit version information
        """
        year = datetime.date.today().year
        header_guard = filename.replace(".", "_").replace("-", "_").upper()
        header = HEADER_TEMPLATE.replace("%%YEAR%%", str(year)).replace("%%HEADER_GUARD%%", header_guard)
        footer = FOOTER_TEMPLATE.replace("%%HEADER_GUARD%%", header_guard)
        last_tag = version.git_versions[0].last_tag
        if version.uid is None:
            version_uid = 0
        else:
            version_uid = version.uid
            
        version_string = VERSION_TEMPLATE.replace("%%MAJOR_VERSION%%", str(last_tag.major))\
            .replace("%%MINOR_VERSION%%", str(last_tag.minor))\
            .replace("%%PATCH_VERSION%%", str(last_tag.patch))\
            .replace("%%MAJOR_SUBVERSION%%", str(last_tag.branch_id))\
            .replace("%%MINOR_SUBVERSION%%", str(last_tag.release_num))\
            .replace("%%UNIQUE_ID%%", str(version_uid)\
            .replace("%%BUILDCONFIG_ID%%", str(version.config_id))

        output.write(header)

        output.write(version_string)

        for register_or_struct in cmapsource.children:
            GenerateApiCheader._output_register_or_struct(register_or_struct, output)

        output.write(footer)
