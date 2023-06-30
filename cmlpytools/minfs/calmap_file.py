"""
CalmapFile class for creating minfs calmap files
"""
# import os
# from os import path
from builtins import str
import json
from cmlpytools import tahini
from .shared import CalmapFileWriter
from .file_types import FileTypes
from .file_base import FileBase

CAL_REG_TYPES = {'REG_TYPE_NONE':               0,  # no special handling required
                 'REG_TYPE_ACTUATOR':           1,
                 'REG_TYPE_CAMERA_BUILD':       2,
                 'REG_TYPE_LIB_PARAM':          3,
                 'REG_TYPE_FW_REG':             4
                 }


def _get_register_offset_in_struct(cmap: tahini.CmapFullRegmap, reg_name: str, struct_name: str) -> int:
    """Get the offset of a register in a given struct using their names.

    Args:
        cmap (tahini.CmapFullRegmap): cmapsource containing regmap information
        reg_name (str): Name of the register
        struct_name (str): Name of the struct

    Raises:
        CalmapParseError: Register could not be found in struct

    Returns:
        int: Offset in bytes of the register relatively to the struct
    """
    struct_match = tahini.search(
        name=struct_name, cmap_type=tahini.CmapType.STRUCT, node=cmap)
    if not struct_match:
        raise CalmapParseError(
            f"Struct name '{struct_name}' could not be found in the register map")

    reg_match = tahini.search(
        name=reg_name, cmap_type=tahini.CmapType.REGISTER, node=struct_match.result)
    if not reg_match:
        raise CalmapParseError(
            f"Register name '{reg_name}' could not be found in the register map")

    return reg_match.address - struct_match.address


class CalmapParseError(Exception):
    """Class used to handle parse errors
    """
    pass


class CalmapFile(FileBase):
    """Class used to create and manipulate packed structure files
    """

    def __init__(self, regmap_file: str, calmap_file: str, file_name: str = None):
        """Create a handle that can be used to write a new calibration map file.

        Args:
            regmap_file (str): specifies the path to the top-level regmap file
            calmap_file (str): specifies the path to the calibration map file
            file_name (str): specifies the name of the output file

        Returns:
            CalmapFile object
        """

        self._data = []
        self._file_type = FileTypes.CALMAP

        if file_name:
            self.file_name = file_name
        else:
            self.file_name = self._get_name_from_path(calmap_file)

        # Load top-level regmap
        cmap = tahini.CmapFullRegmap.load_json(regmap_file)

        # Load calmap definition file
        with open(calmap_file, "r", encoding="utf-8") as file_io:
            f_calmap = json.load(file_io)

        # Get the header information
        map_ver = f_calmap['version info']['map ver']

        # Read the calibration register properties
        calibration_regs = f_calmap['calibration_params']

        h_writer = CalmapFileWriter(len(calibration_regs), map_ver)

        for reg_name in list(calibration_regs.keys()):
            try:
                reg_type = calibration_regs[reg_name]['type']
            except KeyError as exc:
                raise CalmapParseError(f"'type' for register '{reg_name}' was not found") from exc
            try:
                num_bytes = calibration_regs[reg_name]['bytes']
            except KeyError as exc:
                raise CalmapParseError(f"'num_bytes' for register '{reg_name}' was not found") from exc
            try:
                valid_offset = calibration_regs[reg_name]['valid_flag_offset']
            except KeyError as exc:
                raise CalmapParseError(f"'valid_flag_offset' for register '{reg_name}' was not found") from exc
            try:
                cal_offset = calibration_regs[reg_name]['offset_in_cal_buffer']
            except KeyError as exc:
                raise CalmapParseError(f"'offset_in_cal_buffer' for register '{reg_name}' was not found") from exc

            # The register type determines if any special handling is required
            if reg_type == CAL_REG_TYPES['REG_TYPE_LIB_PARAM']:
                # Calibration value that needs to be stored in the library parameter regmap structure
                struct_name = f_calmap['Persist_Name'][0]
                regmap_offset = _get_register_offset_in_struct(cmap, reg_name, struct_name)
            elif reg_type == CAL_REG_TYPES['REG_TYPE_FW_REG']:
                # Calibration value that needs to be stored in the top-level firmware register structure
                struct_name = f_calmap['Top_Level_FW_Reg_Name'][0]
                regmap_offset = _get_register_offset_in_struct(cmap, reg_name, struct_name)
            else:
                # Calibration value does not need special handling
                regmap_offset = 0

            h_writer.add_entry(int(reg_type), int(cal_offset), int(valid_offset), int(num_bytes), int(regmap_offset))

        self.data = h_writer.get_file()

    @property
    def file_name(self) -> str:
        return self._file_name

    @file_name.setter
    def file_name(self, newname: str) -> None:
        self._file_name = newname

    @property
    def file_type(self) -> int:
        return self._file_type

    @file_type.setter
    def file_type(self, newtype: int) -> None:
        self._file_type = newtype

    @property
    def data(self) -> bytes:
        return bytes(self._data)

    @data.setter
    def data(self, newdata: bytes):
        self._data = newdata
