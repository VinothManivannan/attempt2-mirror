"""This file is inteded to generate a number of OUTPUTS to the CmapSource File,
"""
from typing import List, Optional, Dict, Tuple
import re
from copy import deepcopy
import marshmallow.exceptions
from .cmap_schema import ArrayIndex as CmapArrayIndex
from .cmap_schema import Bitfield as CmapBitfield
from .cmap_schema import FullRegmap as CmapFullRegmap
from .cmap_schema import CType as CmapCtype
from .cmap_schema import Register as CmapRegister
from .cmap_schema import RegisterOrStruct as CmapRegisterOrStruct
from .cmap_schema import Regmap as CmapRegmap
from .cmap_schema import State as CmapState
from .cmap_schema import Struct as CmapStruct
from .cmap_schema import Type as CmapType
from .cmap_schema import VisibilityOptions as CmapVisibilityOptions
from .cmap_schema import Scheme as CmapScheme
from .input_json_schema import (InputEnum, InputJson, InputJsonParserError,
                                      InputRegmap, InputType, VisibilityOptions)
from .tahini_version import TahiniVersion
from .version_schema import ExtendedVersionInfo


class TahiniCmapError(Exception):
    """Class used to handle errors when using dataclass method
    """
    pass


def _mask_to_bits(mask: int) -> Tuple[int, int]:
    """Calculate the position and length of a field using its mask.

    Example: _mask_to_bits(0x30) == (4, 2)

    Args:
        mask (int): Mask representing the bitfield

    Returns:
        Tuple[int, int]: Position and length of the bitfield
    """
    field_pos = 0
    field_length = 0

    # Clear bits one by one until the mask is null
    bit = 0
    while mask != 0:
        new_mask = mask & ~(1 << bit)
        if new_mask == mask:
            # No bit was actually cleared
            field_pos += 1
        else:
            # A bit was cleared
            field_length += 1
        mask = new_mask
        bit += 1

    return (field_pos, field_length)


class _CmapContext:
    """A simple class used to store the context of the current node to build the Cmap file,
    in particular the number of array indexes.
    """
    _repeat_for: List[CmapArrayIndex]
    _stack: List[List[CmapArrayIndex]]

    def __init__(self) -> None:
        self._repeat_for = []
        self._stack = []

    def add_index(self, array_index: Optional[CmapArrayIndex]) -> None:
        """Add a repeated node to the current context
        """
        if array_index:
            self._repeat_for.append(array_index)

    def get_indexes(self) -> None:
        """Add a repeated node to the current context
        """
        return deepcopy(self._repeat_for) if len(self._repeat_for) > 0 else None

    def push(self) -> None:
        """Save the current state of indexes
        """
        self._stack.append(deepcopy(self._repeat_for))

    def pop(self) -> None:
        """Restore state from the last push
        """
        self._repeat_for = self._stack.pop()

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, _type, _value, _traceback):
        self.pop()


