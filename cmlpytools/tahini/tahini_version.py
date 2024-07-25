"""
Repository class to generate version information of a FW project
"""
from typing import List, Optional
import datetime
import json
import os
import re
import subprocess
from .version_schema import LastTag, GitVersion, VersionInfo, ExtendedVersionInfo

VERSION_TAG_REGEX_G = r"((?P<major>[0-9]+)(\.)(?P<minor>[0-9]+)(\.)(?P<patch>[0-9]+))"


class InvalidArgumentError(Exception):
    """_summary_

    Args:
        Exception (_type_): _description_
    """
    pass


class InvalidProjectPathError(Exception):
    """_summary_

    Args:
        Exception (_type_): _description_
    """
    pass


class Repository():
    """Abstract class to generate basic and extended version information
    """
    project_path: str
    config_name: str
    config_id: int
    is_s10: None

    # origin_regex: easiest to work from right to left here
    #   (\.)?([\w]+)?\b     - Search for a pattern that has a '.' followed by any number of alpha-numeric characters
    #                         with an end of line after the characters. This searches for a ".git" in reality
    #   (?P<project>[\w-]+) - Searches for and combination of alpha-numeric characters and '-' characters. This is to
    #                         match the project name, such as "STM32-framework" or "dw-9787". The ?P<name> is so later
    #                         we can access what was found in this section.
    #   ([\w\./-]+)?(/) -     Finds any combination of alpha-numeric characters, ".", "/" or "-". Then the (/) at the
    #                         end denotes that the last character this should match before the ?P<project> will be a
    #                         "/". This matches the url of the project.
    ORIGIN_REGEX = r"/(?P<project>[\w-]+)(\.git)?$"

    # The version tag looks for any set of numbers separated by a ".", so for a tag like "2.10.3"
    VERSION_TAG_REGEX = VERSION_TAG_REGEX_G

    # The branch commit regex is similar, just accounting for the odd "-", and searching for alpha-numeric characters in
    # the commit_id
    BRANCH_COMMIT_TAG_REGEX = r"((-)(?P<branch>[0-9]+)(\.)(?P<release_num>[0-9]+))?"

    # The git branch regex is searching for issue numbers like "FW-123", or older "CAEF-123", so letters of any case,
    # followed by a "-", and then any set of numbers.
    GIT_BRANCH_REGEX = r"(?i)(?P<logs>((([a-z]+)(-)([0-9]+))))([\w-])"

    # A modified version of the version tag below. The "[g]" is there as the command used sometimes put a "g" infront of
    # the git hash
    SUBMODULE_TAG_REGEX = r"((?P<major>[0-9]+)(\.)(?P<minor>[0-9]+)(\.)(?P<patch>[0-9]+))?" \
        r"((-)(?P<branch>[0-9]+)(\.)(?P<release_num>[0-9]+))?"

    # This regex looks for patterns which indicates the branch which is merged to the Master,
    # i.e. "Merge branch 'FW-1234-"
    GITLAB_MERGE_REGEX = r"Merge branch '(?P<logs>([\w]+(-)[0-9]+))-"

    # S10 has a different versioning scheme to most other products, so needs it's own regex
    S10_VERSION_REGEX = r"rev(?P<major>[0-9]+)(\.)(?P<minor>[0-9]+)"

    def __init__(self, project_path, device_type, device_display_name, config_name, config_id):
        self.project_path = project_path
        self.device_type = device_type
        self.device_display_name = device_display_name
        self.config_name = config_name
        self.config_id = config_id

    def __find_top_level(self) -> GitVersion:
        """Find version information for Topcode

        Raises:
            Exception: If no project is found

        Returns:
            (GitVersion): Topcode version info
        """
        get_url_cmd = 'git remote get-url origin'
        git_project_url = self.run_command(get_url_cmd)
        search_git_project = re.search(self.ORIGIN_REGEX, git_project_url)
        if search_git_project is None:
            raise Exception('No git repository found')

        project_name = search_git_project.group('project')

        # The Rumba S10 uses a different versioning scheme following "revXXXXX.XX" so needs a different regex
        if 's10' in project_name:
            origin_tag_regex = self.S10_VERSION_REGEX + self.BRANCH_COMMIT_TAG_REGEX
            self.is_s10 = True
        else:
            origin_tag_regex = self.VERSION_TAG_REGEX + self.BRANCH_COMMIT_TAG_REGEX
            self.is_s10 = False

        get_version_cmd = 'git describe --tags --first-parent --always --abbrev=0'
        topcode_tag = self.run_command(get_version_cmd)

        get_log_cmd = 'git log --merges --pretty=%s'
        get_branch_cmd = 'git branch -a --contains HEAD'

        merge_string = self.__git_find_merge_list(get_log_cmd, get_branch_cmd,
                                                  self.GITLAB_MERGE_REGEX, self.GIT_BRANCH_REGEX)

        return self.__find_version(origin_tag_regex, topcode_tag, merge_string, project_name)

    def __find_submodules(self) -> List[GitVersion]:
        """Find version information for submodule

        Returns:
            (list[GitVersion]): Submodule version info
        """
        get_sub_urls_cmd = 'git submodule foreach --recursive git remote get-url origin'
        git_submodule_urls = self.run_command(
            get_sub_urls_cmd)
        git_submodule_urls.strip()
        git_submodule_urls = git_submodule_urls.splitlines()
        get_submodule_versions_cmd = \
            'git submodule foreach --recursive git describe --tags --first-parent --always --abbrev=0'
        submodule_tags = self.run_command(
            get_submodule_versions_cmd)
        submodule_tags = submodule_tags.splitlines()

        submodule_tag_index = 0
        version_list = []
        branch_ids = None
        for origin in git_submodule_urls:
            # The git command used here has 2 lines per command, the first being "Entering <local_path>"
            # which is needed for finding the branch list, and the second is the url of the project
            # which can be used for getting the last tag info
            if origin.startswith('Entering'):
                submodule_path = origin[10: -1]
                get_submodule_log_cmd = 'git -C ' + submodule_path + ' log --merges'
                get_submodule_branch_cmd = 'git -C ' + \
                    submodule_path + ' branch -a --contains HEAD'
                branch_ids = self.__git_find_merge_list(
                    get_submodule_log_cmd, get_submodule_branch_cmd, self.GITLAB_MERGE_REGEX, self.GIT_BRANCH_REGEX)

            elif re.search(self.SUBMODULE_TAG_REGEX, submodule_tags[submodule_tag_index]) is not None:
                assert branch_ids is not None  # Avoid pylance error "branch_ids can be None" later on
                origin_url = re.search(
                    self.ORIGIN_REGEX, origin).group('project')
                version_list.append(self.__find_version(
                    self.SUBMODULE_TAG_REGEX, submodule_tags[submodule_tag_index], branch_ids, origin_url))
                branch_ids = None
            submodule_tag_index += 1

        return version_list

    def __git_find_merge_list(self,
                              log_command: str,
                              branch_command: str,
                              merge_regex: str,
                              branch_regex: str
                              ) -> List[str]:
        """Find the list of branches of a project

        Args:
            log_command (str): Git command to get the list of merge commits
            branch_command (str): Git command to get the current branch
            merge_regex (str): Regex searching pattern like "Merge branch 'FW-1234-"
            branch_regex (str): Regex searching for pattern like "FW-123"

        Returns:
            list[str]: List of merged branches
        """
        branch_ids = []
        unique_id = []
        git_merge_log = self.run_command(log_command)
        git_merge_list = re.findall(merge_regex, git_merge_log)
        for item in git_merge_list:
            # As the `findall` regex will ping up multiplies of the regex we're looking for (this is due to in the merge
            # messages there are often multiple reference to the `FW-XXXX` number, so we only look for the first hit
            # ie element 0 of the list of results
            branch_ids.append(str(item[0]))

        git_branch_log = self.run_command(branch_command)

        if ('master' in git_branch_log) or ('main' in git_branch_log) or ('stable' in git_branch_log):
            pass
        else:
            git_branch_list = re.findall(branch_regex, git_branch_log)
            for item in git_branch_list:
                branch_ids.append(str(item[0]))

        # Branch IDs should be upper case
        for index in branch_ids:
            if index.upper() not in unique_id:
                unique_id.append(index.upper())

        # Remove duplications
        unique_id = list(dict.fromkeys(unique_id))

        return unique_id

    def __add_version(self, git_origin: str,
                      major: Optional[int],
                      minor: Optional[int],
                      patch: Optional[int],
                      branch: Optional[int],
                      release_num: Optional[int],
                      branch_ids: List[str]
                      ) -> None:
        """Generate version information in GitVersion python object form

        Args:
            git_origin (str): Git URL of the project
            major (str): Version tag major
            minor (str): Version tag minor
            patch (str): Version tag patch
            branch (_type_): Branch id
            release_num (str): Release number
            branch_ids (list[str]): List of branch ids those are merged

        Returns:
            (GitVersion): Version Tag information in GitVersion object format
        """

        last_tag_obj = LastTag(
            major, minor, patch, branch, release_num)

        git_version_obj = GitVersion(
            git_origin, last_tag_obj, branch_ids)

        return git_version_obj

    def __find_version(self, version_regex: str, version_tag: str, branch_ids: List[str], origin: str) -> GitVersion:
        """Find version information for Topcode project and submodules

        Args:
            version_regex (str): Regular Expression Pattern for tag info, such as "1.2.3-4567.8-9-10"
            version_tag (str): Git describe output which contains version information for a specific project
            branch_ids (list[str]): List of branch ids those are merged to the master
            origin (str): Git origin URL

        Returns:
        (GitVersion): Version Tag information in GitVersion object format
        """
        search_version_tag = re.search(version_regex, version_tag)
        if search_version_tag is None:
            raise Exception(f"Could not parse version information from version string: '{version_tag}'")

        major = search_version_tag.group('major')
        if major is not None:
            major = int(major)

        minor = search_version_tag.group('minor')
        if minor is not None:
            minor = int(minor)

        # The patch field does not exist for s10 so the regex will throw and error if it tries to search for it
        if self.is_s10 is False:
            patch = search_version_tag.group('patch')
            if patch is not None:
                patch = int(patch)
        else:
            patch = None

        branch = search_version_tag.group('branch')
        if branch is not None:
            branch = int(branch)

        release_num = search_version_tag.group('release_num')
        if release_num is not None:
            release_num = int(release_num)

        return self.__add_version(origin, major, minor, patch, branch, release_num, branch_ids)

    def run_command(self, command: str) -> str:
        """Run Git Command

        Args:
            command (str): Command to run

         Returns:
            (str): Git command output
        """
        raise NotImplementedError("Not implemented in Subclass")

    def __get_gitversion_list(self) -> List[GitVersion]:
        """Generate Git version informations for all repo (topcode and submodules)

        Returns:
            list[GitVersion]: Version Info for all repo (topcode+submodules)
        """
        topcode_version = self.__find_top_level()
        submodule_version = self.__find_submodules()

        full_gitversion = []
        full_gitversion.append(topcode_version)
        full_gitversion = full_gitversion + submodule_version
        return full_gitversion

    def __initialise_version(self, basic_version: VersionInfo, uid: str) -> None:
        """Initialize VersionInfo object

        Args:
            basic_version (VersionInfo): Basic version information of topcode
            uid (str): Firmware uid claimed from CMLWeb
        """
        topcode_version = self.__find_top_level()
        basic_version.project = topcode_version.name
        
        if uid == "git-sha":
            get_git_sha_cmd = 'git rev-parse HEAD'
            basic_version.uid = str(self.run_command(get_git_sha_cmd))[:8]
        else:
            basic_version.uid = uid
        
        get_version_cmd = 'git describe --tags --first-parent --always --long'
        full_version = (
            self.run_command(get_version_cmd)).rstrip()

        # format is either (master tag) maj.min.pat-commit-gitsha or 
        # (branch tag) maj.min.pat-branch.itration-commit-gitsha
        sub_str = full_version.split('-')

        if '.' in sub_str[1]:
            # branch tag
            latest_tag = sub_str[0] + '-' + sub_str[1]
            commits = sub_str[2]
        else:
            # master tag
            latest_tag = sub_str[0]
            commits = sub_str[1]

        basic_version.version = latest_tag if commits == "0" else full_version
        basic_version.timestamp = datetime.datetime.utcnow().replace(
            microsecond=0).isoformat() + "+00:00"

    def __initialise_full_version(self, full_version: ExtendedVersionInfo) -> None:
        """Initialize ExtendedVersionInfo object

        Args:
            full_version(ExtendedVersionInfo): Extended version information of a FW project
        """
        full_version.git_versions = self.__get_gitversion_list()

    def get_basic_version(self, uid: str) -> VersionInfo:
        """User function to generate basic version info

        Args:
            uid (str): Firmware uid claimed from CMLWeb

        Returns:
            (VersionInfo): Extended version info
        """
        self.verify_project_path()
        basic_version = VersionInfo(self.device_type, self.device_display_name, self.config_name, self.config_id)
        self.__initialise_version(basic_version, uid)
        return basic_version

    def deserialize_basic_version(self, version_file_path: str) -> VersionInfo:
        """User function deserialize basic version json to VersionInfo object

        Args:
            version_file_path (str): Path to the basic version info file

        Returns:
            (VersionInfo): Basic version info
        """
        self.check_if_file_exists(version_file_path)

        with open(version_file_path, encoding="UTF-8") as file:
            version_info_dict = json.loads(file.read())
            version_info_json = json.dumps(version_info_dict)

        basic_version_obj = VersionInfo.from_json(version_info_json)

        return basic_version_obj

    def deserialize_full_version(self, version_path: str, file_name: str) -> VersionInfo:
        """User function deserialize basic version json to ExtendedVersionInfo object

        Args:
            version_path (str): Path to the directory containing the full version info file
            file_name (str): Name of the file

        Returns:
            (VersionInfo): Extended version info
        """
        self.check_path_sanity(version_path)
        self.check_if_path_exists(version_path)

        file_path = os.path.join(
            version_path, file_name)

        self.check_if_file_exists(file_path)

        with open(file_path, encoding="UTF-8") as file:
            version_info_dict = json.loads(file.read())
            version_info_json = json.dumps(version_info_dict)

        full_version_obj = ExtendedVersionInfo.from_json(version_info_json)

        return full_version_obj

    def get_full_version(self, version_file_path: str) -> ExtendedVersionInfo:
        """User function to generate extended version info

        Args:
            version_file_path (str): Path to a basic version info file

        Raises:
            Exception: If path is None or empty string or not a string

        Returns:
            (ExtendedVersionInfo): Extended version info
        """
        self.verify_project_path()

        version_info_obj = self.deserialize_basic_version(
            version_file_path)

        full_version = ExtendedVersionInfo(
            device_type=self.device_type, device_display_name=self.device_display_name, config_name=self.config_name,
             config_id=self.config_id)

        full_version.project = version_info_obj.project
        full_version.uid = version_info_obj.uid
        full_version.version = version_info_obj.version
        full_version.device_type = version_info_obj.device_type
        full_version.config_name = version_info_obj.config_name
        full_version.config_id = version_info_obj.config_id
        full_version.timestamp = version_info_obj.timestamp

        self.__initialise_full_version(full_version)
        return full_version

    def check_path_sanity(self, path: str) -> None:
        """Check if the path is a valid string

        Args:
            path (str): Path to be checked

        Raises:
            NotImplementedError: The subclass did not implement this function
        """
        raise NotImplementedError("Not implemented in subclass")

    def check_if_path_exists(self, path: str) -> None:
        """Check if the path exists

        Args:
            path (str): Path to be checked

        Raises:
            NotADirectoryError: Directory does not exist
        """
        if os.path.exists(path) is False:
            error_msg = "The path " + path + " doesn't exist"
            raise NotADirectoryError(error_msg)

    def check_if_file_exists(self, path: str) -> None:
        """Check if the file exists

        Args:
            path (str): Path to be checked

        Raises:
            FileNotFoundError: File does not exist
        """
        if os.path.exists(path) is False:
            error_msg = "The file " + path + " doesn't exist"
            raise FileNotFoundError(error_msg)

    def verify_project_path(self) -> None:
        """Project path verification will be implemented in subclass
        """
        raise NotImplementedError("Not implemented in subclass")


