"""Implement functions used to import files from the legacy json format
"""
from dataclasses import dataclass
import json
from copy import deepcopy
from typing import Any, Optional, Dict, List, Tuple
from .input_json_schema import InputEnum, InputJson, InputRegmap, InputType, VisibilityOptions


def _to_camelcase(name: str) -> str:
    """Helper function to convert a name into camel-case
    """
    return name.title().replace("_", "")


class _ControlContext:
    """This class is used to manage and store the local contexts for control spaces and
    indexes as we recursively traverse the json nodes.
    """

    def __init__(self):
        self._spaces_stack = []
        self._indexes_stack = []
        self._prefix_stack = []
        self.spaces: Dict[str, List[str]] = {}
        self.indexes: Dict[str, int] = {}
        self.register_prefix: str = ""
        self.enums_by_local_name: Dict[str, InputEnum] = {}
        self.all_enums = []

    def add_enum(self, local_name: str, enum: InputEnum) -> None:
        """Add a new enum to be included in the input json

        Args:
            local_name (str): Local name of the enum in the current json context
            enum (InputEnum): Enum to be created
        """
        self.enums_by_local_name[local_name] = enum
        self.all_enums.append(enum)

    def read_control_indexes_and_spaces(self, node: Any, node_name: str) -> None:
        """Read control spaces and indexes from a given json node

        Args:
            node (Any): Json node
            node_name (str): Name of the json node
        """

        if "controlindexes" in node:
            self.indexes.update(node["controlindexes"])

        if "controlspaces" in node:
            self.spaces.update(node["controlspaces"])
            for name, aliases in node["controlspaces"].items():
                new_enum = InputEnum(
                    # Generate an unique name using parent node name as prefix
                    name=_to_camelcase(f"{node_name}_{name}"),
                    enumerators=[InputEnum.InputEnumChild(aliases[i], i) for i in range(len(aliases))]
                )
                self.add_enum(name, new_enum)

        self.register_prefix = str(node["prefix"]) if "prefix" in node else ""

    def add_enum_from_states_node(self, json_data: Any, value_enum: str, states_node: List[List[Any]]) -> None:
        """Add a new enum to be generated in the Input Regmap using legacy states

        Args:
            json_data (Any): Toplevel json node containing all the data 
            value_enum (str): Name of the enum to be generated in the Input Regmap
            states_node (List[List[Any]]): Json node containing the list of states for a given register
        """
        enumerators = []
        for state in states_node:
            enumerators.append(InputEnum.InputEnumChild(
                name=str(state[1]),
                value=int(state[2]),
                brief=json_data["State"][state[1]
                                         ]["brief"] if json_data["State"][state[1]] is not None and "brief" in json_data["State"][state[1]] else None
            ))

        self.add_enum(value_enum, InputEnum(name=value_enum, enumerators=enumerators))

    def add_enum_from_flags_node(self, json_data: Any, mask_enum: str, flags_node: List[List[Any]]) -> None:
        """Add a new enum to be generated in the Input Regmap using legacy flags

        Args:
            json_data (Any): Toplevel json node containing all the data 
            mask_enum (str): Name of the enum to be generated in the Input Regmap
            flags_node (List[List[Any]]): Json node containing the list of flags for a given register
        """
        enumerators = []
        for flag in flags_node:
            enumerators.append(InputEnum.InputEnumChild(
                name=f"{str(flag[1])}_MASK",
                value=int(flag[2]),
                brief=json_data["Flag"][flag[1]
                                        ]["brief"] if json_data["Flag"][flag[1]] is not None and "brief" in json_data["Flag"][flag[1]] else None
            ))

        self.add_enum(mask_enum, InputEnum(name=mask_enum, enumerators=enumerators))

    def push(self) -> None:
        """Save the current state of control indexes and spaces
        """

        self._spaces_stack.append(deepcopy(self.spaces))
        self._indexes_stack.append(deepcopy(self.indexes))
        self._prefix_stack.append(deepcopy(self.register_prefix))

    def pop(self) -> None:
        """Restore state from the last push
        """

        self.spaces = self._spaces_stack.pop()
        self.indexes = self._indexes_stack.pop()
        self.register_prefix = self._prefix_stack.pop()


