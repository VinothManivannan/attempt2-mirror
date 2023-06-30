"""
File base class
"""
from os import path
import abc
from .binary_data import BinaryData
from .file_types import FileTypes


class FileBase(BinaryData):
    """Class used as a base for different types of files supported by MinFS
    """

    MAX_FILENAME_SIZE = 8

    def _get_name_from_path(self, file_path: str) -> str:
        """Get name of a file from its path
        """
        return path.splitext(path.basename(file_path))[0][:8]

    @property
    @abc.abstractmethod
    def file_name(self) -> str:
        """A getter function for the file name.
        """
        return

    @property
    @abc.abstractmethod
    def file_type(self) -> FileTypes:
        """A getter function for the file type.
        """
        return
