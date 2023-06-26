"""
Import unittest module to test
"""

import datetime
import tempfile
import unittest
import json
from cmlpytools.tahini.version_schema import GitVersion, LastTag, ExtendedVersionInfo
from cmlpytools.tahini.tahini_version import LiveRepository, Repository, InvalidProjectPathError, InvalidArgumentError


class MockRepositoryMaster(Repository):
    """Mock Repository for Master build
    """

    def run_command(self, command):
        """Run Git Command

    Args:
        command (str): Git command to run

    Returns:
        (str): Mock Git command output
    """

        if command == "git remote get-url origin":
            return "/topcode.git"

        if command == "git rev-parse --short HEAD":
            return "0123ABC"

        if command == "git describe --tags --first-parent --always --long":
            return "1.2.3-4567.8-9-gABCDEF"

        if command == "git log --merges --pretty=%s":
            return "Merge branch 'branch-00-topcde' into 'master'"

        if command == "git submodule foreach --recursive git remote get-url origin":
            return "Entering 'topcode/submodule1'" + "\n" + "topcode/submodule1.git" + "\n" + \
                "Entering 'topcode/submodule2'" + "\n" + "topcode/submodule2.git"

        if command == "git submodule foreach --recursive git describe --tags --first-parent --always --long":
            return "Entering 'topcode/submodule1'" + "\n" + "2.3.4-5678.9-10-gBCDEFA" + "\n" + \
                "Entering 'topcode/submodule2'" + "\n" + "3.4.5-6789.10-11-gCDEFAB"

        if command == "git -C topcode/submodule1 log --merges":
            return "Merge branch 'branch-01-submodule1' into 'master' \
                    Merge branch 'branch-03-submodule1' into 'master' \
                    Merge branch 'branch-05-submodule1' into 'master'"

        if command == "git -C topcode/submodule2 log --merges":
            return "Merge branch 'branch-02-submodule2' into 'master' \
                    Merge branch 'branch-04-submodule2' into 'master' \
                    Merge branch 'branch-06-submodule2' into 'master'"

        if command == "git branch -a --contains HEAD":
            return "master \
                    XYZ-789-branch-name \
                    remotes/origin/XYZ-789-branch-name"

        if command == "git -C topcode/submodule1 branch -a --contains HEAD":
            return "master \
                    ABC-123-branch-name \
                    remotes/origin/ABC-123-branch-name"

        if command == "git -C topcode/submodule2 branch -a --contains HEAD":
            return "master \
                    DEF-456-branch-name \
                    remotes/origin/DEF-456-branch-name"

        return None

    def check_path_sanity(self, path):
        """Not required in Mock repository
        """
        pass

    def verify_project_path(self):
        """Not required in Mock repository
        """
        pass


class MockRepositoryBranch(Repository):
    """Mock Repository for Master build

    Args:
        Repository(_type_): _description_
    """

    def run_command(self, command):
        """Run Git Command if built from branch

    Args:
        command (str): Git command to run

    Returns:
        (str): Mock Git command output
    """

        if command == "git remote get-url origin":
            return "/topcode.git"

        if command == "git describe --tags --first-parent --always --long":
            return "1.2.3-4567.8-9-gABCDEF"

        if command == "git log --merges --pretty=%s":
            return "Merge branch 'branch-00-topcde' into 'master'"

        if command == "git submodule foreach --recursive git remote get-url origin":
            return "Entering 'topcode/submodule1'" + "\n" + "topcode/submodule1.git" + "\n" + \
                "Entering 'topcode/submodule2'" + "\n" + "topcode/submodule2.git"

        if command == "git submodule foreach --recursive git describe --tags --first-parent --always --long":
            return "Entering 'topcode/submodule1'" + "\n" + "2.3.4-5678.9-10-gBCDEFA" + "\n" + \
                "Entering 'topcode/submodule2'" + "\n" + "3.4.5-6789.10-11-gCDEFAB"

        if command == "git -C topcode/submodule1 log --merges":
            return "Merge branch 'branch-01-submodule1' into 'master' \
                    Merge branch 'branch-03-submodule1' into 'master' \
                    Merge branch 'branch-05-submodule1' into 'master'"

        if command == "git -C topcode/submodule2 log --merges":
            return "Merge branch 'branch-02-submodule2' into 'master' \
                    Merge branch 'branch-04-submodule2' into 'master' \
                    Merge branch 'branch-06-submodule2' into 'master'"

        if command == "git branch -a --contains HEAD":
            return "XYZ-789-branch-name \
                    remotes/origin/XYZ-789-branch-name"

        if command == "git -C topcode/submodule1 branch -a --contains HEAD":
            return "ABC-123-branch-name \
                    remotes/origin/ABC-123-branch-name"

        if command == "git -C topcode/submodule2 branch -a --contains HEAD":
            return "DEF-456-branch-name \
                    remotes/origin/DEF-456-branch-name"

        return None

    def check_path_sanity(self, path):
        """Not required in Mock repository
        """
        pass

    def verify_project_path(self):
        """Not required in Mock repository
        """
        pass


