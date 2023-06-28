"""This module is just a wrapper for the shared minfs library.
"""
from __future__ import print_function

from typing import Union, Optional
from builtins import bytes, str
import ctypes
from os import path
import platform
from .file_types import FileTypes

# Load dll
_FOLDER_PATH = path.dirname(path.realpath(__file__))

_DLL = (ctypes.cdll.LoadLibrary(path.join(_FOLDER_PATH, r'lib_win_x64\minfs_win_x64.dll'))
        if (platform.system() == "Windows") else
        ctypes.cdll.LoadLibrary(path.join(_FOLDER_PATH, r'lib_linux_x64/minfs_linux_x64.so')))

# Error codes imported from minfs-retcodes.h
MINFS_RET_OK = 0
MINFS_RET_ERR_FORMAT = 1
MINFS_RET_BUFF_FULL = 2
MINFS_RET_INDEX_FULL = 3
MINFS_RET_ERR_FILE = 4
MINFS_RET_ERR_VERSION = 5
MINFS_RET_NOT_FOUND = 6
MINFS_RET_FILE_EXISTS = 7
MINFS_RET_DATA_FULL = 8
MINFS_RET_FS_NOT_INIT = 9


class MinFsError(Exception):
    """This class is used to convert error codes returned by the library into python exceptions.
    """

    def __init__(self, error: Optional[Union[str, int]] = None):
        """Represent an error raised in the underlying MinFs DLL.

        Args:
            error (Optional[Union[str, int]], optional): Error message or number. Defaults to None.

        Raises:
            TypeError: Invalid argument type
        """
        # Retrieve error message
        if isinstance(error, int):
            self._errnum = error
            self._message = self._set_error_message(error)
        elif isinstance(error, str):
            self._message = error
            self._errnum = None
        else:
            raise TypeError("Invalid argument.")

        # Call the base class constructor with the parameters it needs
        super().__init__(self._message)

    @property
    def errnum(self) -> int:
        """Integer error identifier"""
        return self._errnum

    @property
    def message(self) -> str:
        """Error message"""
        return self._message

    def _set_error_message(self, code: int) -> str:
        """Set a human readable description of an error code returned by the dll library

        Args:
            code (int): Error code by the dll

        Returns:
            str: Error message associated with the code
        """
        if code == MINFS_RET_ERR_FORMAT:
            return "File format is invalid or is not supported."
        if code == MINFS_RET_BUFF_FULL:
            return "Invalid buffer: The size of the file buffer provided is too small"
        if code == MINFS_RET_INDEX_FULL:
            return "The index of the file is full"
        if code == MINFS_RET_ERR_FILE:
            return "Error reading file: Corrupted data or invalid format."
        if code == MINFS_RET_ERR_VERSION:
            return "The Build ID and/or the Firmware UID provided by the user do not match "\
                + "the version information attached to the file"
        if code == MINFS_RET_NOT_FOUND:
            return "The requested file was not found"
        if code == MINFS_RET_FILE_EXISTS:
            return "pair name and type already exists"
        if code == MINFS_RET_DATA_FULL:
            return "The data section of the file system is full"
        if code == MINFS_RET_FS_NOT_INIT:
            return "Failed to initialise file system"

        return "The MinFS library failed with an unknown error code: " + str(code)


