"""
This file is intended to add json information to the gimli generated json file from the compiled code,
"""

import sys
from typing import Union, Optional
from input_json_schema import InputJson, InputRegmap, InputEnum

class ConflictingFieldsError(Exception):
    """Class used to handle errors for conflicting fields
    """
    pass

class CombineJsonFiles:
    """Class contains the necessary definitions to combine 2 input json files
    """
    @staticmethod
    def combine_json_files(input_json_path: str, additional_json_path: str, combined_json_path: str):
        """Combine input json file with additional one including extra documentation
        """

        assert (input_json_path is not None or additional_json_path is not None),\
            "Error: input_json_path or additional_json_path must be specified"

        input_json_obj = InputJson.load_json(input_json_path)
        additional_json_obj = InputJson.load_json(additional_json_path)

        for additional_regmap_obj in additional_json_obj.regmap:
            CombineJsonFiles.combine_regmap(input_json_obj.regmap, additional_regmap_obj)

        if additional_json_obj.enums[0].name != "None": # Nothing to add
            for additional_enum in additional_json_obj.enums:
                CombineJsonFiles.combine_enums(input_json_obj.enums, additional_enum)

        #last step: output json file after converting it back
        combined_json = input_json_obj.to_json(indent=4)

        stdout = sys.stdout
        if combined_json_path is not None:
            sys.stdout = open(combined_json_path, "w", encoding="UTF-8")
            sys.stdout.write(combined_json)
            sys.stdout.close()
            sys.stdout = stdout

    @staticmethod
    def combine_regmap(input_json_regmap: list[InputRegmap], additional_regmap_obj: InputRegmap):
        """ Adds additonal information from extra json regmap entries to input json file 
        """
        if additional_regmap_obj.type != "struct":
            for idx, obj in enumerate(input_json_regmap):
                if obj.type != "struct":
                    if obj.get_cmap_name() == additional_regmap_obj.get_cmap_name():
                        # Replace fields in object with ones from additional json object
                        CombineJsonFiles.replace_fields(obj, additional_regmap_obj, None)
                        break
                else:
                    # Search for json object inside struct
                    CombineJsonFiles.combine_regmap(input_json_regmap[idx].members, additional_regmap_obj)
        else:
            for input_json_obj in input_json_regmap:
                if input_json_obj.get_cmap_name() == additional_regmap_obj.get_cmap_name():
                    # Replace variables in struct with additional fields except members
                    CombineJsonFiles.replace_fields(input_json_obj, additional_regmap_obj, "members")
                    # Add information from members inside struct
                    for sub_additional_regmap_obj in additional_regmap_obj.members:
                        CombineJsonFiles.combine_regmap(input_json_obj.members, sub_additional_regmap_obj)
                    break
                if input_json_obj.type == "struct":
                    # Look for struct inside struct to replace variables and members
                    CombineJsonFiles.combine_regmap(input_json_obj.members, additional_regmap_obj)

    @staticmethod
    def combine_enums(input_json_enums: list[InputEnum], additional_enum: InputEnum):
        """ Adds additonal information from extra json enum entries to input json file 
        """
        if isinstance(additional_enum, InputEnum.InputEnumChild):
            for idx, obj in enumerate(input_json_enums):
                if isinstance(obj, InputEnum.InputEnumChild):
                    if obj.name == additional_enum.name:
                        # Replace fields in object with ones from additional json object
                        CombineJsonFiles.replace_fields(obj, additional_enum, None)
                        break
                else:
                    CombineJsonFiles.combine_enums(input_json_enums[idx].enumerators, additional_enum)
        else:
            # If not enumChild, replace fields and then add information of enumerators within
            for input_json_enum in input_json_enums:
                if input_json_enum.name == additional_enum.name:
                    # Replace fields
                    CombineJsonFiles.replace_fields(input_json_enum, additional_enum, "enumerators")
                    # Add information from enumerators inside enum
                    for sub_additional_enum in additional_enum.enumerators:
                        CombineJsonFiles.combine_enums(input_json_enum.enumerators, sub_additional_enum)
                    break
                if isinstance(input_json_enum, InputEnum.InputEnumChild) is False:
                    # Look inside enumerator to replace variables
                    CombineJsonFiles.combine_enums(input_json_enum.enumerators, additional_enum)

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