class TestVersionInfo(unittest.TestCase):
    """This tests whether Repository class can be used to get git information
    as ExtendedVersionInfo object while building from master

    Args:
        unittest (<module 'unittest'>): Unittest module
    """

    # Following are some test values to verify the ExtendedVersionInfo class initialization and get_full_version()
    # These values are used in the mock git command functions, if these values are changed, the mock git command
    # function return values need to be changed, accordingly

    test_ver_topcode = GitVersion('topcode', LastTag(
        1, 2, 3, 4567, 8, 9), ['BRANCH-00'], 'ABCDEF')
    test_ver_submod1 = GitVersion('submodule1', LastTag(
        2, 3, 4, 5678, 9, 10), ['BRANCH-01', 'BRANCH-03', 'BRANCH-05'], 'BCDEFA')
    test_ver_submod2 = GitVersion('submodule2', LastTag(
        3, 4, 5, 6789, 10, 11), ['BRANCH-02', 'BRANCH-04', 'BRANCH-06'], 'CDEFAB')

    def test_version_info(self):
        """Test whether the version information of topcode and submodules could be generated using
            while building from master
        """
        test_obj = MockRepositoryMaster(
            "Mock/Path", "CONFIG_NAME", 10)

        version_info = test_obj.get_basic_version()

        self.assertEqual(version_info.project, "topcode")
        self.assertEqual(version_info.uid, "0123ABC")
        self.assertEqual(version_info.version, "1.2.3-4567.8-9-gABCDEF")
        self.assertEqual(version_info.config_name, "CONFIG_NAME")
        self.assertEqual(version_info.config_id, 10)
        # The timstamp check is done only for date, not time as its genereated real time
        data_time_now = datetime.datetime.utcnow().replace(
            microsecond=0).isoformat() + "+00:00"
        self.assertEqual(version_info.timestamp[0:9], data_time_now[0:9])

        full_version_info = test_obj.get_full_version(
            "./tests/tahini/data/test_version.info.json")

        self.assertEqual(full_version_info.project, "topcode")
        self.assertEqual(full_version_info.uid, "0123ABC")
        self.assertEqual(full_version_info.version, "1.2.3-4567.8-9-gABCDEF")
        self.assertEqual(full_version_info.config_name, "CONFIG_NAME")
        self.assertEqual(full_version_info.config_id, 10)
        self.assertEqual(full_version_info.timestamp,
                         "2022-09-13T12:26:02+00:00")

        self.assertEqual(
            full_version_info.git_versions[0].name, self.test_ver_topcode.name)
        self.assertEqual(
            full_version_info.git_versions[1].name, self.test_ver_submod1.name)
        self.assertEqual(
            full_version_info.git_versions[2].name, self.test_ver_submod2.name)

        self.assertEqual(full_version_info.git_versions[0].last_tag.major,
                         self.test_ver_topcode.last_tag.major)
        self.assertEqual(full_version_info.git_versions[1].last_tag.major,
                         self.test_ver_submod1.last_tag.major)
        self.assertEqual(full_version_info.git_versions[2].last_tag.major,
                         self.test_ver_submod2.last_tag.major)

        self.assertEqual(full_version_info.git_versions[0].last_tag.minor,
                         self.test_ver_topcode.last_tag.minor)
        self.assertEqual(full_version_info.git_versions[1].last_tag.minor,
                         self.test_ver_submod1.last_tag.minor)
        self.assertEqual(full_version_info.git_versions[2].last_tag.minor,
                         self.test_ver_submod2.last_tag.minor)

        self.assertEqual(full_version_info.git_versions[0].last_tag.patch,
                         self.test_ver_topcode.last_tag.patch)
        self.assertEqual(full_version_info.git_versions[1].last_tag.patch,
                         self.test_ver_submod1.last_tag.patch)
        self.assertEqual(full_version_info.git_versions[2].last_tag.patch,
                         self.test_ver_submod2.last_tag.patch)

        self.assertEqual(
            full_version_info.git_versions[0].last_tag.branch_id, self.test_ver_topcode.last_tag.branch_id)
        self.assertEqual(
            full_version_info.git_versions[1].last_tag.branch_id, self.test_ver_submod1.last_tag.branch_id)
        self.assertEqual(
            full_version_info.git_versions[2].last_tag.branch_id, self.test_ver_submod2.last_tag.branch_id)

        self.assertEqual(
            full_version_info.git_versions[0].last_tag.release_num, self.test_ver_topcode.last_tag.release_num)
        self.assertEqual(
            full_version_info.git_versions[1].last_tag.release_num, self.test_ver_submod1.last_tag.release_num)
        self.assertEqual(
            full_version_info.git_versions[2].last_tag.release_num, self.test_ver_submod2.last_tag.release_num)

        self.assertEqual(
            full_version_info.git_versions[0].last_tag.commit_num, self.test_ver_topcode.last_tag.commit_num)
        self.assertEqual(
            full_version_info.git_versions[1].last_tag.commit_num, self.test_ver_submod1.last_tag.commit_num)
        self.assertEqual(
            full_version_info.git_versions[2].last_tag.commit_num, self.test_ver_submod2.last_tag.commit_num)

        self.assertEqual(full_version_info.git_versions[0].branch_ids,
                         self.test_ver_topcode.branch_ids)
        self.assertEqual(full_version_info.git_versions[1].branch_ids,
                         self.test_ver_submod1.branch_ids)
        self.assertEqual(full_version_info.git_versions[2].branch_ids,
                         self.test_ver_submod2.branch_ids)

        self.assertEqual(full_version_info.git_versions[0].commit_id,
                         self.test_ver_topcode.commit_id)
        self.assertEqual(full_version_info.git_versions[1].commit_id,
                         self.test_ver_submod1.commit_id)
        self.assertEqual(full_version_info.git_versions[2].commit_id,
                         self.test_ver_submod2.commit_id)


