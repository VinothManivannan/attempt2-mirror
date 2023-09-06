"""
RegmapCfgFile class for creating minfs regmap config files
"""
from builtins import range
import json
from operator import itemgetter
from cmlpytools import tahini
from .shared import RegmapFileWriter
from .file_types import FileTypes
from .file_base import FileBase


class RegmapCfgParseError(Exception):
    """Exception raised when there is an issue with one of the regmap config files.
    """
    pass


class FileEntry():
    """Class used to compile new file entry. It is used only if the regmap compression is enabled
    """

    def __init__(self, address: int, data: bytes):
        """Create a handle that can be used to write a new file entry to the regmap config file.

        Args:
            address (int): specifies the address of the entry
            data (byte array): the value of the first register of the entry

        Returns:
            FileEntry object
        """
        self._data = bytearray()
        self._data += data
        self._address = address
        self._len = len(data)
        self._end = address + len(data)

    def append(self, address: int, data: bytes) -> None:
        """Add a register to the existing file entry.

        Args:
            address (int): specifies the address of the register to add
            data (bytearray): the value of the register to add
        """
        padding = address - self._end
        self._data += bytearray("\0" * (padding), encoding="utf-8")
        self._data += data
        self._len = self._len + padding + len(data)
        self._end = address + len(data)

    @property
    def data(self) -> bytes:
        """Binary data for this file entry
        """
        return self._data

    @property
    def address(self) -> int:
        """Register map address of the entry
        """
        return self._address

    @property
    def len(self) -> int:
        """File length of the entry in bytes
        """
        return self._len

    @property
    def end(self) -> int:
        """End address of the file entry in the regmap
        """
        return self._end


class RegmapCfgFile(FileBase):
    """Class used to create and manipulate regmap cfg files
    """

    FILE_HEADER_SIZE = 6

    def __init__(self, cfg_file: str, regmap_file: str, file_name: str = None, compressed: int = 0):
        """Create a handle that can be used to write a new regmap configuration file.

        Args:
            cfg_file (str): specifies the path to the configuration file
            regmap_file (str): specifies the path to the regmap file
            file_name (str): specifies the name of the output file
            file_compressed (int): mode 1 (1), mode 2 (2) or disable (0) the config file compression

        Returns:
            RegmapCfgFile object
        """

        self._values = []
        self._addresses = []
        self._total_entries = 0
        self._total_size = 0
        self.file_type = FileTypes.REGMAP_CFG
        if file_name:
            self.file_name = file_name[:self.MAX_FILENAME_SIZE]
        else:
            self.file_name = self._get_name_from_path(cfg_file)

        with open(cfg_file, 'r', encoding="UTF-8") as f_cfg:
            f_cfg_data = f_cfg.read()

        # Parse the regmap file and the config file
        json_data = json.loads(f_cfg_data)
        cmap_node = tahini.CmapFullRegmap.load_json(regmap_file)

        if "struct" in json_data:
            match = tahini.search(name=json_data['struct'], cmap_type=tahini.CmapType.STRUCT, node=cmap_node)

            if not match:
                raise RegmapCfgParseError(
                    f"Struct {json_data['struct']} was not found in the regmap file")

            offset = match.address
            cmap_node = match.result
        else:
            offset = 0

        for reg_conf in json_data['data']:
            if 'namespace' in reg_conf:
                namespace = reg_conf['namespace']
            else:
                namespace = None
            match = tahini.search(name=reg_conf['register'], cmap_type=tahini.CmapType.REGISTER, node=cmap_node,
                                  namespace=namespace)

            if not match:
                raise RegmapCfgParseError(
                    f"Register {reg_conf['register']} was not found in the regmap file")

            reg = match.result
            reg_conf['address'] = match.address - offset

            if "value" in reg_conf:
                reg_conf['data'] = reg.register.pack_value(reg_conf['value'])
            elif "flags" in reg_conf:
                try:
                    reg_conf['data'] = reg.register.pack_value_by_bitfields({field: 1 for field in reg_conf['flags']})
                except tahini.InvalidBitfieldsError as exc:
                    raise RegmapCfgParseError(f"Invalid flags found in '{reg_conf['flags']}' for register "
                                              + f"'{reg_conf['register']}' in the regmap config file.") from exc
            elif "state" in reg_conf:
                try:
                    reg_conf['data'] = reg.register.pack_value_by_state(reg_conf['state'])
                except tahini.InvalidStatesError as exc:
                    raise RegmapCfgParseError(
                        f"Invalid state '{reg_conf['state']}' for register '{reg_conf['register']}'"
                        " in the regmap config file.") from exc
            else:
                raise RegmapCfgParseError("No valid value, flag, or state found for the register "
                                          + f"'{reg_conf['register']}' in the regmap config file.")

        if compressed > 0:
            new_entry = None
            # determine the maximal distance between two registers based on the chosen
            # compression mode.
            if compressed == 2:
                distance = self.FILE_HEADER_SIZE
            elif compressed == 1:
                distance = 0
            else:
                raise RegmapCfgParseError("Unsupported compression algorithm")
            json_data['data'].sort(key=itemgetter('address'))

            # Assempble entries
            for reg_conf in json_data['data']:
                if new_entry is None:
                    # Create the first entry
                    new_entry = FileEntry(
                        reg_conf['address'], reg_conf['data'])
                elif (reg_conf['address'] - new_entry.end) > distance:
                    # Finalise the current entry and write it to the file.
                    # Create the next entry.
                    self._add_entry(new_entry.address, new_entry.data)
                    new_entry = FileEntry(reg_conf['address'], reg_conf['data'])
                elif (reg_conf['address'] - new_entry.end) < 0:
                    raise RegmapCfgParseError(f"Register {reg_conf['register']} detected twice in the parameter file.")
                else:
                    new_entry.append(reg_conf['address'], reg_conf['data'])
            # Finalise the final entry and write it to the file
            self._add_entry(new_entry.address, new_entry.data)
        else:
            # 1 regsiter results as one entry if there is no compression mode enabled
            for reg_conf in json_data['data']:
                self._add_entry(reg_conf['address'], reg_conf['data'])

        whandle = RegmapFileWriter(self._total_entries, self._total_size)
        for i in range(self._total_entries):
            whandle.add_entry(self._addresses[i], self._values[i])
        self.data = whandle.get_file()

    def _add_entry(self, addr, value):
        """Create a regmap cfg entry suitable for minfs file format

        Args:
            addr (int): Regmap address of the entry.
            value (str): Byte string in the regmap format
        """
        self._values.append(value)
        self._addresses.append(addr)
        self._total_entries += 1
        self._total_size += len(value)

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
