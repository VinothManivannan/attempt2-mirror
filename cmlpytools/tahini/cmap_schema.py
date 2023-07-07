"""
Import json and dataclasses modules
Create 'FullRegmap' class to operate CMapSource Json Files
"""
from enum import Enum
import re
from typing import Optional, List, Dict
from dataclasses import field
from dataclasses import dataclass
import struct
from marshmallow_dataclass import class_schema
from .schema import Schema
from .input_json_schema import VisibilityOptions as InputVisibilityOptions
from .version_schema import ExtendedVersionInfo


class InvalidRegisterStructError(Exception):
    """Class used to handle errors of common property in RegisterOrStruct
    """
    pass


class InvalidRegisterError(Exception):
    """Class used to handle errors of register property
    """
    pass


class InvalidStatesError(Exception):
    """Class used to handle errors of states property
    """
    pass


class InvalidBitfieldsError(Exception):
    """Class used to handle errors of bitfields property
    """
    pass


class InvalidRepeatForError(Exception):
    """Class used to handle errors of repeat_for property
    """
    pass


class Type(str, Enum):
    """Represents type of the target in a hierarchy.
    """
    REGISTER = "register"
    STRUCT = "struct"


class VisibilityOptions(str, Enum):
    """Represents the visibility property of a register/struct:
    """
    PUBLIC = "public"
    PRIVATE = "private"

    @staticmethod
    def from_input_enum(input_visibility: InputVisibilityOptions) -> "VisibilityOptions":
        """Convert VisibilityOptions of InputRegmap into Cmap

        Args:
            input_visibility (InputVisibilityOptions): Visibility option specified in the input json

        Returns:
            VisibilityOptions: Visibility option to use in the Cmap file
        """
        if input_visibility == InputVisibilityOptions.PRIVATE:
            return VisibilityOptions.PRIVATE
        if input_visibility == InputVisibilityOptions.PUBLIC:
            return VisibilityOptions.PUBLIC
        if input_visibility == InputVisibilityOptions.NONE:
            raise Exception("Error: Tried to convert input visibility option 'none' to Cmap.")
        raise Exception(f"Mapping for input visibility option {input_visibility} is not defined.")


class CType(str, Enum):
    """Represents the underlying C type of a register:
    """
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    FLOAT = "float"

    @staticmethod
    def get_bit_size(c_type: str) -> int:
        """Get bit size of the ctype

        Args:
            c_type (str): string representing the C type of a register as defined Cmap files

        Returns:
            int: Number of bits
        """
        return {
            CType.UINT8: 8,
            CType.UINT16: 16,
            CType.UINT32: 32,
            CType.INT8: 8,
            CType.INT16: 16,
            CType.INT32: 32,
            CType.FLOAT: 32,
        }.get(c_type)


@dataclass
class ArrayIndex:
    """Dictionary of ArrayIndex, indexed by name
    """
    count: int
    offset: int
    aliases: Optional[list[str]] = None
    brief: Optional[str] = None

    def __post_init__(self):
        """Fields to check validity of repeat_for field
        """
        if self.count < 1:
            raise InvalidRepeatForError("Count value in ArrayIndex should not be smaller than 1")
        if self.aliases is not None:
            if self.count != len(self.aliases):
                raise InvalidRepeatForError("Count value should be the number of aliases list")

            pattern = re.compile(r"^[a-z_]([a-z0-9_]+)?$")
            for alias in self.aliases:
                if pattern.match(alias) is None:
                    raise InvalidRepeatForError(f"Invalid alias format found in repeat_for: '{alias}'")


@dataclass
class State:
    """Represents the state of registers
    """
    name: str
    value: int
    brief: Optional[str] = None
    customer_alias: Optional[str] = None
    access: VisibilityOptions = field(default=None, metadata={"by_value": True})

    def __post_init__(self):
        """Fields to check validity of states field
        """
        if re.compile(r"^[a-z_]([a-z0-9_]+)?$").match(self.name) is None:
            raise InvalidStatesError(f"Invalid name: {self.name}")

    def get_customer_name(self):
        """Get name to be used for customer-facing documentation and files

        Returns:
            str: Name to be used with customers
        """
        return self.customer_alias if self.customer_alias else self.name


