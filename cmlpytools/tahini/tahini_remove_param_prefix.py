"""
This file implements a method to remove the Param prefix from the Rumba s10 registers
"""

import re
from .input_json_schema import InputJson, InputRegmap

class TahiniRemoveParamPrefix:
    """Class contains the necessary definitions to implement intended function
    """
    @staticmethod
    def remove_param_prefix(input_json_path: str) -> InputJson:
        """Remove Param prefix from registers

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
        """ Removes Param prefix from registers

        Args:
            input_json_reg (InputRegmap): InputRegmap object to remove Param prefix from
        """
        if input_json_reg.type != "struct":
            if re.match("Param",input_json_reg.name) is not None:
                input_json_reg.name = input_json_reg.name[5:]

        else:
            if re.match("Param",input_json_reg.name) is not None:
                input_json_reg.name = input_json_reg.name[5:]
            for reg in input_json_reg.members:
                TahiniRemoveParamPrefix.remove_reg_param_prefix(reg)