class CalmapFileWriter():
    """Class used to create and manipulate CalmapFileWriter handles from the library
    """

    def __init__(self, max_entries: int, map_version: int):
        """Create a handle that can be used to write a new calmap configuration file.

        Args:
            map_version (int): The version of the map file used to generate the file
            max_entries (int): Number of calmap entries to allocate in the index.
        """
        # Configure dll function
        c_new_writer = _DLL.CalmapFileWriter_New
        c_new_writer.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte]
        c_new_writer.restype = ctypes.c_void_p

        self._hdl = c_new_writer(max_entries, map_version)
        if self._hdl == 0:
            raise MinFsError()

    def __del__(self):
        """Release a handle that was previously allocated with `CalmapFileWriter()`
        """
        if self._hdl != 0:
            # Configure the external function
            c_free_writer = _DLL.CalmapFileWriter_Free
            c_free_writer.argtypes = [ctypes.c_void_p]
            c_free_writer(self._hdl)

    def add_entry(self, entry_type: int, cal_buffer_offset: int, validity_flag_offset: int,
                  num_bytes: int, regmap_offset: int):
        """Add a new entry to the file.

        Args:
            entry_type (int): Value indicating how this entry should be handled.
            num_bytes (int): Number of data bytes this entry comprises
            validity_flag_offset (int): Offset of this entry's validity flag in the calibration buffer
            cal_buffer_offset (int): Offset of this entry's data in the calibration buffer
            regmap_offset (int): Offset of storage for this entry's data in the regmap (not used for all types)
        """
        # Configure dll function
        c_add_entry = _DLL.CalmapFileWriter_AddEntry
        c_add_entry.argtypes = [ctypes.c_void_p, ctypes.c_ubyte,
                                ctypes.c_ushort, ctypes.c_ushort, ctypes.c_ushort, ctypes.c_ushort]

        # Add entry
        ret = c_add_entry(self._hdl, entry_type, cal_buffer_offset, validity_flag_offset, num_bytes, regmap_offset)
        if ret != MINFS_RET_OK:
            raise MinFsError(ret)

    def get_file(self) -> bytearray:
        """Get memory location of the buffer where the file is written.

        Returns:
            bytearray: A buffer in the requested file
        """
        # Configure dll function
        c_get_file = _DLL.CalmapFileWriter_GetFile
        c_get_file.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

        # Create variables to receive the output of CalmapFileWriter_GetFile()
        file_loc = ctypes.c_void_p()
        file_len = ctypes.c_ushort()

        # Call dll function
        ret = c_get_file(self._hdl, ctypes.byref(file_loc), ctypes.byref(file_len))
        if ret != MINFS_RET_OK:
            raise MinFsError(ret)
        # Create a buffer to receive the content of the file
        file_buffer = ctypes.c_char * file_len.value
        buff = file_buffer()

        # Copy content of the file
        ctypes.memmove(buff, file_loc, file_len.value)
        return bytearray(buff)


class RegmapFileWriter():
    """Class used to create and manipulate RegmapFileWriter handles from the library
    """

    def __init__(self, max_entries: int, max_data: int):
        """Create a handle that can be used to write a new regmap configuration file.

        Args:
            max_entries (int): Number of regmap entries to allocate in the index.
            max_data (int): Number of bytes to allocate for data section.
        """
        # Configure dll function
        c_new_writer = _DLL.RegmapFileWriter_New
        c_new_writer.argtypes = [ctypes.c_ubyte, ctypes.c_ushort]
        c_new_writer.restype = ctypes.c_void_p

        self._hdl = c_new_writer(max_entries, max_data)
        if self._hdl == 0:
            raise MinFsError()

    def __del__(self):
        """Release a handle that was previously allocated with `RegmapFileReader_New()`
        """
        # Configure the external function
        c_free_writer = _DLL.RegmapFileWriter_Free
        c_free_writer.argtypes = [ctypes.c_void_p]

        c_free_writer(self._hdl)

    def add_entry(self, addr, data):
        """Add a new entry to the file.

        Args:
            addr (int): Regmap address of the entry.
            data (str): Byte string in the regmap format
        """
        # Configure dll function
        c_add_entry = _DLL.RegmapFileWriter_AddEntry
        c_add_entry.argtypes = [ctypes.c_void_p, ctypes.c_ushort, ctypes.c_char_p, ctypes.c_ushort]
        # This ensure data is provided as a bytearray
        data = bytearray(data)

        # Add entry
        ret = c_add_entry(self._hdl, addr, bytes(data), len(data))
        if ret != MINFS_RET_OK:
            raise MinFsError(ret)

    def set_fw_version(self, fw_uid: int, build_id: int):
        """Set Firmware version info for the file to be written.

        Args:
            fw_uid (int): Unique ID of the Firmware
            build_id (int): ID of the build configuration
        """
        set_fw_version = _DLL.RegmapFileWriter_SetFwVersion(self._hdl, fw_uid, build_id)
        set_fw_version.argtypes = [ctypes.c_uint, ctypes.c_ubyte]

        ret = set_fw_version(self._hdl, fw_uid, build_id)
        if ret != MINFS_RET_OK:
            raise MinFsError(ret)

    def get_file(self) -> bytearray:
        """Get memory location of the buffer where the file is written.

        Returns:
            bytearray: Copy of the file
        """
        # Configure dll function
        c_get_file = _DLL.RegmapFileWriter_GetFile
        c_get_file.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

        # Create variables to receive the output of RegmapFileWriter_GetFile()
        file_loc = ctypes.c_void_p()
        file_len = ctypes.c_short()

        # Call dll function
        ret = c_get_file(self._hdl, ctypes.byref(
            file_loc), ctypes.byref(file_len))
        if ret != MINFS_RET_OK:
            raise MinFsError(ret)
        # Create a buffer to receive the content of the file
        file_buffer = ctypes.c_char * file_len.value
        buff = file_buffer()
        # Copy content of the file
        ctypes.memmove(buff, file_loc, file_len.value)
        return bytearray(buff)