class TestVersionInfoBranch(unittest.TestCase):
    """This tests whether Repository class can be used to get git information
    as ExtendedVersionInfo object while building from branch

    Args:
        unittest (<module 'unittest'>): Unittest module
    """

    test_ver_topcode = GitVersion('topcode', LastTag(
        1, 2, 3, 9, 4567, 8), ['BRANCH-00', 'XYZ-789'], 'ABCDEF')
    test_ver_submod1 = GitVersion('submodule1', LastTag(
        2, 3, 4, 10, 5678, 9), ['BRANCH-01', 'BRANCH-03', 'BRANCH-05', 'ABC-123'], 'BCDEFA')
    test_ver_submod2 = GitVersion('submodule2', LastTag(
        3, 4, 5, 11, 6789, 10), ['BRANCH-02', 'BRANCH-04', 'BRANCH-06', 'DEF-456'], 'CDEFAB')

    def test_version_info(self):
        """Test whether the version information of topcode and submodules could be generated using
            ExtendedVersionInfo class and its method while building from a branch
        """
        test_obj = MockRepositoryBranch(
            None, "CONFIG_NAME", 3)

        full_version_info = test_obj.get_full_version(
            "./tests/tahini/data/test_version.info.json")

        self.assertEqual(full_version_info.git_versions[0].branch_ids,
                         self.test_ver_topcode.branch_ids)
        self.assertEqual(full_version_info.git_versions[1].branch_ids,
                         self.test_ver_submod1.branch_ids)
        self.assertEqual(full_version_info.git_versions[2].branch_ids,
                         self.test_ver_submod2.branch_ids)


