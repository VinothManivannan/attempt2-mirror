"""Generate .regmap output
    """
import re
import json
import sys
from os import path
from typing import Optional
import clr
from tahini.legacy_regmap_schema import LegacyRegmap, LegacyRegmapRegister, \
    HostAccessOptions, DeviceInformation, DataToEncrypt
from tahini.cmap_schema import FullRegmap, Type, CType, RegisterOrStruct

sys.path.append(path.dirname(path.realpath(__file__)))
clr.AddReference("SERVALib")

# pylint:disable = wrong-import-position, wrong-import-order
from Encryption_Module import JSON_Serialisation  # nopep8
# pylint:enable = wrong-import-position, wrong-import-order

INPUTPATH = "../tests/data/test_fullregmap_inputjsonexample.json"

VERSION_TAG_REGEX_G = r"((?P<major>[0-9]+)(\.)(?P<minor>[0-9]+)(\.)(?P<patch>[0-9]+))"


class GenerateLegacyRegmap():
    """Class for generating Legacy Regmap
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def create_legacy_regmap(cmap_file: Optional[str] = None, cmap: Optional[FullRegmap] = None) -> str:
        """Create encrypted legacy regmap output from from either a cmapsource file or an existing
        cmapsource FullRegmap instance.

        Args:
            cmap_file (str, optional): Path to the cmapsource file
            cmap (FullRegmap, optional): A FullRegmap instance

        Returns:
            str: Legacy regmap file as string
        """
        assert cmap_file is not None or cmap is not None,\
            "Error: This function must be called with either cmap_file or cmap specified as argument"

        if cmap_file is not None:
            cmap = FullRegmap.load_json(cmap_file)

        full_version = cmap.version

        project_name = full_version.project

        device_information = GenerateLegacyRegmap.__get_device_info(
            project_name)

        name = device_information["Name"]
        addr_size = device_information["Addr_Size"]
        reg_size = device_information["Reg_Size"]
        addr_little_end = device_information["Addr_Little_End"]
        data_little_end = device_information["Data_Little_End"]

        fw_versions = name + "_" + (re.search(
            VERSION_TAG_REGEX_G, full_version.version).group(0)).replace(".", "_")

        versions = {str(int(full_version.uid, 16)): fw_versions}

        timestamp = full_version.timestamp
        build_config = full_version.config_name
        build_config_id = str(full_version.config_id)

        gitversions_to_encrypt = full_version.git_versions
        registers_to_encrypt = GenerateLegacyRegmap.__get_registers_list(
            cmap)

        data_to_encrypt = DataToEncrypt(
            gitversions_to_encrypt, registers_to_encrypt)

        legacy_regmap_obj = LegacyRegmap(name.upper(),
                                         addr_size,
                                         reg_size,
                                         addr_little_end,
                                         data_little_end,
                                         versions,
                                         timestamp,
                                         build_config,
                                         build_config_id,
                                         data_to_encrypt)

        regmap_body = legacy_regmap_obj.to_json()
        regmap_body_encrypted = JSON_Serialisation.Encrypt_JSON_string(
            regmap_body)

        regmap_header = "/****************************************************************\n"
        regmap_header += " *** File generated from tahini:\n"
        regmap_header += " *** Unique ID: 0x" + full_version.uid + "\n"
        regmap_header += " *** Name: " + fw_versions + "\n"
        regmap_header += " *** Major version: " + \
            str(full_version.git_versions[0].last_tag.major) + "\n"
        regmap_header += " *** Minor version: " + \
            str(full_version.git_versions[0].last_tag.minor) + "\n"
        regmap_header += """ ***
 *** THIS FILE HAS BEEN AUTOMATICALLY GENERATED
 *** DO NOT MAKE CHANGES TO THIS FILE DIRECTLY
 ***
 ****************************************************************/\n\n"""

        legacy_regmap_body_dict = json.loads(regmap_body_encrypted)
        legacy_regmap_body_json = json.dumps(legacy_regmap_body_dict, indent=4)

        return regmap_header + legacy_regmap_body_json

    @ staticmethod
    def __get_legacy_type(ctype: CType) -> str:
        """Convert CType into a legacy type string

        Args:
            ctype (CType): Cmap type to be converted

        Returns:
            str: Equivalent legacy type
        """
        if ctype == CType.UINT8:
            return "byte"
        if ctype == CType.INT8:
            return "sbyte"
        # Other types don't need to be converted
        return ctype.value

    @ staticmethod
    def __get_device_info(git_repo_name):
        """Get Device Information

        Args:
            git_repo_name (str): FW project name

        Raises:
            Exception: Raise if the device is not supported anymore

        Returns:
            DeviceInformation: Platform specific information
        """
        if git_repo_name == "dw9787-fw":
            return DeviceInformation.dw9787
        if git_repo_name == "rumba-s10-firmware":
            return DeviceInformation.rumba_s10
        if git_repo_name == "STM32-framework":
            return DeviceInformation.stm32
        if git_repo_name == "saturn":
            return DeviceInformation.cm8x4
        if git_repo_name == "LC898129-OC":
            raise Exception("Onsemi 129 is not supported in Tahini")
        return DeviceInformation.mock

    @ staticmethod
    def __get_registers_list(cmap: FullRegmap) -> list[LegacyRegmapRegister]:
        """Extract all the registers from the cmap source file

        Args:
            cmap (FullRegmap): Cmapsource object

        Returns:
            list[LegacyRegmapRegister]: List of all registers found in the regmap
        """
        registers_list = []

        list_of_reg_or_struct = cmap.regmap.children

        for _, each_item in enumerate(list_of_reg_or_struct):
            if each_item.type == Type.REGISTER:
                legacy_regmap_register = GenerateLegacyRegmap.__get_register_aliases(
                    each_item)
                if legacy_regmap_register is not None:
                    registers_list = registers_list + legacy_regmap_register

            elif each_item.type == Type.STRUCT:
                legacy_regmap_register = GenerateLegacyRegmap.__get_registers_info_from_struct(
                    each_item.struct.children)
                if legacy_regmap_register is not None:
                    registers_list = registers_list + legacy_regmap_register
        return registers_list

    @ staticmethod
    def __get_states_info(each_register: RegisterOrStruct) -> dict[str, int]:
        """Extract states information of a register if any

        Args:
            each_register (RegisterOrStruct): Register from which states info to be extracted

        Returns:
            dict[str, int]: States info of a register
        """
        if each_register.register.states is not None:
            states = {}
            for state in each_register.register.states:
                states[state.name.upper()] = state.value
        else:
            states = None

        return states

    @ staticmethod
    def __get_flags_info(each_register: RegisterOrStruct) -> dict[str, int]:
        """Extract flags information from a register and output a dictionary of flags that can
        be used in a legacy regmap file.

        Args:
            each_register (RegisterOrStruct): Register from which to extract the flags

        Returns:
            dict[str, int]: Flags information in legacy regmap format.
        """
        if each_register.register.bitfields is not None:
            flags = {}
            for bitfield in each_register.register.bitfields:
                # Assume num_bits is always 1, since legacy regmap files don't support fields larger than 1 bit anyways
                flags[bitfield.name.upper()] = bitfield.position
        else:
            flags = None

        return flags

    @ staticmethod
    def __get_register_aliases(each_register: RegisterOrStruct) -> list[LegacyRegmapRegister]:
        """Extract all the aliases of a register and generate their names with suffix and set their addresses

        Args:
            each_register (RegisterOrStruct): Register which has aliases

        Returns:
           list[LegacyRegmapRegister]: List of the aliases of registers
        """
        register_aliases = []

        states = GenerateLegacyRegmap.__get_states_info(each_register)
        flags = GenerateLegacyRegmap.__get_flags_info(each_register)
        legacy_type = GenerateLegacyRegmap.__get_legacy_type(each_register.register.ctype)

        if each_register.repeat_for is not None:
            for instance in each_register.get_instances():
                instance_name = each_register.name + instance.get_legacy_suffix()

                register_aliases.append(
                    LegacyRegmapRegister(
                        instance.addr,
                        instance_name.upper(),
                        legacy_type,
                        states,
                        flags,
                        each_register.access.value,
                        HostAccessOptions.INDIRECT.value))

        else:
            each_alias = LegacyRegmapRegister(each_register.addr,
                                              each_register.name.upper(),
                                              legacy_type,
                                              states,
                                              flags,
                                              each_register.access.value,
                                              HostAccessOptions.INDIRECT.value)
            register_aliases.append(each_alias)

        return register_aliases

    @ staticmethod
    def __get_registers_info_from_struct(each_struct):
        """Extract the list of a registers from a struct recursively

        Args:
            each_struct (Struct): Struct from contains other C struct and registers

        Returns:
            list[LegacyRegmapRegister]: List of all registers
        """
        register_list = []

        for _, each_item in enumerate(each_struct):

            if each_item.type == Type.STRUCT:
                register_list += GenerateLegacyRegmap.__get_registers_info_from_struct(
                    each_item.struct.children)

            if each_item.type == Type.REGISTER:
                register_list += GenerateLegacyRegmap.__get_register_aliases(
                    each_item)

        return register_list