@dataclass
class Bitfield:
    """Represents the bitfield of registers
    """
    name: str
    position: int
    num_bits: int
    brief: Optional[str] = None
    states: Optional[list[State]] = None
    customer_alias: Optional[str] = None
    access: VisibilityOptions = field(default=None, metadata={"by_value": True})

    def __post_init__(self):
        """Fields to check validity of bitfields field
        """
        if re.compile(r"^[a-z_]([a-z0-9_]+)?$").match(self.name) is None:
            raise InvalidBitfieldsError("Invalid name")
        if self.position < 0:
            raise InvalidBitfieldsError("Position value should not be lower than 0")
        if self.num_bits < 1:
            raise InvalidBitfieldsError("Num_bits value should not be lower than 1")
        if self.states is not None:
            for item in self.states:
                bit_length = item.value.bit_length()
                if item.value < 0:
                    # One more bit to store the sign, which is not included in `int.bit_length()`
                    bit_length += 1
                if bit_length > self.num_bits:
                    raise InvalidBitfieldsError("Values in states exceed num_bits in bitfield {self.name}")

    def get_mask(self) -> int:
        """Get the mask value associated with the bitfield
        """
        mask = 0
        for i in range(self.num_bits):
            mask += 1 << i
        mask <<= self.position

        return mask

    def get_customer_name(self) -> str:
        """Get name to be used for customer-facing documentation and files

        Returns:
            str: Name to be used with customers
        """
        return self.customer_alias if self.customer_alias else self.name


@dataclass
class Register:
    """Represents the properties shown in a register
    """
    ctype: CType = field(metadata={"by_value": True})
    format: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    units: Optional[str] = None
    bitfields: Optional[list[Bitfield]] = None
    states: Optional[list[State]] = None

    def _post_init_register_check(self):
        """Register properies check
        """
        if self.format is not None:
            if re.compile(r"^Q(\d+\.)?\d+$").match(self.format) is None:
                raise InvalidRegisterError("Format is wrong which should be: Qn.m, Qn")
            if re.compile(r"^Q\d+$").match(self.format) is not None:
                num_format = self.format.split('Q')[1]
                if int(num_format) > CType.get_bit_size(self.ctype):
                    raise InvalidRegisterError("The format is not support the ctype")
                if self.max is not None:
                    if self.ctype.value[0] == 'u':
                        if 2 ** int(num_format) < self.max:
                            raise InvalidRegisterError("The unsigned max value exceeds the limit of format")
                    elif 2 ** (int(num_format) - 1) < self.max:
                        raise InvalidRegisterError("The signed max value exceeds the limit of format")
            else:
                num_1_format = self.format.split('.')[0].split('Q')[1]
                num_2_format = self.format.split('.')[1]
                if int(num_1_format) + int(num_2_format) > CType.get_bit_size(self.ctype):
                    raise InvalidRegisterError("The format is not support the ctype")
                if self.max is not None:
                    if self.ctype.value[0] == 'u':
                        if (2 ** int(num_1_format) + 1/(2 ** int(num_2_format))) < self.max:
                            raise InvalidRegisterError("The unsigned max value exceeds the limit of format")
                    elif (2 ** (int(num_1_format) - 1) + 1/(2 ** int(num_2_format))) < self.max:
                        raise InvalidRegisterError("The signed max value exceeds the limit of format")
        if self.min is not None and self.max is None:
            raise InvalidRegisterError("Maximum value is missing")
        if self.max is not None and self.min is None:
            raise InvalidRegisterError("Minimum value is missing")
        if self.max is None and self.min is None:
            pass
        elif self.ctype.value[0] == 'u' and self.min < 0:
            raise InvalidRegisterError("Minimum value should not be smaller than 0 in unsigned ctype")
        elif self.max < self.min:
            raise InvalidRegisterError("Minimum value should be smaller than maximum value")

    def _post_init_states_check(self):
        """States properties check
        """
        if self.states is not None:
            cup_1 = []
            for item in self.states:
                if item.value not in cup_1:
                    cup_1.append(item.value)
                else:
                    raise InvalidStatesError("States value should be unique")
                if self.min is not None or self.max is not None:
                    if item.value < self.min:
                        raise InvalidStatesError("States value should not be smaller than minimum value")
                    if item.value > self.max:
                        raise InvalidStatesError("States value should not be larger than maximum value")
                if self.ctype.value[0] == 'u':
                    if item.value < 0:
                        raise InvalidStatesError("Unsigned value should not be smaller than 0")
                    if item.value.bit_length() > CType.get_bit_size(self.ctype):
                        raise InvalidStatesError("States value exceed the limit of unsigned ctype")
                elif item.value.bit_length() > CType.get_bit_size(self.ctype) - 1:
                    raise InvalidStatesError("States value exceed the limit of signed ctype")

    def _post_init_bitfields_check(self):
        """Bitfields properies check
        """
        if self.bitfields is not None:
            if self.bitfields[0].position > CType.get_bit_size(self.ctype) or \
                    self.bitfields[0].num_bits > CType.get_bit_size(self.ctype):
                raise InvalidBitfieldsError("Bitfields position or num_bits values exceed the limit of ctype")
            cup_2 = []
            for item in self.bitfields:
                if (item.position + item.num_bits) > CType.get_bit_size(self.ctype):
                    raise InvalidBitfieldsError("Invalid position or num_bits to the ctype")
                index = item.position
                items = 0
                while items < len(range(item.num_bits)):
                    if index not in cup_2:
                        cup_2.append(index)
                        index = index + 1
                        items = items + 1
                    else:
                        raise InvalidBitfieldsError("Overlap bitfields detected")

    def __post_init__(self):
        """Fields to check validity of register field
        """
        self._post_init_register_check()
        self._post_init_states_check()
        self._post_init_bitfields_check()

    def pack_value(self, value: float) -> bytes:
        """Convert a value into bytes representation for the current register.

        Args:
            value (float): Value to be converted into bytes

        Raises:
            Exception: No conversion found for the register type, and this function
                       probably needs updating.

        Returns:
            bytes: Bytes representing the register value
        """
        if self.ctype == CType.FLOAT:
            format_string = "<f"
        elif self.ctype == CType.INT8:
            format_string = "<b"
        elif self.ctype == CType.UINT8:
            format_string = "<B"
        elif self.ctype == CType.INT16:
            format_string = "<h"
        elif self.ctype == CType.UINT16:
            format_string = "<H"
        elif self.ctype == CType.INT32:
            format_string = "<l"
        elif self.ctype == CType.UINT32:
            format_string = "<L"
        else:
            raise Exception(f"Bytes conversion is not known for register type: {self.ctype}")

        return bytes(struct.pack(format_string, value))

    def pack_value_by_bitfields(self, fields: Dict[str, int]) -> bytes:
        """Convert a list of field values into bytes representation for the current register.

        Args:
            fields (Dict[str, int]): List of values to write indexed using the field names

        Raises:
            InvalidBitfieldsError: Specified field was not found

        Returns:
            bytes: Bytes representing the register value
        """
        value = 0
        for field_name, field_value in fields.items():
            reg_value = None
            for bitfield in self.bitfields:
                if bitfield.name == field_name.lower():
                    reg_value = field_value * 2 ** bitfield.position
                    break

            if reg_value is None:
                raise InvalidBitfieldsError(
                    f"Field '{field_name}' was not found")

            value += reg_value

        return self.pack_value(value)

    def pack_value_by_state(self, state_name: str) -> bytes:
        """Get the bytes to be written into a register using its state

        Args:
            state_name (str): Name of the state

        Raises:
            InvalidStatesError: Specified state was not found

        Returns:
            bytes: Bytes representing the register value
        """
        for state in self.states:
            if state_name.lower() == state.name:
                return self.pack_value(state.value)
        raise InvalidStatesError(f"State '{state_name}' was not found.")


