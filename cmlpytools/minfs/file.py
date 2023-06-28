"""
RegmapCfgFile class for creating minfs files
"""
from .file_types import FileTypes
from .file_base import FileBase


class File(FileBase):
    """
    Class used to create and manipulate files
    """

    def __init__(self, bin_file_path, bin_file_type, bin_file_name=None):
        """
        Create a handle that can be used to write a new binary system.

        Args:
            bin_file_path (str): specifies the path to the binary file
            bin_file_type (str): specifies the type of the binary file
            bin_file_name (str): specifies the name of the output file
        """
        if hasattr(FileTypes, bin_file_type):
            file_type = getattr(FileTypes, bin_file_type)
        else:
            raise Exception("The file type is not supported")

        with open(bin_file_path, 'rb') as bin_file:
            bin_file_data = bin_file.read()
        self.data = bin_file_data

        self.file_type = file_type
        if bin_file_name:
            self.file_name = bin_file_name
        else:
            self.file_name = self._get_name_from_path(bin_file_path)

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