@dataclass
class _InputRegmapResult:
    """Data resulting from the creation of an InputRegmap from a legacy json node.
    """

    input_regmap: InputRegmap
    next_offset: int
    alignment: int


def _get_alignment(input_regmap: InputRegmap) -> int:
    """Calculate alignment constraint of an InputRegmap (1, 2 or 4)

    Args:
        input_regmap (InputRegmap): Input regmap object

    Returns:
        int: Alignment constraint of the element in number of bytes
    """

    alignment = 1

    if input_regmap.type in InputType.STRUCT:
        for child in input_regmap.members:
            child_alignment = _get_alignment(child)
            alignment = max(alignment, child_alignment)
    else:  # Register
        alignment = input_regmap.byte_size

    return alignment


def _get_register_type(reg: Any, size: int) -> str:
    """Get register input type

    Args:
        reg (Any): Json node representing a register in Legacy json
        size (int): Size of the element in bytes

    Returns:
        str: Equivalent type of the register in new Input Json format
    """

    signed = bool(reg["signed"]) if "signed" in reg else False
    if "float" in reg and reg["float"] is True:
        return InputType.FLOAT[0]
    if (size, signed) == (1, False):
        return InputType.CTYPE_UNSIGNED_CHAR[0]
    if (size, signed) == (1, True):
        return InputType.CTYPE_SIGNED_CHAR[0]
    if (size, signed) == (2, False):
        return InputType.CTYPE_UNSIGNED_SHORT[0]
    if (size, signed) == (2, True):
        return InputType.CTYPE_SIGNED_SHORT[0]
    if (size, signed) == (4, False):
        return InputType.CTYPE_UNSIGNED_LONG[0]
    if (size, signed) == (4, True):
        return InputType.CTYPE_SIGNED_LONG[0]

    raise Exception(f"Could not validate InputType of register: {reg}")


def _get_array_size(node: Any, context: _ControlContext) -> Tuple[Optional[int], Optional[str]]:
    """Return size of array for a register or struct node

    Args:
        node (Any): Json node representing a register or struct in Legacy json
        context (_ControlContext): Object used to hold information about the current context

    Returns:
        Tuple[Optional[int], Optional[str]]: Type specifying the values for the properties
                                             "array_count" and "array_enum" in new Input Json format
    """

    array_count = None
    array_enum = None

    if "count" in node:
        array_count = int(node["count"])
    elif "repeatfor" in node:
        if node["repeatfor"] in context.indexes:
            array_count = context.indexes[node["repeatfor"]]
        elif node["repeatfor"] in context.spaces:
            array_enum = context.enums_by_local_name[node["repeatfor"]].name
            array_count = len(context.spaces[node["repeatfor"]])
        else:
            raise Exception(f"Repeatfor definition of '{node['repeatfor']}' was not found in current context.")

    return array_count, array_enum


