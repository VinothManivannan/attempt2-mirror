"""
Import json and dataclasses modules
Create 'InputJson' class to verify the format of input json files
"""
from enum import Enum
from dataclasses import field
from dataclasses import dataclass
from typing import Optional, List
from marshmallow_dataclass import class_schema
import marshmallow.exceptions
from schema import Schema


class InvalidInputRegmapError(Exception):
    """Class used to handle errors of regmap property
    """
    pass


class InvalidInputEnumError(Exception):
    """Class used to handle errors of enums property
    """
    pass


class InputJsonParserError(Exception):
    """Class used to handle errors when using InputJson dataclass method
    """
    pass


class InputJsonNotFoundError(Exception):
    """Class used to handle errors when input json is not found
    """
    pass


class VisibilityOptions(str, Enum):
    """Represents the visibility property of a register/struct:
    """
    NONE = "none"
    PUBLIC = "public"
    PRIVATE = "private"


class InputType:
    """Represents type of the target in a hierarchy for the input json file:
    """
    STRUCT = ["struct"]
    UNION = ["union"]
    STRUCT_OR_UNION = ["struct", "union"]
    FLOAT = ["float"]
    CTYPE_UNSIGNED_CHAR = ["unsigned char", "char unsigned"]
    CTYPE_SIGNED_CHAR = ["char", "signed char", "char signed"]
    CTYPE_UNSIGNED_SHORT = [
        "unsigned short", "short unsigned, unsigned short int",
        "short unsigned int", "short int unsigned"
    ]
    CTYPE_SIGNED_SHORT = ["short", "signed short", "short signed"]
    CTYPE_UNSIGNED_LONG = [
        "long unsigned int", "unsigned long int", "long int unsigned",
        "unsigned long", "long unsigned"
    ]
    CTYPE_SIGNED_LONG = [
        "signed long int", "long signed int", "long int signed",
        "signed long", "long signed", "long int", "long"
    ]
    CTYPE_UNSIGNED_INT = ["unsigned int", "int unsigned"]
    CTYPE_SIGNED_INT = ["signed int", "int signed", "int"]
    CTYPE_UNSIGNED_LONG_LONG = [
        "long long unsigned int", "unsigned long long int", "long long int unsigned",
        "unsigned long long", "long long unsigned"
    ]
    CTYPE_SIGNED_LONG_LONG = [
        "signed long long int", "long signed long int", "long long int signed",
        "signed long long", "long long signed", "long long int", "long long"
    ]


@dataclass(frozen=False)
class InputRegmap:
    """Represents the properties shown in regmap field in input json
    """
    type: str
    name: str
    byte_size: int
    namespace: Optional[str] = None
    cmap_name: Optional[str] = None
    format: Optional[str] = None
    address: Optional[int] = None
    members: Optional[List['InputRegmap']] = None
    brief: Optional[str] = None
    bit_size: Optional[int] = None
    bit_offset: Optional[int] = None
    byte_offset: Optional[int] = None
    min: Optional[float] = None
    max: Optional[float] = None
    units: Optional[str] = None
    value_enum: Optional[str] = None
    array_enum: Optional[str] = None
    array_count: Optional[int] = None
    mask_enum: Optional[str] = None
    cref: Optional[str] = None
    access: VisibilityOptions = field(default=None, metadata={"by_value": True})
    hif_access: Optional[bool] = None
    customer_alias: Optional[str] = None

    def get_cmap_name(self) -> str:
        """Get name to be used in the cmapsource file: Use in priority the property `cmap_name` if defined,
        otherwise use the instance name.

        Returns:
            str: Name of the node to use in the cmap file
        """
        return (self.cmap_name or self.name).lower()

    def get_array_size(self) -> int:
        """Get the total size of the element in bytes, taking into account all the elements
        of the array if it is one.

        Returns:
            int: Size of the element or array
        """
        return self.byte_size * (self.array_count or 1)

    def __post_init__(self):
        """Fields to check validity of InputRegmap field
        """
        if self.type in InputType.STRUCT_OR_UNION and self.members is None:
            raise InvalidInputRegmapError(f"struct or union '{self.name}' has no members field")

        if self.type in InputType.CTYPE_UNSIGNED_CHAR:
            pass
        elif self.type in InputType.CTYPE_SIGNED_CHAR:
            pass
        elif self.type in InputType.CTYPE_UNSIGNED_SHORT:
            pass
        elif self.type in InputType.CTYPE_SIGNED_SHORT:
            pass
        elif self.type in InputType.CTYPE_UNSIGNED_INT:
            pass
        elif self.type in InputType.CTYPE_SIGNED_INT:
            pass
        elif self.type in InputType.CTYPE_UNSIGNED_LONG:
            pass
        elif self.type in InputType.CTYPE_SIGNED_LONG:
            pass
        elif self.type in InputType.CTYPE_UNSIGNED_LONG_LONG:
            pass
        elif self.type in InputType.CTYPE_SIGNED_LONG_LONG:
            pass
        elif self.type in InputType.FLOAT:
            pass
        elif self.type in InputType.STRUCT_OR_UNION:
            pass
        else:
            raise InputJsonParserError("Invalid input json type")


@dataclass(frozen=False)
class InputEnum:
    """Represents the properties shown in enums field in input json
    """
    @dataclass(frozen=False)
    class InputEnumChild:
        """Represents the name and value of each enum property in input Json
        """
        name: str
        value: int
        brief: Optional[str] = None
        customer_alias: Optional[str] = None
        access: VisibilityOptions = field(default=None, metadata={"by_value": True})

    name: str
    enumerators: list[InputEnumChild]
    brief: Optional[str] = None

    def __post_init__(self):
        """Fields to check validity of InputEnum field
        """
        cup_name = []
        for items in self.enumerators:
            if items.name not in cup_name:
                cup_name.append(items.name)
            else:
                raise InvalidInputEnumError("States name should be unique")


@dataclass(frozen=False)
class InputJson:
    """
    An entry class to regulate the format from input json files
    """
    regmap: list[InputRegmap]
    enums: list[InputEnum]

    @staticmethod
    def load_json(json_path: str) -> "InputJson":
        """Create a InputJson object from a json file

        Args:
            json_path (str): Path to the json file

        Returns:
            InputJson: Deserialised python object

        Raises:
            InputJsonNotFoundError: Handle errors when input json is not found
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as loadfile:
                return InputJson.from_json(loadfile.read())
        except FileNotFoundError as exc:
            raise InputJsonNotFoundError(str(exc) + " file is not found") from exc

    @staticmethod
    def from_json(json_data: str) -> "InputJson":
        """Create a InputJson instance from a json string

        Args:
            json_data (str): json string to be deserialised

        Returns:
            InputJson: Deserialised python object

        Raises:
            InputJsonParserError: Handle errors when using InputJson dataclass method
        """
        try:
            json_obj = class_schema(InputJson, base_schema=Schema)().loads(json_data)
        except marshmallow.exceptions.ValidationError as exc:
            raise InputJsonParserError(str(exc) + " Invalid value in input json") from exc

        return json_obj

    def to_json(self, indent: int = 2) -> str:
        """Serialise python object into a json string

        Args:
            indent (int, optional): Number of spaces used for indentation. Defaults to 2.

        Returns:
            str: Python object serialised into a string
        """
        return class_schema(InputJson, base_schema=Schema)().dumps(self, indent=indent)
