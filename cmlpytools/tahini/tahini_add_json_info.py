"""
This file is inteded to add json information to the gimli generated json file from the compiled code,
"""

import sys
import os
from input_json_schema import InputJson, InputRegmap

class CombineJsonFiles:
    """Class contains the necessary definitions to combine 2 input json files
    """
    @staticmethod
    def import_json_files(input_json_path: str, additional_json_path: str):
        """Import json files to be combined
        """

        assert (input_json_path is not None or additional_json_path is not None),\
           "Error: input_json_path or additional_json_path must be specified"
        
        input_json_obj = InputJson.load_json(input_json_path)
        additional_json_obj = InputJson.load_json(additional_json_path)

        for additional_regmap_object in additional_json_obj.regmap:
            input_json_obj = CombineJsonFiles.find_and_replace_fields(input_json_obj, additional_regmap_object)

        #struct needs to be supported too

        #last step: output json file after converting it back
        combined_json = additional_json_obj.to_json(indent=4)

        output_path_trial = os.path.join(os.getcwd(), "json_try_output.json")

        stdout = sys.stdout
        if output_path_trial is not None:
            sys.stdout = open(output_path_trial, "w", encoding="UTF-8")

        # probs delete everything that is currently there in this step

            sys.stdout.write(combined_json)

            sys.stdout.close()
            sys.stdout = stdout

    @staticmethod
    def find_and_replace_fields(input_json_obj: InputJson, additional_regmap_object: InputRegmap) -> list[InputRegmap]:
        """ Finds corresponding object in input json file and replaces fields
        """

        for idx, obj in enumerate(input_json_obj.regmap):
            if obj.get_cmap_name() == additional_regmap_object.get_cmap_name():
                input_json_obj.regmap[idx] = additional_regmap_object
                break
        return input_json_obj