class TahiniCmap():
    """Implements the `tahini cmap ...` sub-command
    """
    @staticmethod
    def _remove_enum_prefix(input_enum: InputEnum) -> InputEnum:
        """Process an enum and remove prefix (if any) of the members of a given enum.

        For instance, if the input is an enum GYRO_AXES with members GYRO_AXES_RZ, GYRO_AXES_X, etc...
        then the prefix `GYRO_AXES_` will be removed.

        Args:
            input_enum (InputEnum): Enum definition to be processed

        Returns:
            InputEnum: Resulting enum definition after conversion
        """
        input_enum_children = []
        prefix = f"{input_enum.name}_".lower()
        for input_enum_child in input_enum.enumerators:
            if input_enum_child.name.lower().startswith(prefix):
                child_name = input_enum_child.name[len(prefix):]
            else:
                child_name = input_enum_child.name

            input_enum_children.append(InputEnum.InputEnumChild(
                name=child_name,
                brief=input_enum_child.brief,
                value=input_enum_child.value
            ))

        return InputEnum(
            name=input_enum.name,
            enumerators=input_enum_children,
            brief=input_enum.brief)

    @staticmethod
    def _cmap_repeat_for_from_input_regmap(input_regmap: InputRegmap,
                                           input_enum_by_name: Dict[str, InputEnum]
                                           ) -> Optional[CmapArrayIndex]:
        """Construct Cmap 'ArrayIndex' from an input regmap

        Args:
            input_regmap (InputRegmap): Input regmap to be converted
            input_enum_by_name (Dict[str, InputEnum]): List of enum definitions found in the input json

        Returns:
            Optional[CmapArrayIndex]: A Cmap "ArrayIndex" if the element was repeated, otherwise None.
        """
        if input_regmap.array_enum is not None:
            input_enum = input_enum_by_name[input_regmap.array_enum]
            aliases = []
            count = input_regmap.array_count or 1
            for enumerator in input_enum.enumerators:
                aliases.append(enumerator.name.lower())
            return CmapArrayIndex(count, input_regmap.byte_size,
                                  aliases[:count], input_enum.brief)

        if input_regmap.array_count is not None:
            return CmapArrayIndex(input_regmap.array_count, input_regmap.byte_size, None, None)

        return None

    @staticmethod
    def _cmap_bitfields_from_input_regmap(register: InputRegmap,
                                          input_enum_by_name: Dict[str, InputEnum]
                                          ) -> Optional[List[CmapBitfield]]:
        """Construct Cmap 'Bitfield' array from an input register.

        Args:
            register (InputRegmap): A register definition from an input json file
            input_enum_by_name (Dict[str, InputEnum]): List of enum definitions found in the input json

        Returns:
            Optional[List[CmapBitfield]]: List of bitfields associated with the register, or None if there aren't any.
        """
        if register.mask_enum is None:
            return None

        if register.mask_enum not in input_enum_by_name:
            raise TahiniCmapError(
                f"Mask enum '{register.mask_enum}' was specified, but no definition was found")
        input_enum = input_enum_by_name[register.mask_enum]

        field_pattern = re.compile(r"^(?P<field_name>[a-z_0-9]*)_MASK$", re.IGNORECASE)

        # Loop used to find bitfields in the enum
        bitfields = []
        enum_children = iter(input_enum.enumerators)
        enum_child = next(enum_children, None)
        while enum_child is not None:
            field_match = field_pattern.match(enum_child.name)

            if field_match is None:
                enum_child = next(enum_children, None)
                continue

            field_name = field_match["field_name"]
            field_mask = enum_child.value
            field_brief = enum_child.brief
            state_pattern = re.compile(f"^{field_name}_(?P<state_name>[a-z_0-9]*)(?<!(MASK))$", re.IGNORECASE)
            field_pos, field_length = _mask_to_bits(field_mask)

            # Loop used to find all the states associated with the bitfield. The states **MUST** be
            # following the initial mask declaration.
            field_states = []
            while (enum_child := next(enum_children, None)) is not None:
                state_match = state_pattern.match(enum_child.name)

                if state_match is None:
                    # Go back to the bitfield loop and see if this matches the bitfield pattern instead
                    break

                state_name = state_match["state_name"]

                # Verify that the state value found fits the associated mask
                if enum_child.value & field_mask != enum_child.value:
                    raise TahiniCmapError(f"Invalid state '{state_name}=0x{enum_child.value:x}' "
                                          f"found for field '{field_name}' with mask {field_mask}.")

                state_value = enum_child.value >> field_pos
                field_states.append(CmapState(name=state_name.lower(), value=state_value, brief=enum_child.brief))

            # Order states by value
            field_states.sort(key=lambda state: state.value)

            bitfields.append(CmapBitfield(name=field_name.lower(),
                                          position=field_pos,
                                          num_bits=field_length,
                                          brief=field_brief,
                                          states=field_states if len(field_states) > 0 else None))

        # Order bitfields by bit position
        bitfields.sort(key=lambda bitfield: bitfield.position)

        return bitfields if len(bitfields) > 0 else None

    @ staticmethod
    def _cmap_state_from_input_enumerator(input_enumerator: InputEnum.InputEnumChild) -> CmapState:
        """Construct Cmap 'State' from an enum constant

        Args:
            input_enumerator (InputEnum.InputEnumChild): Enum constant

        Returns:
            CmapState: Cmap state generated
        """
        return CmapState(
            brief=input_enumerator.brief,
            name=input_enumerator.name.lower(),
            value=input_enumerator.value)

    @ staticmethod
    def _cmap_states_from_input_enum(input_enum: InputEnum) -> List[CmapState]:
        """Construct Cmap 'State' array from an enum definition

        Args:
            input_enum (InputEnum): Enum definition to be converted

        Returns:
            List[CmapState]: List of states extracted from the enum definition
        """
        states = []
        for enumerator in input_enum.enumerators:
            states.append(TahiniCmap._cmap_state_from_input_enumerator(enumerator))

        # Sort states by values
        states.sort(key=lambda state: state.value)

        return states

    @ staticmethod
    def _cmap_states_from_input_regmap(input_regmap: InputRegmap,
                                       input_enum_by_name: Dict[str, InputEnum]
                                       ) -> Optional[List[CmapState]]:
        """Construct Cmap 'State' array from an input regmap object

        Args:
            input_regmap (InputRegmap): InputRegmap node to extract states from
            input_enum_by_name (Dict[str, InputEnum]): Set of enum definitions indexed by name

        Returns:
            Optional[List[CmapState]]: Array of Cmap states, or None if empty
        """
        states = None
        if input_regmap.value_enum is not None:
            states = TahiniCmap._cmap_states_from_input_enum(input_enum_by_name[input_regmap.value_enum])
        return states

    @ staticmethod
    def _cmap_ctype_from_input_regmap(input_regmap: InputRegmap) -> CmapCtype:
        """Determine Cmap 'CType' from input regmap node

        Args:
            input_regmap (InputRegmap): InputRegmap node

        Raises:
            InputJsonParserError: Type of input regmap is not supported

        Returns:
            CmapCtype: Corresponding Cmap type
        """
        ctype = None
        if input_regmap.type in InputType.CTYPE_UNSIGNED_CHAR and input_regmap.byte_size == 1:
            ctype = CmapCtype.UINT8
        elif input_regmap.type in InputType.CTYPE_UNSIGNED_SHORT and input_regmap.byte_size == 2:
            ctype = CmapCtype.UINT16
        elif input_regmap.type in InputType.CTYPE_UNSIGNED_INT and input_regmap.byte_size == 4:
            ctype = CmapCtype.UINT32
        elif input_regmap.type in InputType.CTYPE_UNSIGNED_LONG and input_regmap.byte_size == 4:
            ctype = CmapCtype.UINT32
        elif input_regmap.type in InputType.CTYPE_SIGNED_CHAR and input_regmap.byte_size == 1:
            ctype = CmapCtype.INT8
        elif input_regmap.type in InputType.CTYPE_SIGNED_SHORT and input_regmap.byte_size == 2:
            ctype = CmapCtype.INT16
        elif input_regmap.type in InputType.CTYPE_SIGNED_INT and input_regmap.byte_size == 4:
            ctype = CmapCtype.INT32
        elif input_regmap.type in InputType.CTYPE_SIGNED_LONG and input_regmap.byte_size == 4:
            ctype = CmapCtype.INT32
        elif input_regmap.type in InputType.FLOAT and input_regmap.byte_size == 4:
            ctype = CmapCtype.FLOAT
        else:
            raise InputJsonParserError("Input json type does not match byte size")
        return ctype

    @ staticmethod
    def _cmap_register_or_struct_from_input_regmap(parent: CmapRegisterOrStruct,
                                                   input_regmap: InputRegmap,
                                                   input_regmap_by_name: Dict[str, InputRegmap],
                                                   input_enum_by_name: Dict[str, InputEnum],
                                                   context: _CmapContext
                                                   ) -> Optional[CmapRegisterOrStruct]:
        """Construct Cmap 'RegisterOrStruct' ... this may be called recursively

        Args:
            parent (CmapRegisterOrStruct): Parent cmap node for the register/struct to be created
            input_regmap (InputRegmap): Input regmap node of the register/struct to be created
            input_regmap_by_name (Dict[str, InputEnum]): Top-level input regmap nodes indexed by names
            input_enum_by_name (Dict[str, InputEnum]): Set of enum definitions indexed by name
            context (_CmapContext): Context object provided information about nested arrays, etc...

        Raises:
            TahiniCmapError: The input regmap node could not be converted into a cmap node

        Returns:
            Optional[CmapRegisterOrStruct]: CmapRegisterOrStruct or None if nothing should be added
                                            to the cmapsource file
        """
        with context:
            # Skip any register or struct that has the visibility option "none"
            if input_regmap.access == VisibilityOptions.NONE:
                return None

            child = CmapRegisterOrStruct(name="temp", type=CmapType.STRUCT, addr=0, size=0, brief=None,
                                         offset=0, access=None, hif_access=None, repeat_for=None,
                                         namespace=None, struct=CmapStruct(children=[]), register=None)

            if input_regmap.byte_offset is not None:
                child.offset = input_regmap.byte_offset
                child.addr = parent.addr + input_regmap.byte_offset
            elif input_regmap.address is not None:
                child.offset = 0
                child.addr = input_regmap.address
            else:
                # Ignore elements for which we can't find any address
                return None

            # If the keyword `cref` is present, then we need to use a different input regmap
            if input_regmap.cref:
                if input_regmap.cref not in input_regmap_by_name:
                    raise TahiniCmapError(
                        f"The 'cref' keyword was used in the register or struct '{input_regmap.name}', "
                        f"but the referenced regmap member '{input_regmap.cref}' is not present in the regmap.")
                if input_regmap_by_name[input_regmap.cref].get_array_size() > input_regmap.get_array_size():
                    raise TahiniCmapError(
                        f"The size of '{input_regmap.name}' is '{input_regmap.byte_size}' bytes, which is smaller than "
                        f"'{input_regmap.cref}' which is '{input_regmap_by_name[input_regmap.cref].byte_size}' bytes")
                input_regmap = input_regmap_by_name[input_regmap.cref]

            if input_regmap.access is not None:
                # Specified value
                child.access = CmapVisibilityOptions.from_input_enum(input_regmap.access)
            elif parent is not None:
                # Inherited value
                child.access = parent.access
            else:
                # Default value
                child.access = CmapVisibilityOptions.PRIVATE

            if input_regmap.hif_access is not None:
                # Specified value
                child.hif_access = input_regmap.hif_access
            elif parent is not None:
                # Inherited value
                child.hif_access = parent.hif_access
            else:
                # Default value
                child.hif_access = False

            child.name = input_regmap.get_cmap_name()
            child.size = input_regmap.byte_size
            child.brief = input_regmap.brief
            child.namespace = input_regmap.namespace

            # Register or struct is an array?
            context.add_index(TahiniCmap._cmap_repeat_for_from_input_regmap(input_regmap, input_enum_by_name))

            child.repeat_for = context.get_indexes()

            if input_regmap.type not in InputType.STRUCT_OR_UNION:
                child.type = CmapType.REGISTER
                child.register = CmapRegister(
                    ctype=TahiniCmap._cmap_ctype_from_input_regmap(input_regmap),
                    format=input_regmap.format,
                    min=input_regmap.min,
                    max=input_regmap.max,
                    units=input_regmap.units,
                    bitfields=TahiniCmap._cmap_bitfields_from_input_regmap(input_regmap, input_enum_by_name),
                    states=TahiniCmap._cmap_states_from_input_regmap(input_regmap, input_enum_by_name))
                child.struct = None
            elif input_regmap.type in InputType.STRUCT:
                for next_data in input_regmap.members:
                    new_child = TahiniCmap._cmap_register_or_struct_from_input_regmap(
                        child, next_data, input_regmap_by_name, input_enum_by_name, context)
                    if new_child is not None:
                        child.struct.children.append(new_child)
            else:
                raise TahiniCmapError(f"Error: could not parse regmap input of type: {input_regmap.type}")

            return child

    @ staticmethod
    def cmap_regmap_from_input_json(input_json: InputJson) -> CmapRegmap:
        """Create a 'CMap Source' object from an 'Input JSON' object

        Args:
            input_json (InputJson): Input json object to be converted

        Raises:
            InputJsonParserError: Invalid data in Input Json file
            TahiniCmapError: Input Json file could not be converted into a Cmap file

        Returns:
            CmapRegmap: Cmap object created
        """
        try:
            context = _CmapContext()

            # Create dictionary to find input_enum by name
            input_enum_by_name = {}
            for input_enum in input_json.enums:
                input_enum_by_name[input_enum.name] = TahiniCmap._remove_enum_prefix(input_enum)

            # Create dictionary to find input_regmap by name
            input_regmap_by_name = {}
            for input_regmap in input_json.regmap:
                input_regmap_by_name[input_regmap.name] = input_regmap

            obj = CmapRegmap(children=[])
            for current_data in input_json.regmap:
                new_child = TahiniCmap._cmap_register_or_struct_from_input_regmap(
                    None, current_data, input_regmap_by_name, input_enum_by_name, context)
                if new_child is not None:
                    obj.children.append(new_child)

            # Sort all elements by address
            obj.children.sort(key=lambda reg_or_struct: reg_or_struct.addr)

            return obj

        except marshmallow.exceptions.ValidationError as exc:
            raise InputJsonParserError(str(exc) + " Invalid value in input json") from exc
        except Exception as exc:
            raise TahiniCmapError("Unable to convert from input json file to cmapsource file") from exc

    @ staticmethod
    def cmap_regmap_from_input_json_path(path: str) -> CmapRegmap:
        """Create a 'Cmap Regmap' object from an 'Input JSON' file path

        Args:
            path (str): Input json file path

        Returns:
            CmapRegmap: CMap regmap object generated
        """
        return TahiniCmap.cmap_regmap_from_input_json(InputJson.load_json(path))

    @ staticmethod
    def cmap_fullregmap_from_input_json_path(input_json_path: str,
                                             version_info_path: (Optional[str]) = None,
                                             project_path: Optional[str] = None,
                                             extended_version_info_path: Optional[str] = None
                                             ) -> CmapFullRegmap:
        """Create a 'Cmap FullRegmap' object from an 'Input JSON' file

        Args:
            input_json_path (str): Path to the input json file
            version_info_path (str, optional): Specify version info file.
            project_path (str, optional): Path of the git repository. Only required if version_info_path is used.
            extended_version_info_path (str, optional): Use an extended version info file.

        Returns:
            CmapFullRegmap: Full cmap regmap
        """
        return TahiniCmap.cmap_fullregmap_from_input_json(
            input_json=InputJson.load_json(input_json_path),
            version_info_path=version_info_path,
            project_path=project_path,
            extended_version_info_path=extended_version_info_path)

    @ staticmethod
    def cmap_fullregmap_from_input_json(input_json: InputJson,
                                        version_info_path: (Optional[str]) = None,
                                        project_path: Optional[str] = None,
                                        extended_version_info_path: Optional[str] = None
                                        ) -> CmapFullRegmap:
        """Create a 'Cmap FullRegmap' object from an 'Input JSON' file

        Args:
            input_json (InputJson): InputJson object
            version_info_path (str, optional): Specify version info file.
            project_path (str, optional): Path of the git repository. Only required if version_info_path is used.
            extended_version_info_path (str, optional): Use an extended version info file.

        Returns:
            CmapFullRegmap: Full cmap regmap
        """
        assert (extended_version_info_path is not None or version_info_path is not None),\
            "Error: version_info_path or extended_version_info_path must be specified"

        if extended_version_info_path is not None:
            cmap = CmapFullRegmap(
                scheme=CmapScheme(1, 0),
                version=ExtendedVersionInfo.load_json(extended_version_info_path),
                regmap=TahiniCmap.cmap_regmap_from_input_json(input_json)
            )
        else:
            assert project_path is not None, "Error: version_info_path was specified but not project_path"
            cmap = CmapFullRegmap(
                scheme=CmapScheme(1, 0),
                version=TahiniVersion.create_extended_version_info(project_path, version_info_path),
                regmap=TahiniCmap.cmap_regmap_from_input_json(input_json)
            )

        return cmap
