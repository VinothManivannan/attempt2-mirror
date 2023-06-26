"""
Import json and dataclasses modules
"""
from typing import Optional
from dataclasses import dataclass, field
from marshmallow_dataclass import class_schema
from tahini.schema import Schema


@dataclass
class LastTag():
    """Contains tag information of a git repository
    """

    major: Optional[int] = field(metadata=dict(metadata=dict(legacy_name="Major")))
    minor: Optional[int] = field(metadata=dict(metadata=dict(legacy_name="Minor")))
    patch: Optional[int] = field(metadata=dict(metadata=dict(legacy_name="Patch")))
    branch_id: Optional[int] = field(metadata=dict(metadata=dict(legacy_name="BranchId")))
    release_num: Optional[int] = field(metadata=dict(metadata=dict(legacy_name="ReleaseNumber")))
    commit_num: Optional[int] = field(metadata=dict(metadata=dict(legacy_name="CommitNumber")))

    def __init__(self, major=None, minor=None, patch=None, branch_id=None, release_num=None, commit_num=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.branch_id = branch_id
        self.release_num = release_num
        self.commit_num = commit_num


@dataclass
class GitVersion():
    """Contains Git version information of a git repo
    """

    name: str = field(metadata=dict(metadata=dict(legacy_name="Name")))
    last_tag: LastTag = field(metadata=dict(metadata=dict(legacy_name="LastTag")))
    branch_ids: Optional[list[str]] = field(metadata=dict(metadata=dict(legacy_name="BranchIds")))
    commit_id: str = field(metadata=dict(metadata=dict(legacy_name="CommitId")))

    def __init__(self, name=None, last_tag=None, branch_ids=None, commit_id=None):
        self.name = name
        self.last_tag = last_tag
        self.branch_ids = branch_ids
        self.commit_id = commit_id


@dataclass
class VersionInfo():
    """Class for storing basic version information for the topcode
    """
    project: str
    uid: str
    version: str
    config_name: Optional[str]
    config_id: Optional[int]
    timestamp: str

    def __init__(self, config_name, config_id, project=None, uid=None, version=None, timestamp=None):
        self.project = project
        self.uid = uid
        self.version = version
        self.config_name = config_name
        self.config_id = config_id
        self.timestamp = timestamp

    @staticmethod
    def load_json(json_path: str) -> "VersionInfo":
        """Create a VersionInfo object from a json file

        Args:
            json_path (str): Path to the json file

        Returns:
            VersionInfo: Deserialised python object
        """
        with open(json_path, 'r', encoding='utf-8') as loadfile:
            return VersionInfo.from_json(loadfile.read())

    @staticmethod
    def from_json(json_data: str) -> "VersionInfo":
        """Deserialise some json data into a python object

        Args:
            json_data (str): Json data provided as a string

        Returns:
            VersionInfo: Deserialised python instance
        """
        return class_schema(VersionInfo, base_schema=Schema)().loads(json_data)

    def to_json(self, indent: int = 2) -> str:
        """Serialise python object into a json string

        Args:
            indent (int, optional): Number of spaces used for indentation. Defaults to 2.

        Returns:
            str: Python object serialised into a string
        """
        return class_schema(VersionInfo, base_schema=Schema)().dumps(self, indent=indent)


@dataclass
class ExtendedVersionInfo(VersionInfo):
    """Class for storing full version information of a FW project which includes
    basic version(topcode) and list of git version(topcode+submodules)

    Args:
        list(GitVersion): Git Information
    """
    git_versions: list[GitVersion]

    def __init__(self, config_name, config_id, project=None, uid=None, version=None, timestamp=None, git_versions=None):
        VersionInfo.__init__(self, config_name,
                             config_id, project, uid, version, timestamp)
        self.git_versions = git_versions

    @staticmethod
    def load_json(json_path: str) -> "VersionInfo":
        """Create an ExtendedVersionInfo object from a json file

        Args:
            json_path (str): Path to the json file

        Returns:
            ExtendedVersionInfo: Deserialised python object
        """
        with open(json_path, 'r', encoding='utf-8') as loadfile:
            return ExtendedVersionInfo.from_json(loadfile.read())

    @staticmethod
    def from_json(json_data: str) -> "ExtendedVersionInfo":
        """Deserialise some json data into a python object

        Args:
            json_data (str): Json data provided as a string

        Returns:
            VersionInfo: Deserialised python instance
        """
        return class_schema(ExtendedVersionInfo, base_schema=Schema)().loads(json_data)

    def to_json(self, indent: int = 2) -> str:
        """Serialise python object into a json string

        Args:
            indent (int, optional): Number of spaces used for indentation. Defaults to 2.

        Returns:
            str: Python object serialised into a string
        """
        return class_schema(ExtendedVersionInfo, base_schema=Schema)().dumps(self, indent=indent)
