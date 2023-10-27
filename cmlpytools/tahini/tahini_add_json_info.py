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

        for additional_regmap_object in additional_json_obj.regmap:
            input_json_obj = CombineJsonFiles.replace_regmap_fields(input_json_obj, additional_regmap_object)

        if additional_json_obj.enums[0].name != "None":
            for additional_enum_object in additional_json_obj.enums:
                input_json_obj = CombineJsonFiles.replace_enum_fields(input_json_obj, additional_enum_object)

        #struct needs to be supported too

        #last step: output json file after converting it back
        combined_json = input_json_obj.to_json(indent=4)

        output_path_trial = os.path.join(os.getcwd(), "json_try_output.json")

        stdout = sys.stdout
        if output_path_trial is not None:
            sys.stdout = open(output_path_trial, "w", encoding="UTF-8")

        # probs delete everything that is currently there in this step

            sys.stdout.write(combined_json)

            sys.stdout.close()
            sys.stdout = stdout

    @staticmethod
    def replace_regmap_fields(input_json_obj: InputJson, additional_regmap_object: InputRegmap) -> InputJson:
        """ Finds corresponding object in input json file regmap and replaces fields
        """

        for idx, obj in enumerate(input_json_obj.regmap):
            if obj.get_cmap_name() == additional_regmap_object.get_cmap_name():
                input_json_obj.regmap[idx] = additional_regmap_object
                break
        return input_json_obj

    @staticmethod
    def replace_enum_fields(input_json_obj: InputJson, additional_enum_object: InputEnum) -> InputJson:
        """ Finds corresponding object in input json file enums and replaces fields
        """

        for idx, obj in enumerate(input_json_obj.regmap):
            if obj.name == additional_enum_object.name:
                input_json_obj.enums[idx] = additional_enum_object
                break
        return input_json_obj
    