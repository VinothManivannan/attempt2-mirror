"""This module is a set of tools and functions used to simplify the release process

  Using the module it is possible to:
  - Upload a file to our amazon server
  - Convert an axf file into bin, hex or txt file
  - Prepare a servo library release
"""

from __future__ import print_function
from __future__ import absolute_import

from builtins import str
import os
import os.path
import stat
import tempfile
import shutil

from .gitutils import GitUtils


# Working DIR for running tests
TEMP_DIR = tempfile.gettempdir()
WORKING_DIR = os.path.join(TEMP_DIR, 'releases')


def on_rm_error(_func, path, _exc_info):
    """his function is used to handle read-only files that could not be deleted by shutil.rmtree
    """
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


class ARS:
    """Class containing functions used for releases.
    """

    def __init__(self):
        # Get pointers to submodules
        self.git_utils = GitUtils()

        # Create working dir if it doesn't already exist
        if os.path.exists(WORKING_DIR) is False:
            os.mkdir(WORKING_DIR)

    def export_release(self, src, tag, keep_paths, prefix="", silent=False):
        """Export a source directory in preparation for a release.
        This function copies a list of relative paths specified by keep_paths from the source directory
        into a new directory created in a temporary workspace. It also add 2 files VERSION.md and REVISION.md
        containing the version and revision of the source directory. The directory created is then compressed
        and the function returns the paths to the exported dir and compressed zip file.

        Args:
            src (str): Path to the root folder containing the files to include in the release.
            tag (str): Version or tag of the release
            keep_paths (List[str]): List of relative paths in the folder to include in the release
            prefix (str, optional): Prefix to append to the folder name. Defaults to "".
            silent (bool, optional): Enable verbose output. Defaults to False.

        Returns:
            Dict[str, str]: A dictionary containing 2 entries `dir` and `zip`, where the former is the
                path the new folder containing, and the later is the same directory archived in a zip file.
        """
        # Create temporary workspace
        self.__log('Creating a temporary workspace...', silent)
        release_name = prefix + tag
        working_dir = os.path.join(WORKING_DIR, "staging_" + release_name)
        if os.path.exists(working_dir):
            shutil.rmtree(working_dir, onerror=on_rm_error)
        os.mkdir(working_dir)

        # Create output directory
        self.__log('Creating output directory...', silent)
        out_dir = os.path.join(working_dir, release_name)
        os.mkdir(out_dir)

        # Export paths
        self.__log('Copying files...', silent)
        for path in keep_paths:
            self.__log('    Copying ' + path, silent)
            self.__rcopy(src, path, out_dir)

        # Add VERSION.md
        self.__log('Creating file VERSION.md...', silent)
        version_file = os.path.join(out_dir, 'VERSION.md')
        self.write_file(version_file, tag)

        # Make file REVISION.md
        self.__log('Creating file REVISION.md...', silent)
        self.write_revision_file(src, out_dir)

        # Make archive
        self.__log('Creating archive...', silent)
        zip_dir = shutil.make_archive(out_dir, 'zip', working_dir, release_name)

        # End
        self.__log('Release ready!', silent)
        return {'dir': out_dir,
                'zip': zip_dir}

    def write_file(self, dst, txt):
        """
        Create a simple file using a target path and a string content.

        :param dst: Path to the file to create
        :param txt: Content of the file
        :type dst: String
        :type txt: String
        """
        with open(dst, 'w', encoding="utf-8") as file_io:
            file_io.write(txt)

    def read_file(self, src):
        """Read a text file and return content.

        :param src: Path to the file to read
        :type src: String
        """
        with open(src, 'r', encoding="utf-8") as file_io:
            file_content = file_io.read()
        return file_content

    def write_revision_file(self, checkout_dir, dst):
        """
        Create a new file REVISION.md in dst containing the sha1 of checkout_dir.
        dst must be a repository.

        This function is deprecated and is only kept for backward compatibility purposes.
        Instead consider using writeVersionFile();

        :param checkout_dir: Path to input git repository
        :param dst: Output directory
        :type checkout_dir: String
        :type dst: String
        """
        if os.path.isdir(dst) is not True:
            raise ValueError('dst must be an existing directory')

        revision_file = os.path.join(dst, 'REVISION.md')
        sha1 = self.git_utils.get_sha1(checkout_dir)
        self.write_file(revision_file, sha1)

    def write_git_logs_file(self, checkout_dir, dst):
        """
        Create a new file GITLOGS.md in dst containing the logs of checkout_dir.
        dst must be an existing repository.

        :param checkout_dir: Path to input git repository
        :param dst: Output directory
        :type checkout_dir: String
        :type dst: String
        """
        if os.path.isdir(dst) is not True:
            raise ValueError('dst must be an existing directory')

        gitlogs_file = os.path.join(dst, 'GITLOGS.md')
        logs = self.git_utils.get_git_logs(checkout_dir)
        self.write_file(gitlogs_file, logs)

    def __rcopy(self, src, rpath, dst):
        """
        Copy a relative path (file or directory) to a target directory recreating
        any subdirectory present in rpath.
        The target directory should already exist, otherwise an exception will be raised.

        Example:
        `ars.__rcopy(src, 'a/b/c', dst)` will copy (src + /a/b/c) to (dst + /a/b/c)

        :param src: Source directory
        :param rpath: Path to copy relatively to src
        :param dst: Target directory
        :type src: String
        :type rpath: String
        :type dst: String
        """
        # Check that dst is an existing directory
        if os.path.isdir(dst) is False:
            raise Exception(str(dst) + ' must be an existing directory')

        # Check that rpath exists
        full_src = os.path.join(src, rpath)
        full_dst = os.path.join(dst, rpath)
        if os.path.exists(full_src) is False:
            raise Exception(str(full_src) + ' must be an existing path')

        # If full_src is a directory, copy using shutil.copytree
        if os.path.isdir(full_src):
            shutil.copytree(full_src, full_dst)

        # If full_src is a file, copy using shutil.copy
        else:
            # Make sure target directory exists
            full_dst_dir = os.path.dirname(full_dst)
            if os.path.exists(full_dst_dir) is False:
                os.makedirs(full_dst_dir)
            # Copy file
            shutil.copy2(full_src, full_dst)

    def __log(self, string, silent=False):
        """
        A print function with a silent argument.

        :param string: Argument to print
        :param silent: Enable or disable logs
        :type string: String
        :type silent: Boolean
        """
        if silent is False:
            print(string)