def _create_reg(json_data: Any, name: str, byte_offset: int, context: _ControlContext) -> _InputRegmapResult:
    """Create a new InputRegmap for a "Reg" child node in a legacy json

    Args:
        json_data (Any): Json node containing all registers in Legacy json
        name (str): Name of the register
        byte_offset (int): Offset in input regmap
        context (_ControlContext): Object used to hold information about the current context

    Returns:
        _InputRegmapResult: Input regmap object created for the register
    """
    reg = json_data["Reg"][name]

    reg_size = reg["bytes"] if "bytes" in reg else 2
    reg_type = _get_register_type(reg, reg_size)

    alignment = reg_size
    byte_offset = _apply_alignment(byte_offset, alignment)

    array_count, array_enum = _get_array_size(reg, context)

    if "children" in reg and reg["children"][0][0] == "State":
        value_enum = _to_camelcase(f"{name}_States")
        context.add_enum_from_states_node(json_data, value_enum=value_enum, states_node=reg["children"])
    else:
        value_enum = None

    if "children" in reg and reg["children"][0][0] == "Flag":
        mask_enum = _to_camelcase(f"{name}_Flags")
        context.add_enum_from_flags_node(json_data, mask_enum=mask_enum, flags_node=reg["children"])
    else:
        mask_enum = None

    next_offset = byte_offset + reg_size * (array_count if array_count is not None else 1)

    # Add prefix only if is not already present in the register name
    if not name.startswith(context.register_prefix):
        name = f"{context.register_prefix}_{name}"

    hif_access = False if "host_access" in reg and reg["host_access"] == "direct" else True

    access = None
    if "access" in reg and reg["access"] == "public":
        access = VisibilityOptions.PUBLIC
    elif "access" in reg and reg["access"] == "private":
        access = VisibilityOptions.PRIVATE

    return _InputRegmapResult(
        input_regmap=InputRegmap(
            name=name.lower(),
            byte_size=reg_size,
            byte_offset=byte_offset,
            type=reg_type,
            array_count=array_count,
            array_enum=array_enum,
            value_enum=value_enum,
            mask_enum=mask_enum,
            brief=reg["brief"] if "brief" in reg else None,
            min=reg["min"] if "min" in reg else None,
            max=reg["max"] if "max" in reg else None,
            format=reg["format"] if "format" in reg else None,
            units=reg["units"] if "units" in reg else None,
            hif_access=hif_access,
            access=access),
        next_offset=next_offset,
        alignment=alignment)


def _create_reserved_reg(json_data: Any, name: str, byte_offset: int, context: _ControlContext) -> _InputRegmapResult:
    """Create a new InputRegmap for a "ReservedReg" child node in a legacy json

    Args:
        json_data (Any): Json node representing a reserved register in Legacy json
        name (str): Name of the reserved register
        byte_offset (int): Offset in input regmap
        context (_ControlContext): Object used to hold information about the current context

    Returns:
        _InputRegmapResult: Resulting input regmap object created
    """

    reg = json_data["ReservedReg"][name]
    reg_size = reg["bytes"] if "bytes" in reg else 2
    reg_type = _get_register_type(reg, reg_size)

    alignment = reg_size
    byte_offset = _apply_alignment(byte_offset, alignment)

    array_count, array_enum = _get_array_size(reg, context)

    next_offset = byte_offset + reg_size * (array_count if array_count is not None else 1)

    return _InputRegmapResult(
        input_regmap=InputRegmap(
            name=name.lower(),
            byte_size=reg_size,
            byte_offset=byte_offset,
            type=reg_type,
            array_count=array_count,
            array_enum=array_enum,
            access=VisibilityOptions.NONE),
        next_offset=next_offset,
        alignment=alignment)


def _apply_alignment(offset: int, alignment: int) -> int:
    """Apply some alignment constraint on a given offset, and return the new value.

    Args:
        offset (int): Current offset
        alignment (int): Alignment constraint

    Returns:
        int: New offset
    """

    if (offset % alignment) == 0:
        return offset

    return offset + alignment - (offset % alignment)


