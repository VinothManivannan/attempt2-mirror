"""
This file contains methods to add json information, such as Cref, briefs... to the gimli generated 
input json file from the compiled code
"""

import re
from .input_json_schema import InputJson, InputRegmap

class TahiniRemoveParamPrefix:
    """Class contains the necessary definitions to combine 2 input json files
    """
    @staticmethod
    def remove_param_prefix(input_json_path: str) -> InputJson:
        """Combine input json file with additional one including extra documentation

        Args:
            input_json_path (str): gimli generated input json

        Returns:
            InputJson: InputJson object containing the combined json regmap information
        """

        assert input_json_path is not None, "Error: input_json_path must be specified"

        input_json_obj = InputJson.load_json(input_json_path)

        if input_json_obj.regmap[0].name != "None": # Nothing to add
            for input_json_reg in input_json_obj.regmap:
                TahiniRemoveParamPrefix.remove_reg_param_prefix(input_json_reg)

        return input_json_obj


    @staticmethod
    def remove_reg_param_prefix(input_json_reg: InputRegmap):
        """ Adds additonal information from extra json regmap entries to input json file 

        Args:
            input_json_reg (InputRegmap): InputRegmap object from which information is to be added
        """
        if input_json_reg.type != "struct":
            if (re.match(r"Param*",input_json_reg.name) is not None):
                input_json_reg.name = input_json_reg.name[5:]

        else:
            if (re.match(r"Param*",input_json_reg.name) is not None):
                input_json_reg.name = input_json_reg.name[5:]
            for reg in input_json_reg.members:
                TahiniRemoveParamPrefix.remove_reg_param_prefix(reg)
