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
    def __init__(self, top_level_config: str, json_path: str):
        """ 
        Create a handle that can be used to merge together several regmap parameter file with
        different namespaces

        Args:
            top_level_config (str): a top level config file
            json_path (str): path to the cml json configs
        """
        with open(top_level_config, 'r', encoding="UTF-8") as f_cfg:
            tl_cfg_data = f_cfg.read()
        tl_json_data = json.loads(tl_cfg_data)

        if 'minfs' not in tl_json_data:
            raise Exception("minfs section is not found in the config file")

        if 'regmap_params' not in tl_json_data['minfs']:
            raise Exception("regmap_params section is not found in the minfs section")

        params_full_path = os.path.join(json_path, 
                                        tl_json_data['minfs']['regmap_params'][0]['path'])
        with open(params_full_path, 'r', encoding="UTF-8") as f_cfg:
            main_cfg_data = f_cfg.read()

        # Parse the regmap file and the config file
        self._main_json_data = json.loads(main_cfg_data)
        if "struct" in self._main_json_data:
            config_struct = self._main_json_data['struct']
        else:
            config_struct = None

        first_ns = tl_json_data['minfs']['regmap_params']['namespace']

        self._main_json_data['data'] = attach_namespace(self._main_json_data['data'], first_ns)

        if len(tl_json_data['minfs']['regmap_params']) >1:
            for config_file in tl_json_data['minfs']['regmap_params'][1:]:
                with open(config_file['path'], 'r', encoding="UTF-8") as f_cfg:
                    cfg_data = f_cfg.read()
                json_data = json.loads(cfg_data)

                if 'struct' in json_data:
                    if json_data['struct'] != config_struct:
                        raise Exception("It is only possible to merge configs with the same offset")

                namespace = tl_json_data['minfs']['regmap_params']['namespace']
                self._main_json_data['data'].append(attach_namespace(json_data['data'],namespace))

    @property
    def merged_json(self) -> dict:
        return self._main_json_data