"""
RegmapCfgMergeFile class for merging config files with different namespaces
"""
from builtins import range
import json
from operator import itemgetter
from cmlpytools import tahini
from .shared import RegmapFileWriter
from .file_types import FileTypes
from .file_base import FileBase
import os

def attach_namespace(data_list, namespace):
    """
    A function to add namespace to every register in the dict
    
    Args:
        data_list (str): a dict that contains the register data section of a config file
        namespace (str): namespace to add
    """
    for register in data_list:
        register['namespace'] = namespace
    return data_list

class RegmapCfgMergeFile(object):
    """
    Class used to create merge regmap parameter files together
    """
    def __init__(self, top_level_config: str, json_path: str, cmap_source: str):
        """ 
        Create a handle that can be used to merge together several regmap parameter files with
        different namespaces

        Args:
            top_level_config (str): a top level config file
            json_path (str): path to the cml json configs
        """
        with open(top_level_config, 'r', encoding="UTF-8") as f_cfg:
            tl_cfg_data = f_cfg.read()
        tl_json_data = json.loads(tl_cfg_data)

        cmap_full_regmap = tahini.CmapFullRegmap.load_json(cmap_source)

        if 'minfs' not in tl_json_data:
            raise Exception("minfs section is not found in the config file")

        if 'regmap_params' not in tl_json_data['minfs']:
            raise Exception("regmap_params section is not found in the minfs section")

        # Read the first config file
        params_full_path = os.path.join(json_path, 
                                        tl_json_data['minfs']['regmap_params'][0]['path'])
        with open(params_full_path, 'r', encoding="UTF-8") as f_cfg:
            main_cfg_data = f_cfg.read()

        # Parse the regmap file and the config file
        self._main_json_data = json.loads(main_cfg_data)

        # Get the struct file parameter of the first config file
        if "struct" in self._main_json_data:
            config_struct = self._main_json_data['struct']
        else:
            config_struct = None

        # get the namesapce of the first config file
        first_ns = tl_json_data['minfs']['regmap_params'][0]['namespace']

        # extract common registers from the config file
        common_regs = []
        for register in self._main_json_data['data']:
            match = tahini.search(name=register['register'], cmap_type=tahini.CmapType.REGISTER, 
                                  node=cmap_full_regmap)
            if not match.result.namespace:
                common_regs.append(register)
        for register in common_regs:
            if register in self._main_json_data['data']:
                self._main_json_data['data'].remove(register)

        # Add the namespace to the first config file
        self._main_json_data['data'] = attach_namespace(self._main_json_data['data'], first_ns)

        # Process all the subsequent config files
        if len(tl_json_data['minfs']['regmap_params']) > 1:
            for config_file in tl_json_data['minfs']['regmap_params'][1:]:
                config_file_path = os.path.join(json_path, config_file['path'])
                with open(config_file_path, 'r', encoding="UTF-8") as f_cfg:
                    cfg_data = f_cfg.read()
                json_data = json.loads(cfg_data)

                # Check if the struct parameter equals to the struct parameter of the first file
                if 'struct' in json_data:
                    if json_data['struct'] != config_struct:
                        raise Exception("It is only possible to merge configs with the same offset")
                else:
                    if config_struct is not None:
                        raise Exception("It is only possible to merge configs with the same offset")

                # extract common registers and compare them to the common registers of the registers that are
                # already in the common registers list.
                for register in json_data['data']:
                    match = tahini.search(name=register['register'], cmap_type=tahini.CmapType.REGISTER, 
                                          node=cmap_full_regmap)
                    if not match.result.namespace:
                        register_found = 0
                        for common_reg in common_regs:
                            if register['register'] == common_reg['register']:
                                if register['value'] != common_reg['value']:
                                    raise Exception("Common register in config files contain different values")
                                register_found = 1
                                break
                        if register_found == 0:
                            common_regs.append(register)
                for register in common_regs:
                    if register in json_data['data']:
                        json_data['data'].remove(register)

                # attach namespace to the registers
                namespace = config_file['namespace']
                self._main_json_data['data'].extend(attach_namespace(json_data['data'], namespace))

        # append the common registers to the end of the file
        self._main_json_data['data'].extend(common_regs)

    @property
    def merged_json(self) -> dict:
        return self._main_json_data