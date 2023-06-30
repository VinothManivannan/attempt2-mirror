"""
RegmapCfgFile class for creating minfs regmap config files
"""
from typing import List
from builtins import str
import os
import binascii
from subprocess import Popen, PIPE
from io import FileIO
from .shared import FileSystemWriter
from .binary_data import BinaryData
from .file_base import FileBase


class FileSystem(BinaryData):
    """
    Class used to create and manipulate regmap cfg files
    """

    def __init__(self, files: List[FileBase]):
        """Create a new file system handle from the provided files.

        Args:
            files (List[FileBase]): List of files for the file system
        """
        super().__init__()

        self._fs_size = 0
        fs_data = bytearray()
        for fs_file in files:
            self._fs_size += (((len(fs_file.data)+7) >> 3)*8)
            fs_data += fs_file.data

        if len(fs_data) > 0:
            fs_data = binascii.hexlify(fs_data)
            self.uid = f"0x{format((hash(fs_data) & 0xffffffff), 'x')}"
        else:
            self.uid = f"0x{format(0xffffffff, 'x')}"

        self._file_system = FileSystemWriter(len(files), self._fs_size)

        uid_int = int(self.uid, 16)

        for fs_file in files:
            self._file_system.add_file(fs_file.file_name, fs_file.file_type, fs_file.data, uid_int)

        self.data = self._file_system.get_fs()

    @property
    def data(self) -> bytes:
        """Get binary data for the file system
        """
        return self._data

    @data.setter
    def data(self, newdata: bytes) -> None:
        self._data = newdata

    @property
    def uid(self) -> str:
        """Unique identifier of the file system
        """
        return self._uid

    @uid.setter
    def uid(self, uid: str):
        self._uid = uid

    def generate_file_report(self, cfg_paths: List[str], output_dir: str) -> None:
        """
        This function generates a file system report.
        The resulting file contains a unique file system hash value and infurmation about individual
        files.

        Args:
            cfg_paths (List[str]): A list of files to report
            output_dir (str): Output directory
        """
        f_path = os.path.join(output_dir, "file_system_info_" + self.uid + ".txt")
        with open(f_path, "w", encoding="utf-8") as file_io:
            file_io.write("----------------------------------------------------------------")
            file_io.write("\n File System Config UID: " + str(self.uid))
            file_io.write("\n----------------------------------------------------------------\n\n\n\n")

            # Iterate over each config file
            for cfg_file in cfg_paths:
                cfg_dir = os.path.dirname(cfg_file)
                cfg_file_name = os.path.basename(cfg_file)
                csa_cfg = os.path.join(cfg_dir, os.path.splitext(
                    cfg_file_name)[0] + "_info.txt")
                if os.path.exists(csa_cfg):
                    with open(csa_cfg, encoding="utf-8") as infile:
                        for line in infile:
                            file_io.write(line)
                    infile.close()
                elif os.path.abspath(cfg_file).endswith('.json'):
                    json_info(file_io, cfg_dir, cfg_file_name)


def json_info(write_file: FileIO, cfg_dir: str, cfg_file_name: str) -> None:
    """Write json version information into a specified IO file

    Args:
        write_file (FileIO): Open file handle to write the json info to
        cfg_dir (str): Directory of the config file, to extract git info
        cfg_file_name (str): Name of the config file
    """
    working_dir = os.getcwd()

    write_file.write("======================================================================"
                     "===========================\n")
    write_file.write("---- INFO FOR CONFIG " +
                     cfg_file_name + " ----\n")
    write_file.write("======================================================================"
                     "===========================\n\n\r")
    write_file.write("\nFile Path: \t" + cfg_dir + "\\" + cfg_file_name)
    write_file.write("\nGit SHA-1 : \t" + get_git_sha1(cfg_dir, working_dir))
    write_file.write("\nGit Remote URL: \t" + get_git_remote_info(cfg_dir, working_dir))


def get_git_sha1(file_dir: str, working_dir: str) -> str:
    """Get git sha1 for a given file directory, and return to the specified working dir.

    Args:
        file_dir (str): Git directory
        working_dir (str): Working directory to return to

    Returns:
        str: Full-sized git sha1
    """
    os.chdir(file_dir)
    with Popen(['git', 'rev-parse', 'HEAD'], stdout=PIPE, stderr=PIPE) as process:
        process.stderr.close()
        try:
            line = process.stdout.readlines()[0]
        except IOError:
            line = ("No git repo found")
    os.chdir(working_dir)
    return str(line, encoding="utf-8")


def get_git_remote_info(file_dir: str, working_dir: str) -> str:
    """Get git remote for a given directory, then return to the specified working dir.

    Args:
        file_dir (str): Git directory
        working_dir (str): Working directory to return to

    Returns:
        str: Remote url
    """
    os.chdir(file_dir)
    with Popen(['git', 'config', '--get', 'remote.origin.url'], stdout=PIPE, stderr=PIPE) as process:
        process.stderr.close()
        try:
            line = process.stdout.readlines()[0]
        except IOError:
            line = ("No remote found")
    os.chdir(working_dir)
    return str(line, encoding="utf-8")
