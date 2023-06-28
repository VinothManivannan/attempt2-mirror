"""
RegmapStructFile class for creating minfs regmap config files
Partially based on:
http://gitlab.cm.local/devops/tzatziki/-/blob/master/tzatziki/regmap_out/sslconfig.py
"""
from builtins import range
import json
from typing import List, Any
import tahini
from .file_types import FileTypes
from .file_base import FileBase


class RegmapStructFile(FileBase):
    """Class used to create and manipulate regmap struct files
    """

    def __init__(self, files: List[str], cmap_file: str, struct_name: str, file_name: str = None):
        """Create a handle that can be used to write a new regmap struct binary file.

        Args:
            files (List[str]): a list of paths to configuration files
            regmap_file (str): specifies the path to the regmap file
            struct_name (str): specifies the name of a structure to pack
            file_name (str): specifies the file name
        """

        self.file_type = FileTypes.STRUCT_BIN

        init_files = []

        if file_name is not None:
            self.file_name = file_name[:self.MAX_FILENAME_SIZE]
        else:
            self.file_name = struct_name[:self.MAX_FILENAME_SIZE]

        for file_init in files:
            with open(file_init, 'r', encoding="utf-8") as f_init:
                init_files.append(json.loads(f_init.read()))

        # Parse regmap
        cmap = tahini.CmapFullRegmap.load_json(cmap_file)

        # Search for the requested struct
        struct_match = tahini.search(name=struct_name, cmap_type=tahini.CmapType.STRUCT, node=cmap)

        # If the specified structure is found continue, otherwise an error that the structure
        # doesn't exist will be raised
        if struct_match is None:
            raise Exception("Structure not found")

        # Merge the config files
        configs = {}
        for config in init_files:
            configs.update(config['Reg'])

        self.data = parse_config(struct_match.result, configs)

    @property
    def file_name(self) -> str:
        return self._file_name

    @file_name.setter
    def file_name(self, newname: str):
        self._file_name = newname

    @property
    def file_type(self) -> FileTypes:
        return self._file_type

    @file_type.setter
    def file_type(self, newtype: FileTypes):
        self._file_type = newtype

    @property
    def data(self) -> bytes:
        return self._data

    @data.setter
    def data(self, newdata: bytes):
        self._data = newdata


def parse_config(struct: tahini.CmapRegisterOrStruct, configs: Any) -> bytearray:
    """This function parses the config files and packs the data according
    to the descriptions in the regmap file

    Args:
        struct (tahini.CmapRegisterOrStruct): Struct containing the registers to be filled
        configs (Any): Json data representing configuration of the registers inside the struct

    Raises:
        Exception: Register was not found

    Returns:
        bytearray: Bytes to fill the struct with
    """
    byte_array = bytearray(struct.size)
    starting_addr = struct.addr
    for register_name in configs:
        register_match = tahini.search(name=register_name, cmap_type=tahini.CmapType.REGISTER, node=struct)
        if register_match is None:
            raise Exception(f"Register {register_name} not found")

        offset = register_match.address - starting_addr

        # Copy register data in the buffer
        value = configs[register_name]["reset"]
        register_data = register_match.result.register.pack_value(value)
        for i in range(register_match.result.size):
            byte_array[offset + i] = register_data[i]

    return byte_array