@dataclass
class Struct:
    """Represents the properties shown in a struct
    """
    children: List['RegisterOrStruct']


@dataclass
class RegisterOrStruct:
    """Represents the properties in a struct or register
    """
    name: str
    type: Type = field(metadata={"by_value": True})
    addr: int
    size: int
    brief: Optional[str] = None
    register: Optional[Register] = None
    struct: Optional[Struct] = None
    namespace: Optional[str] = None
    repeat_for: Optional[List[ArrayIndex]] = None
    offset: int = 0
    access: VisibilityOptions = field(default=None, metadata={"by_value": True})
    hif_access: Optional[bool] = None
    customer_alias: Optional[str] = None

    def __post_init__(self):
        """Fields to check validity of struct field
        """
        # name check
        if re.compile(r"^[a-z_]([a-z0-9_]+)?$").match(self.name) is None:
            raise InvalidBitfieldsError(f"Invalid register or struct name: {self.name}")
        # address check
        if self.addr < 0:
            raise InvalidRegisterStructError(f"Register or struct {self.name} has invalid address: {self.addr}")
        # check if register and struct fields are conflicted.
        if bool(self.register) ^ bool(self.struct) is False:
            raise InvalidRegisterStructError(
                f"Register or struct {self.name} must have either a register or a struct field")
        if self.type.value == Type.STRUCT.value and self.register is not None:
            raise InvalidRegisterStructError(f"Struct {self.name} must have struct field")
        if self.type.value == Type.REGISTER.value and self.struct is not None:
            raise InvalidRegisterStructError(f"Register {self.name} must have register field")

    @dataclass
    class ArrayInstance:
        """Class used to store information about a single instance or a struct or reg.
        """
        addr: int
        indexes: List[int]
        aliases: List[Optional[str]]

        def get_legacy_suffix(self) -> str:
            """Return suffix of the instance as it would appear in our "legacy" outputs (.regmap .flat.txt)

            Returns:
                str: Suffix to be used in legacy formats
            """
            aliases_or_indexes = [str(self.aliases[i] or self.indexes[i]) for i in range(len(self.indexes))]
            return "_".join(aliases_or_indexes)

    def _get_instances(self, instances: List[ArrayInstance], depth: int) -> List[ArrayInstance]:
        """Implement the internal logic of the function get_instance()

        Args:
            instances (List[ArrayInstance]): List of instances found so far given the level of recursion
            depth (int): Current depth of the recursion in the array indexes

        Returns:
            List[ArrayInstance]: List of instances found
        """

        if depth == len(self.repeat_for):
            return instances

        repeat_for = self.repeat_for[depth]

        new_instances = []
        for instance in instances:
            for index in range(repeat_for.count):
                addr = instance.addr + index * repeat_for.offset
                indexes = instance.indexes.copy()
                indexes.append(index)
                aliases = instance.aliases.copy()
                aliases.append(repeat_for.aliases[index] if repeat_for.aliases is not None else None)
                new_instances.append(RegisterOrStruct.ArrayInstance(addr, indexes, aliases))

        return self._get_instances(new_instances, depth=depth+1)

    def get_instances(self) -> List[ArrayInstance]:
        """Get list of instances for this register or struct based on the number of repeats.

        Returns:
            List[ArrayInstance]: List of all instances for the register
        """

        assert self.repeat_for is not None, "This element is not part of an array"

        return self._get_instances([RegisterOrStruct.ArrayInstance(self.addr, [], [])], depth=0)

    def get_customer_name(self) -> str:
        """Get name to be used for customer-facing documentation and files

        Returns:
            str: Name to be used with customers
        """
        return self.customer_alias if self.customer_alias is not None else self.name