def _create_struct(json_data: Any,
                   name: str,
                   context: _ControlContext,
                   byte_offset: Optional[int] = None,
                   address: Optional[int] = None
                   ) -> _InputRegmapResult:
    """Create an InputRegmap from a legacy json struct node.

    Args:
        json_data (Any): Json node containing all structs in Legacy json
        name (str): Name of the struct
        context (_ControlContext): Object used to hold information about the current context
        byte_offset (Optional[int], optional): Offset in parent input regmap object. Defaults to None.
        address (Optional[int], optional): Address of the struct in the regmap. Defaults to None.

    Returns:
        _InputRegmapResult: Resulting input regmap object
    """

    if byte_offset is None and address is None:
        raise Exception("Error: Both byte_offset and address are None")

    struct = json_data["Struct"][name]

    context.push()
    context.read_control_indexes_and_spaces(struct, name)

    members = []
    offset = 0
    alignment = 1
    for child in struct["children"]:
        if child[0] == "Reg":
            result = _create_reg(json_data, name=child[1], byte_offset=offset, context=context)
        elif child[0] == "ReservedReg":
            result = _create_reserved_reg(json_data, name=child[1], byte_offset=offset, context=context)
        elif child[0] == "Struct":
            result = _create_struct(json_data, name=child[1], byte_offset=offset, context=context)
        else:
            raise Exception(f"Unknown type: {child[0]}")

        offset = result.next_offset
        alignment = max(alignment, result.alignment)

        members.append(result.input_regmap)

    if byte_offset is not None:
        byte_offset = _apply_alignment(byte_offset, alignment)

    if address is not None:
        address = _apply_alignment(address, alignment)

    # Perform last alignment adjustment to get the size of the struct
    byte_size = _apply_alignment(offset, alignment)

    # Identify if the struct is part of an array
    array_count, array_enum = _get_array_size(struct, context)

    # Calculate the next offset
    if address is not None:
        next_offset = address
    else:
        next_offset = byte_offset
    next_offset += byte_size * (array_count if array_count is not None else 1)

    hif_access = False if "host_access" in struct and struct["host_access"] == "direct" else True

    access = None
    if "access" in struct and struct["access"] == "public":
        access = VisibilityOptions.PUBLIC
    elif "access" in struct and struct["access"] == "private":
        access = VisibilityOptions.PRIVATE

    context.pop()

    return _InputRegmapResult(
        input_regmap=InputRegmap(
            name=name,
            byte_size=byte_size,
            byte_offset=byte_offset,
            type=InputType.STRUCT[0],
            address=address,
            members=members,
            array_count=array_count,
            array_enum=array_enum,
            hif_access=hif_access,
            brief=struct["brief"] if "brief" in struct else None,
            access=access),
        next_offset=next_offset,
        alignment=alignment)


def legacy_to_input_json(json_data: Any) -> InputJson:
    """Convert legacy json data to the new input json format

    Args:
        json_data (Any): Json data to be converted

    Returns:
        InputJson: Converted data
    """
    members = []

    context = _ControlContext()

    if "RegMap" in json_data:
        entry_node = json_data["RegMap"]
    elif "Module" in json_data:
        entry_node = json_data["Module"]
    elif "Chain" in json_data:
        entry_node = json_data["Chain"]
    elif "Actuator" in json_data:
        entry_node = json_data["Actuator"]
    else:
        raise Exception("Legacy converter not found!")

    entry_node = entry_node[next(iter(entry_node.keys()))]

    context.read_control_indexes_and_spaces(entry_node, "")

    # Generate members
    next_address = 0

    for child in entry_node["children"]:
        if len(child) == 3:
            next_address = int(child[2])

        if child[0] == "Struct":
            new_member = _create_struct(
                json_data,
                name=child[1],
                address=next_address,
                context=context)
            next_address += new_member.input_regmap.byte_size
        elif child[0] == "Reg":
            new_member = _create_reg(json_data, name=child[1], byte_offset=next_address, context=context)
        else:
            # Module, Chain, Actuator...
            new_member = None

        if new_member:
            members.append(new_member.input_regmap)

    # Generate enums
    enums = context.all_enums

    return InputJson(
        regmap=members,
        enums=enums
    )


def legacy_json_to_input_regmap(legacy_path: str) -> InputJson:
    """Import a legacy json file and convert it into an input json file

    Args:
        legacy_path (str): Path to the file containing the legacy json data

    Returns:
        InputJson: Converted data
    """

    with open(legacy_path, "r", encoding="utf-8") as file_in:
        json_data = json.load(file_in)

    return legacy_to_input_json(json_data)
