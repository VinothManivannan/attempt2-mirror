"""This module is a wrapper of gitpython, it provides helpful functions to manipulate some of the Rumba git projects
"""

import sys
import os
import stat
import subprocess


def on_rm_error(_func, path, _exc_info):
    """Used to handle errors when calling `rmtree()`
    """
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    try:
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)
    except Exception:  # pylint: disable=broad-except
        pass


# Documentation for GitUtils class.
#
#  This class is just a container for helpful git functions
class GitUtils:
    """Contains basic utilities to get information on git repositories
    """

    def get_sha1(self, checkout_path, silent=True, digits=8):
        """Get commit sha1 from a git checkout.

        Args:
            checkout_path (str): Path to the git checkout
            silent (bool, optional): Enable verbose to stdout. Defaults to True.
            digits (int, optional): Number of characters to include in the sha1. Defaults to 8.

        Returns:
            str: sha1 of the git repository
        """
        # Change directory
        old_cwd = os.getcwd()
        os.chdir(checkout_path)

        # Get sha1 by executing git rev-parse HEAD at the checkout path
        command = 'git rev-parse HEAD'
        try:
            with open(os.devnull, 'w', encoding="utf-8") as devnull:
                if silent is True:
                    dev = devnull
                else:
                    dev = sys.stdout
                sha1 = subprocess.check_output(command, shell=True, stderr=dev).decode('utf-8')[:digits]
        except Exception as exc:
            raise Exception(checkout_path + ' is not in a git repository') from exc
        finally:
            os.chdir(old_cwd)

        return sha1

    def describe(self, checkout_path, silent=True):
        """
        Get tag of a source git repository using `git describe --tags`. Raise an exception if the path specified
        is not in a git repository.

        :param self: The object pointer
        :type self: Instance of GitUtils

        :param checkout_path: Path to the source git repository
        :type checkout_path: String

        :param silent: Enable or disable console output for this method
        :type silent: bool

        :return: 32 bits sha1
        :rtype: String (8 characters)
        """
        # Change directory
        old_cwd = os.getcwd()
        os.chdir(checkout_path)

        # Get sha1 by executing git rev-parse HEAD at the checkout path forcing the hash to a length of 8
        command = 'git describe --tags --abbrev=8'
        try:
            with open(os.devnull, 'w', encoding="utf-8") as devnull:
                if silent is True:
                    dev = devnull
                else:
                    dev = sys.stdout
                tag = subprocess.check_output(command, shell=True, stderr=dev).decode('utf-8')\
                    .replace("\r", "").replace("\n", "")
        except Exception as exc:
            raise Exception(checkout_path + ' is not in a git repository') from exc
        finally:
            os.chdir(old_cwd)

        return tag

    def get_git_logs(self, checkout_path):
        """
        Generate and return git logs in a string format.

        :param self: The object pointer
        :param checkout_path: Path to the source git repository
        :type self: Instance of GitUtils
        :type checkout_path: String
        :return: git logs
        :rtype: String
        """
        # Change directory
        old_cwd = os.getcwd()
        os.chdir(checkout_path)

        # Get git logs by executing git rev-parse HEAD at the checkout path
        command = 'git log --oneline --decorate'
        try:
            logs = subprocess.check_output(command, shell=True).decode('utf-8')
        except Exception as exc:
            raise Exception(checkout_path + ' is not in a git repository') from exc
        finally:
            os.chdir(old_cwd)

        return logs