class LiveRepository(Repository):
    """This subclass is for use in a real build process
    """

    def __init__(self, project_path: str, device_type: str, device_display_name: str, config_name: str, config_id: int):
        """Initialise a LiveRepository object

        Args:
            project_path (str): Path to the project
            config_name (str): Name of the build configuration
            config_id (int): ID of the build configuration
        """
        Repository.__init__(self, project_path, device_type, device_display_name, config_name, config_id)

        self.check_path_sanity(project_path)

    def run_command(self, command: str) -> str:
        """Run Git Command

        Args:
            command(str): Git command to run

        Returns:
            (str): Git command output
        """
        return str(subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, cwd=self.project_path),
                   encoding="UTF-8")

    def check_path_sanity(self, path: str) -> None:
        """Check if the path is a valid string

        Args:
            path (str): Path to be verfied

        Raises:
            InvalidArgumentError: Path is empty is not a valid string
        """
        if (path is None) or (path == "") or not isinstance(path, str):
            raise InvalidArgumentError(
                "Path must be a valid string, can't be None or empty string")

    def verify_project_path(self) -> None:
        """Verify if the project path is invalid or not a git repository for a LiveRepository object
        """

        self.check_if_path_exists(self.project_path)

        if os.path.isdir(self.project_path) is False:
            raise InvalidProjectPathError(
                "Project path exists but not a directory")

        try:
            self.run_command('git remote get-url origin')
        except subprocess.CalledProcessError as exec_origin:
            raise InvalidProjectPathError(
                "Project path exists but not a Git repository") from exec_origin


class TahiniVersion():
    """Implements tahini version commands
    """

    @staticmethod
    def create_version_info(project_path: str, device_type: str, device_display_name: str, config_name: str,
                            config_id: int, uid: str) -> VersionInfo:
        """Write version.info.json file

        Args:
            project_path (str): Project path
            device_type (str): Device type
            device_display_name (str): External display name of the device
            config_name (str): Name of the build configuration
            config_id (int): ID of the build configuration
            uid (str): Firmware uid claimed from CMLWeb

        Returns:
            VersionInfo: Basic version info object
        """

        repo = LiveRepository(project_path, device_type, device_display_name, config_name, config_id)
        return repo.get_basic_version(uid)

    @staticmethod
    def create_extended_version_info(project_path, version_info_path) -> ExtendedVersionInfo:
        """Create an ExtendedVersion object from an existing version info file

        Args:
            project_path (str): FW project path
            version_info_path (str): Path to version info json file

        Returns:
            ExtendedVersionInfo: Full version information of the FW project
        """

        version_info = VersionInfo.load_json(version_info_path)

        repo = LiveRepository(project_path, version_info.device_type, version_info.device_display_name,
                              version_info.config_name, version_info.config_id)

        return repo.get_full_version(version_info_path)
