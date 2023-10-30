"""
This file is inteded to add json information to the gimli generated json file from the compiled code,
"""

import sys
import os
from input_json_schema import InputJson, InputRegmap, InputEnum

class CombineJsonFiles:
    """Class contains the necessary definitions to combine 2 input json files
    """
    @staticmethod
    def combine_json_files(input_json_path: str, additional_json_path: str):
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

        output_path_trial = os.path.join(os.getcwd(), "json_try_output.json")

        stdout = sys.stdout
        if output_path_trial is not None:
            sys.stdout = open(output_path_trial, "w", encoding="UTF-8")
            sys.stdout.write(combined_json)
            sys.stdout.close()
            sys.stdout = stdout

    @staticmethod
    def combine_regmap(input_json_regmap: list[InputRegmap], additional_regmap_obj: InputRegmap):
        """ Adds additonal information from extra json file to input json file 
        """
        if additional_regmap_obj.type != "struct":
            CombineJsonFiles.replace_regmap_fields(input_json_regmap, additional_regmap_obj)
        else:
            for input_json_obj in input_json_regmap:
                if input_json_obj.get_cmap_name() == additional_regmap_obj.get_cmap_name():
                    # Replace variables in struct with additional fields except members
                    for variable in vars(additional_regmap_obj):
                        if variable != "members":
                            setattr(input_json_obj, variable, getattr(additional_regmap_obj, variable))
                    # Add information from members inside struct
                    for sub_additional_regmap_obj in additional_regmap_obj.members:
                        CombineJsonFiles.combine_regmap(input_json_obj.members, sub_additional_regmap_obj)
                    break
                if input_json_obj.type == "struct":
                    # Look for struct inside struct to replace variables and members
                    CombineJsonFiles.combine_regmap(input_json_obj.members, additional_regmap_obj)

    @staticmethod
    def replace_regmap_fields(input_json_obj: list[InputRegmap], additional_regmap_object: InputRegmap):
        """ Finds corresponding object in input json file regmap and replaces fields
        """
        for idx, obj in enumerate(input_json_obj):
            if obj.type != "struct":
                if obj.get_cmap_name() == additional_regmap_object.get_cmap_name():
                    input_json_obj[idx] = additional_regmap_object
                    break
            else:
                CombineJsonFiles.replace_regmap_fields(input_json_obj[idx].members, additional_regmap_object)

    @staticmethod
    def combine_enums(input_json_enums: list[InputEnum], additional_enum: InputEnum):
        """ Finds corresponding object in input json file enums and replaces fields
        """
        if isinstance(additional_enum, InputEnum.InputEnumChild):
            CombineJsonFiles.replace_enum_child_fields(input_json_enums, additional_enum)
        else:
            # If not enumChild, replace fields and then add information of enumerators within
            for input_json_enum in input_json_enums:
                if input_json_enum.name == additional_enum.name:
                    # Replace fields
                    for variable in vars(additional_enum):
                        if variable != "enumerators":
                            setattr(input_json_enum, variable, getattr(additional_enum, variable))
                    # Add information from enumerators inside enum
                    for sub_additional_enum in additional_enum.enumerators:
                        CombineJsonFiles.combine_enums(input_json_enum.enumerators, sub_additional_enum)
                    break
                if isinstance(input_json_enum, InputEnum.InputEnumChild) is False:
                    # Look inside enumerator to replace variables
                    CombineJsonFiles.combine_enums(input_json_enum.enumerators, additional_enum)

    @staticmethod
    def replace_enum_child_fields(input_json_obj: list[InputEnum], additional_enum_obj: InputEnum.InputEnumChild):
        """ Finds corresponding object in input json file enums and replaces fields
        """

        for idx, obj in enumerate(input_json_obj):
            if isinstance(obj, InputEnum.InputEnumChild):
                if obj.name == additional_enum_obj.name:
                    input_json_obj[idx] = additional_enum_obj
                    break
            else:
                CombineJsonFiles.replace_enum_fields(input_json_obj[idx].enumerators, additional_enum_obj)