class TestSerialization(unittest.TestCase):
    """Serialization test

    Args:
        unittest (<module 'unittest'>): Unittest module
    """

    def test_serialization(self):
        """Test whether the object generated from ExtendedVersionInfo class can be serialized
        """

        test_obj = MockRepositoryMaster(
            None, None, None)

        full_version_info = test_obj.get_full_version(
            "./tests/tahini/data/test_version.info.json")

        # Serialize into json

        full_version_json = full_version_info.to_json()
        full_version_dict = json.loads(full_version_json)

        self.assertEqual(full_version_info.project,
                         full_version_dict["project"])
        self.assertEqual(full_version_info.uid,
                         full_version_dict["uid"])
        self.assertEqual(full_version_info.config_name,
                         full_version_dict["config_name"])
        self.assertEqual(full_version_info.config_id,
                         full_version_dict["config_id"])

        for index, git_version_list in enumerate(full_version_info.git_versions):

            self.assertEqual(
                git_version_list.name, full_version_dict["git_versions"][index]["name"])
            self.assertEqual(
                git_version_list.branch_ids, full_version_dict["git_versions"][index]["branch_ids"])
            self.assertEqual(
                git_version_list.last_tag.major, full_version_dict["git_versions"][index]["last_tag"]["major"])
            self.assertEqual(
                git_version_list.last_tag.minor, full_version_dict["git_versions"][index]["last_tag"]["minor"])
            self.assertEqual(
                git_version_list.last_tag.patch, full_version_dict["git_versions"][index]["last_tag"]["patch"])
            self.assertEqual(
                git_version_list.last_tag.branch_id, full_version_dict["git_versions"][index]["last_tag"]["branch_id"])
            self.assertEqual(
                git_version_list.last_tag.release_num,
                full_version_dict["git_versions"][index]["last_tag"]["release_num"])
            self.assertEqual(
                git_version_list.last_tag.commit_num,
                full_version_dict["git_versions"][index]["last_tag"]["commit_num"])
            self.assertEqual(
                git_version_list.branch_ids, full_version_dict["git_versions"][index]["branch_ids"])
            self.assertEqual(
                git_version_list.commit_id, full_version_dict["git_versions"][index]["commit_id"])


class TestDeserialization1(unittest.TestCase):
    """Deserialization test

    Args:
        unittest (<module 'unittest'>): Unittest module
    """

    def test_deserialization(self):
        """Test a json file with version info properties can be deserialized into ExtendedVersionInfo object
        """

        test_obj = MockRepositoryMaster(
            None, "CONFIG_NAME", 10)

        full_version_obj = test_obj.get_full_version(
            "./tests/tahini/data/test_version.info.json")

        # Serialize
        full_version_json = full_version_obj.to_json()

        # Deserialize into object
        full_version_deserialized = ExtendedVersionInfo.from_json(full_version_json)

        self.assertEqual(full_version_obj.project,
                         full_version_deserialized.project)
        self.assertEqual(full_version_obj.uid,
                         full_version_deserialized.uid)
        self.assertEqual(full_version_obj.version,
                         full_version_deserialized.version)
        self.assertEqual(full_version_obj.config_name,
                         full_version_deserialized.config_name)
        self.assertEqual(full_version_obj.config_id,
                         full_version_deserialized.config_id)
        self.assertEqual(full_version_obj.timestamp,
                         full_version_deserialized.timestamp)

        for index, git_version_list in enumerate(full_version_obj.git_versions):

            self.assertEqual(
                git_version_list.name, full_version_deserialized.git_versions[index].name)
            self.assertEqual(
                git_version_list.branch_ids, full_version_deserialized.git_versions[index].branch_ids)
            self.assertEqual(
                git_version_list.last_tag.major, full_version_deserialized.git_versions[index].last_tag.major)
            self.assertEqual(
                git_version_list.last_tag.minor, full_version_deserialized.git_versions[index].last_tag.minor)
            self.assertEqual(
                git_version_list.last_tag.patch, full_version_deserialized.git_versions[index].last_tag.patch)
            self.assertEqual(
                git_version_list.last_tag.branch_id, full_version_deserialized.git_versions[index].last_tag.branch_id)
            self.assertEqual(
                git_version_list.last_tag.release_num,
                full_version_deserialized.git_versions[index].last_tag.release_num)
            self.assertEqual(
                git_version_list.last_tag.commit_num, full_version_deserialized.git_versions[index].last_tag.commit_num)
            self.assertEqual(
                git_version_list.branch_ids, full_version_deserialized.git_versions[index].branch_ids)
            self.assertEqual(
                git_version_list.commit_id, full_version_deserialized.git_versions[index].commit_id)


