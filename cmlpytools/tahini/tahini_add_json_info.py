"""
This file contains methods to add json information, such as Cref, briefs... to the gimli generated 
input json file from the compiled code
"""

from typing import Union, Optional
from .input_json_schema import InputJson, InputRegmap, InputEnum

class ConflictingFieldsError(Exception):
    """Class used to handle errors for conflicting fields
    """
    pass

class ObjectNotFoundError(Exception):
    """Class used to handle errors for json objects missing
    """
    pass

class TahiniAddJsonInfo:
    """Class contains the necessary definitions to combine 2 input json files
    """
    @staticmethod
    def combine_json_files(input_json_path: str, additional_json_path: str) -> InputJson:
        """Combine input json file with additional one including extra documentation
        """

        assert input_json_path is not None, "Error: input_json_path must be specified"
        assert additional_json_path is not None, "Error: additional_json_path must be specified"

        input_json_obj = InputJson.load_json(input_json_path)
        additional_json_obj = InputJson.load_json(additional_json_path)

        if additional_json_obj.regmap[0].name != "None": # Nothing to add
            for additional_regmap_obj in additional_json_obj.regmap:
                object_found = TahiniAddJsonInfo.combine_regmap(input_json_obj.regmap, additional_regmap_obj)
                if object_found is False:
                    raise ObjectNotFoundError(f"Object with name {additional_regmap_obj.name} specified in the "
                        "additional json file was not found in the input json regmap")

        if additional_json_obj.enums[0].name != "None": # Nothing to add
            for additional_enum in additional_json_obj.enums:
                object_found = TahiniAddJsonInfo.combine_enums(input_json_obj.enums, additional_enum)
                if object_found is False:
                    raise ObjectNotFoundError(f"Object with name {additional_enum.name} specified in the additional "
                        "json file was not found in the input json enums")

        return input_json_obj


    @staticmethod
    def combine_regmap(input_json_regmap: list[InputRegmap], additional_regmap_obj: InputRegmap) -> bool:
        """ Adds additonal information from extra json regmap entries to input json file 
        """
        object_found = False
        if additional_regmap_obj.type != "struct":
            for obj in input_json_regmap:
                if obj.type != "struct":
                    if obj.get_cmap_name() == additional_regmap_obj.get_cmap_name():
                        object_found = True
                        # Replace fields in object with ones from additional json object
                        TahiniAddJsonInfo.replace_fields(obj, additional_regmap_obj, None)
                        break
                # Search for json object inside struct
                elif TahiniAddJsonInfo.combine_regmap(obj.members, additional_regmap_obj) is True:
                    object_found = True
        else:
            for input_json_obj in input_json_regmap:
                if input_json_obj.get_cmap_name() == additional_regmap_obj.get_cmap_name():
                    # Add additional fields in struct except members
                    TahiniAddJsonInfo.replace_fields(input_json_obj, additional_regmap_obj, "members")
                    object_found = True
                    # Add information from members inside struct
                    for sub_additional_regmap in additional_regmap_obj.members:
                        if sub_additional_regmap.name != "None" and not\
                            TahiniAddJsonInfo.combine_regmap(input_json_obj.members, sub_additional_regmap):
                            raise ObjectNotFoundError(f"Object with name {sub_additional_regmap.name} specified"
                                " in the additional json file was not found in the input json regmap")
                    break
                if input_json_obj.type == "struct":
                    # Look for struct inside struct to replace variables and members
                    if TahiniAddJsonInfo.combine_regmap(input_json_obj.members, additional_regmap_obj):
                        object_found = True
        return object_found

    @staticmethod
    def combine_enums(input_json_enums: list[InputEnum], additional_enum: InputEnum) -> bool:
        """ Adds additonal information from extra json enum entries to input json file 
        """
        object_found = False
        if isinstance(additional_enum, InputEnum.InputEnumChild):
            for obj in input_json_enums:
                if isinstance(obj, InputEnum.InputEnumChild):
                    if obj.name == additional_enum.name:
                        object_found = True
                        # Replace fields in object with ones from additional json object
                        TahiniAddJsonInfo.replace_fields(obj, additional_enum, None)
                        break
                elif TahiniAddJsonInfo.combine_enums(obj.enumerators, additional_enum):
                    object_found = True
        else:
            # If not enumChild, replace fields and then add information of enumerators within
            for input_json_enum in input_json_enums:
                if input_json_enum.name == additional_enum.name:
                    # Replace fields
                    TahiniAddJsonInfo.replace_fields(input_json_enum, additional_enum, "enumerators")
                    object_found = True
                    # Add information from enumerators inside enum
                    for sub_additional_enum in additional_enum.enumerators:
                        if sub_additional_enum != "None" and not\
                            TahiniAddJsonInfo.combine_enums(input_json_enum.enumerators, sub_additional_enum):
                            raise ObjectNotFoundError(f"Object with name {sub_additional_enum.name} specified in"
                                " the additional json file was not found in the input json enums")
                    break
                if isinstance(input_json_enum, InputEnum.InputEnumChild) is False:
                    # Look inside enumerator to replace variables
                    if TahiniAddJsonInfo.combine_enums(input_json_enum.enumerators, additional_enum):
                        object_found = True
        return object_found

    @staticmethod
    def replace_fields(input_json_obj: Union[InputRegmap, InputEnum],
        additional_obj: Union[InputRegmap, InputEnum.InputEnumChild], not_to_replace: Optional[str]):
        """ Replaces fields in corresponding object in input_json_file
        """
        for variable in vars(additional_obj):
            additional_obj_attr = getattr(additional_obj, variable)
            input_json_obj_attr = getattr(input_json_obj, variable)
            if additional_obj_attr is not None and variable != not_to_replace:
                if input_json_obj_attr is not None and variable != "brief":
                    # Check if fields are equal, otherwise throw an error
                    if additional_obj_attr != input_json_obj_attr:
                        raise ConflictingFieldsError(f"Field \"{variable}\": \"{additional_obj_attr}\" from"
                            f" additional json object {additional_obj.name} doesn't match the existing one"
                            f"\"{variable}\":\"{input_json_obj_attr}\"")
                else:
                    setattr(input_json_obj, variable, additional_obj_attr)
