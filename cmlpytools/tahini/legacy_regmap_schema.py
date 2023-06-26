"""Dataclasses for Legacy Regmap
    """
import sys
from os import path
from enum import Enum
from typing import Optional
from dataclasses import dataclass
import re

from marshmallow_dataclass import class_schema
from marshmallow.fields import Field
import marshmallow.exceptions
import clr
from tahini.schema import Schema
from tahini.version_schema import GitVersion


sys.path.append(path.dirname(path.realpath(__file__)))
clr.AddReference("SERVALib")


class LegacyRegmapParserError(Exception):
    """Class used to handle errors when using LegacyRegmap dataclass method
    """
    pass


class LegacyRegmapNotFoundError(Exception):
    """Class used to handle errors when LegacyRegmap is not found
    """
    pass


class HostAccessOptions(str, Enum):
    """Represents the visibility property of a register/struct:

        The name of the fields are case-sensitive, and must match the serialised representation
        in json. This is why pylint naming checks are disabled in this class.
    """
    INDIRECT = "indirect"
    DIRECT = "direct"


class DeviceInformation():
    """Device information of address and data size and endianness
    """
    dw9787 = {"Name": "dw9787", "Addr_Size": 2, "Reg_Size": 1,
              "Addr_Little_End": False, "Data_Little_End": False}
    rumba_s10 = {"Name": "rumba_s10", "Addr_Size": 2, "Reg_Size": 1,
                 "Addr_Little_End": False, "Data_Little_End": True}
    stm32 = {"Name": "stm32_framework", "Addr_Size": 2, "Reg_Size": 1,
             "Addr_Little_End": False, "Data_Little_End": True}
    cm8x4 = {"Name": "cm8x4", "Addr_Size": 2, "Reg_Size": 1,
             "Addr_Little_End": False, "Data_Little_End": False}
    mock = {"Name": "mock", "Addr_Size": 2, "Reg_Size": 1,
            "Addr_Little_End": False, "Data_Little_End": False}


class _LegacyRegmapSchema(Schema):
    """Schema used to change field names during serialisation or deserialisation of legacy regmap
    files so the names of the fields match what Cats expect to find, rather than the names in python.
    """

    def on_bind_field(self, field_name: str, field_obj: Field):
        """Convert field name between from internal representation (python) and
        external representation (json) for legacy regmap files
        """
        if "legacy_name" in field_obj.metadata:
            field_obj.data_key = field_obj.metadata["legacy_name"]
        else:
            field_obj.data_key = field_obj.data_key or field_name

# pylint: disable=invalid-name


@ dataclass
class LegacyRegmapRegister():
    """Dataclass for containing a register information in Legacy regmap
    """
    Address: int
    Name: str
    Type: str
    States: Optional[dict[str, int]]
    Flags: Optional[dict[str, int]]
    Access: str
    Host_access: str

    class Meta:
        """Options object for a Schema
        """
        ordered = True

    def __post_init__(self):
        """Check validity of fields in legacy regmap: Only allow upper-case.
        """
        pattern = re.compile(r"^[A-Z_]([A-Z0-9_]+)?$")

        if pattern.match(self.Name) is None:
            raise LegacyRegmapParserError(f"Invalid name for legacy regmap {self.Name}")

        if self.States:
            for state in self.States:
                if pattern.match(state) is None:
                    raise LegacyRegmapParserError(f"Invalid state for legacy regmap {state}")

        if self.Flags:
            for flag in self.Flags:
                if pattern.match(flag) is None:
                    raise LegacyRegmapParserError(f"Invalid flag for legacy regmap {flag}")


@ dataclass
class DataToEncrypt():
    """Data in the Register map to be encrypted
    """
    Versions: list[GitVersion]
    Registers: list[LegacyRegmapRegister]

    class Meta:
        """Options object for a Schema
        """
        ordered = True


@ dataclass
class LegacyRegmap():
    """Data Class for Legacy Regmap
    """
    Name: str
    Addr_Size: int
    Reg_Size: int
    Addr_Little_End: bool
    Data_Little_End: bool
    Versions: dict
    Timestamp: str
    Build_Config: str
    Build_Config_ID: str
    Secure: DataToEncrypt

    def to_json(self, indent: int = 2) -> str:
        """Serialise python object into a json string

        Args:
            indent (int, optional): Number of spaces used for indentation. Defaults to 2.

        Returns:
            str: Python object serialised into a string
        """
        return class_schema(LegacyRegmap, base_schema=_LegacyRegmapSchema)().dumps(self, indent=indent)

    @ staticmethod
    def load_json(json_path: str) -> "LegacyRegmap":
        """Create a LegacyRegmap object from a json file

        Args:
            json_path (str): Path to the json file

        Returns:
            InputJson: Deserialised python object

        Raises:
            LegacyRegmapNotFoundError: Handle errors when input json is not found
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as loadfile:
                return _LegacyRegmapSchema.from_json(loadfile.read())
        except FileNotFoundError as exc:
            raise LegacyRegmapNotFoundError(str(exc) + " file is not found") from exc

    @ staticmethod
    def from_json(json_data: str) -> "LegacyRegmap":
        """Create a LegacyRegmap instance from a json string

        Args:
            json_data (str): json string to be deserialised

        Returns:
            InputJson: Deserialised python object

        Raises:
            LegacyRegmapParserError: Handle errors when using LegacyRegmap dataclass method
        """
        try:
            json_obj = class_schema(LegacyRegmap, base_schema=_LegacyRegmapSchema)().loads(json_data)
        except marshmallow.exceptions.ValidationError as exc:
            raise LegacyRegmapParserError(str(exc) + " Invalid value in legacy regmap") from exc

        return json_obj

# pylint: enable=invalid-name