class TestDeserialization2(unittest.TestCase):
    """Deserialization test

    Args:
        unittest (<module 'unittest'>): Unittest module
    """

    def test_deserialization(self):
        """This is to test whether an actual .json file can be deserialized into an object
        """

        test_obj = MockRepositoryMaster(
            None, "CONFIG_NAME", 10)

        basic_version_obj = test_obj.get_basic_version()

        basic_version_deserialized = test_obj.deserialize_basic_version(
            "./tests/tahini/data/test_version.info.json")

        self.assertEqual(basic_version_obj.project,
                         basic_version_deserialized.project)
        self.assertEqual(basic_version_obj.uid,
                         basic_version_deserialized.uid)
        self.assertEqual(basic_version_obj.version,
                         basic_version_deserialized.version)
        self.assertEqual(basic_version_obj.config_id,
                         basic_version_deserialized.config_id)
        self.assertEqual(basic_version_obj.config_name,
                         basic_version_deserialized.config_name)
        # The timestamp is genereated everytime the get_basic_version is called,
        # so this is compared against the string value from the json file directly
        self.assertEqual("2022-09-13T12:26:02+00:00",
                         basic_version_deserialized.timestamp)


class TestProjectPathValidity1(unittest.TestCase):
    """Test if the project path argument is correct (basic sanity check) in a live repository

    Args:
        unittest (<module 'unittest'>)
    """

    def test_project_path(self):
        """Test if the project_path is not None or ""
        """

        with self.assertRaises(InvalidArgumentError):
            LiveRepository(None, None, None)

        with self.assertRaises(InvalidArgumentError):
            LiveRepository("", None, None)


# Calls to setUp and tearDown are always made, disable the pylint suggestion to use 'with'
# pylint: disable=consider-using-with

class TestProjectPathValidity2(unittest.TestCase):
    """Verify if the project path is valid in a live repository

    Args:
        unittest (<module 'unittest'>)
    """

    mock_file: tempfile.TemporaryFile
    mock_directory: tempfile.TemporaryDirectory

    def setUp(self):
        """Set up our mock 'path' objects"""
        self.mock_file = tempfile.TemporaryFile()
        self.mock_directory = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Tear down our mock 'path' objects"""
        self.mock_file.close()
        self.mock_directory.cleanup()
        pass

    def test_project_path(self):
        """This tests if the project_path exists, is a directory and a valid git repo
        """

        with self.assertRaises(NotADirectoryError):
            test_obj = LiveRepository("invalid/path", None, None)
            test_obj.get_basic_version()

        with self.assertRaises(expected_exception=(InvalidArgumentError, InvalidProjectPathError)):
            test_obj = LiveRepository(self.mock_file.name, None, None)
            test_obj.get_basic_version()

        with self.assertRaises(InvalidProjectPathError):
            test_obj = LiveRepository(
                self.mock_directory.name, None, None)
            test_obj.get_basic_version()

    def test_version_info_path_exists(self):
        """Test if the path contains to version.info.json exists. MockRepositoryMaster is used so to skip
        project path sanity and validity checks. This test makes sure the script fails if there is no
        version.info.json file in the given version_path directory
        """

        with self.assertRaises(FileNotFoundError):
            test_obj = MockRepositoryMaster(
                self.mock_directory.name, None, None)
            test_obj.get_full_version(
                self.mock_directory.name + "invalid.file")

# pylint: enable=consider-using-with


if __name__ == '__main__':
    unittest.main()
