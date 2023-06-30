"""Function and utilities used to interface with the gimli command-line tool.
"""
from os import path
import platform
from typing import List
from subprocess import Popen, PIPE
import sys


class GimliCommandError(Exception):
    """Exception raised when a gimli command failed
    """
    pass


class TahiniGimli():
    """Implements `tahini gimli ...` sub-command
    """

    @staticmethod
    def main(elf_path: str, compile_unit_names: List[str]) -> None:
        """Generate input json file from object file (.elf, .exe, etc...)

        Args:
            elf_path (str): Name of FW binary
            compile_unit_names (List[str]): List of 'C' files

        Raises:
            NotImplementedError: Raised if the current platform does have a gimli implementation
            GimliCommandError: Raised if the return code was not 0
        """

        args = [elf_path]
        args.extend(compile_unit_names)

        this_folder = path.dirname(path.realpath(__file__))
        os_platform = platform.system()
        if os_platform == "Windows":
            gimli_path = path.join(this_folder, r'gimli/build-windows/gimli.exe')
        else:
            raise NotImplementedError(
                f"No gimli implementation found for {platform.system()}")

        full_command = [gimli_path]
        full_command.extend(args)

        with Popen(full_command, stdout=sys.stdout, stderr=PIPE) as process:
            process.wait()

            # Check for errors
            if process.returncode != 0:
                # Pass the error to stderr as well as raise an exception
                error = str(process.stderr.read(), encoding="UTF-8")
                sys.stderr.write(error)
                raise GimliCommandError(error)