@dataclass
class Regmap:
    """Represents the properties shown in regmap struct in json
    """
    children: list[RegisterOrStruct]

    def __post_init__(self):
        Regmap._check_no_duplicate_names(self.children)

    @staticmethod
    def _check_no_duplicate_names(children: list[RegisterOrStruct],
                                  register_names: Optional[list[str]] = None,
                                  struct_names: Optional[list[str]] = None,
                                  ) -> None:
        """Check that the register names in a cmapsource file are all unique.

        Args:
            children (list[RegisterOrStruct]): Regmap children to be checked
            register_names (Optional[list[str]], optional): Used to hold the current list of register names found
                                                            through reccursive calls. Defaults to None.
            struct_names (Optional[list[str]], optional): Used to hold the current list of struct names found
                                                          through reccursive calls. Defaults to None.

        Raises:
            InvalidRegisterStructError: Register or struct name is not unique
        """
        if register_names is None:
            register_names = []

        if struct_names is None:
            struct_names = []

        for child in children:
            if child.type == Type.REGISTER:
                if child.name in register_names:
                    raise InvalidRegisterStructError(f"Error: Register '{child.name}' is not unique.")

                register_names.append(child.name)
            else:
                if child.name in struct_names:
                    raise InvalidRegisterStructError(f"Error: Struct '{child.name}' is not unique.")

                struct_names.append(child.name)
                Regmap._check_no_duplicate_names(child.struct.children, register_names, struct_names)


@dataclass
class Scheme:
    """A class to store version of the cmapsource format used:
      - major number should increment when non-backward compatible change(s) are done to the cmapsource format
      - minor number should increment when a backward-compatible change is done (for instance - adding a new field)
    """
    major: int
    minor: int


@dataclass
class FullRegmap:
    """A class to store regmap properties of CMapSource json files
    """
    scheme: Scheme
    version: ExtendedVersionInfo
    regmap: Regmap

    @staticmethod
    def load_json(json_path: str) -> "FullRegmap":
        """Create a FullRegmap object from a json file

        Args:
            json_path (str): Path to the json file

        Returns:
            FullRegmap: Deserialised python object
        """
        with open(json_path, 'r', encoding='utf-8') as loadfile:
            return FullRegmap.from_json(loadfile.read())

    @staticmethod
    def from_json(json_data: str) -> "FullRegmap":
        """Create a FullRegmap instance from a json string

        Args:
            json_data (str): json string to be deserialised

        Returns:
            FullRegmap: Deserialised python object
        """
        return class_schema(FullRegmap, base_schema=Schema)().loads(json_data)

    def to_json(self, indent: int = 2) -> str:
        """Serialise python object into a json string

        Args:
            indent (int, optional): Number of spaces used for indentation. Defaults to 2.

        Returns:
            str: Python object serialised into a string
        """
        return class_schema(FullRegmap, base_schema=Schema)().dumps(self, indent=indent)