class FileSystemWriter():
    """Class used to create and manipulate FileSystemWriter handles from the library
    """

    def __init__(self, max_files: int, max_data: int):
        """Create a handle that can be used to write a new file system.
        """
        # Configure dll function
        c_new_writer = _DLL.FileSystemWriter_New
        c_new_writer.argtypes = [ctypes.c_ubyte, ctypes.c_ushort]
        c_new_writer.restype = ctypes.c_void_p

        self._hdl = c_new_writer(max_files, max_data)
        if self._hdl == 0:
            raise MinFsError()

    def __del__(self):
        """Release a handle that was previously allocated with `FileSystemWriter_New()`
        """
        # Configure the external function
        c_free_writer = _DLL.FileSystemWriter_Free
        c_free_writer.argtypes = [ctypes.c_void_p]

        c_free_writer(self._hdl)

    def add_file(self, file_name: str, file_type: FileTypes, file: bytes, uid: int):
        """Add a file to the file system

        Args:
            file_name (str): Name of the file in the file system
            file_type (FileTypes): Type of the file
            file (bytes): Content of the file
            uid (int): Unique identifier
        """
        c_add_file = _DLL.FileSystemWriter_AddFile
        c_add_file.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                               ctypes.c_ushort, ctypes.c_void_p, ctypes.c_ushort]

        # This ensure data is provided as a bytearray
        file = bytearray(file)

        ret = c_add_file(self._hdl, bytes(file_name, encoding="utf-8"), int(file_type), bytes(file), len(file), uid)

        if ret != MINFS_RET_OK:
            print(ret)
            raise MinFsError(ret)

    def get_fs(self):
        """Get memory copy of the buffer where the file system is written.

        Returns:
            bytearray: a buffer with a copy of the requested file system
        """
        # Configure dll function
        c_get_fs = _DLL.FileSystemWriter_GetFS
        c_get_fs.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

        # Create variables to receive the output of FileSystemWriter_GetFS()
        fs_loc = ctypes.c_void_p()
        fs_len = ctypes.c_short()

        # Call dll function
        ret = c_get_fs(self._hdl, ctypes.byref(fs_loc), ctypes.byref(fs_len))
        if ret != MINFS_RET_OK:
            raise MinFsError(ret)
        # Create a buffer to receive the content of the file system
        fs_buffer = ctypes.c_char * fs_len.value
        buff = fs_buffer()
        # Copy content of the file system
        ctypes.memmove(buff, fs_loc, fs_len.value)
        return bytearray(buff)
