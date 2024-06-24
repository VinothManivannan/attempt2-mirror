"""Implement functions used to import files from the legacy json format and convert to C header text
"""
from string import Template
from re import sub
import json
import os
import datetime
from typing import Any, Dict, List
from .legacy_json_converter import legacy_json_to_input_regmap
from .input_json_schema import InputJson, InputRegmap, InputEnum

C_HEADER_BOILERPLATE = \
"""/***************************************************************************************************
 * @copyright Copyright (C) ${year} Cambridge Mechatronics Ltd. All rights reserved.
 * @par Disclaimer
 * This software is supplied by Cambridge Mechatronics Ltd. (CML) and is only intended for use with
 * CML products. No other uses are authorized. This software is owned by Cambridge Mechatronics Ltd.
 * and is protected under all applicable laws, including copyright laws.
 **************************************************************************************************/

#ifndef __${unique_header_name}_AUTO_H__
#define __${unique_header_name}_AUTO_H__
"""

CPP_IFDEF = """
#ifdef __cplusplus
extern "C" {
#endif
"""

INCLUDES_TITLE = """
/***************************************************************************************************
* Includes
***************************************************************************************************/
#include "tahini.h"
#include "caef_types.h"
"""

CONSTANTS_TYPES_TITLE = """
/***************************************************************************************************
* Constants & Type Definitions
***************************************************************************************************/
"""

C_HEADER_ENDIF = \
"""#ifdef __cplusplus
}
#endif

#endif /* __${unique_header_name}_AUTO_H__ */"""

def _camel_case(text: str) -> str:
    """Convert a string to CamelCase

    Args:
        text (str): String to be converted

    Returns:
        str: string in CamelCase
    """
    text = sub(r"(_|-)+", " ", text).title().replace(" ", "")
    return ''.join([text[0].upper(), text[1:]])


def _snake_case(text: str) -> str:
    """Convert a string to snake_case

    Args:
        text (str): String to be converted

    Returns:
        str: string in snake_case
    """
    return sub(r'(?<!^)(?=[A-Z])', '_', text).lower()


def _extract_constants(const_value: Dict, description: str, const_type: str = None) -> str:
    """Extract constant values and convert to C header text 

    Args:
        const_value (Dict): A dictionary that describes the constant values
        description (str): A text description of the CAEF component, to be used when appending to certain #defs
        const_type (str): A string to decribe the type of constant

    Returns:
        str: C header text
    """
    header_text: str = ""

    num_items = len(const_value.items())
    mykeys = list(const_value.keys())
    myvalues = list(const_value.values())
    for i in range(0, num_items):
        if const_type == "controlindexes":
            value = str(myvalues[i])
            prefix = description + "_"
        elif const_type == "controlspaces":
            value = str(len(myvalues[i]))
            prefix = description + "_"
        elif const_type == "initvalues":
            value = str(myvalues[i])
            prefix = ""
        else:
            # else case sets to empty string to satisfy the linter
            value = prefix = ""

        header_text += "#define " + prefix + mykeys[i].upper() + " " + value + "\n"

    return header_text


def _json_actuator_to_cheader(json_data: Any, description: str, header_contents: str) -> str:
    """Convert legacy json file containing a CAEF 'Actuator' into C header text

    Args:
        json_data (Any): Json data to be converted
        description (str): A text description of the CAEF component, to be used when appending to certain #defs
        header_contents (str): C header text

    Returns:
        str: C integer type
    """

    header_contents += "#include \"caef_module.h\"\n"
    header_contents += "#include \"caef_chain.h\"\n"

    # Find the top of the JSON for this actuator
    caef_actuator = json_data["Actuator"]
    caef_actuator = caef_actuator[next(iter(caef_actuator.keys()))]

    # Iterate throught the child nodes, performing two tasks:
    # - Add the required #includes
    # - Insert the top level public and private regmap structures for this actuator into a list
    actuator_struct_list: List = []
    for child in caef_actuator["children"]:
        if child[0] == "Chain":
            header_contents += "#include \"" + child[1].lower().replace(" ", "_") + ".h\"\n"
        elif child[0] == "Module":
            header_contents += "#include \"" + child[1].lower().replace(" ", "_") + ".h\"\n"
        elif child[0] == "Struct":
            actuator_struct_list.append(child[1])

    header_contents += CONSTANTS_TYPES_TITLE

    # Parse the top level public and private regmap structures after recursively parsing their member structures
    # pylint: disable=too-many-nested-blocks
    for actuator_struct_id in actuator_struct_list:
        caef_actuator_structs = json_data["Struct"][actuator_struct_id]

        for child in caef_actuator_structs["children"]:
            struct_name = _camel_case(child[1])
            header_contents += "struct " + struct_name + " {\n"
            struct_contents = json_data["Struct"][child[1]]["children"]
            for inner_struct_member in struct_contents:
                if inner_struct_member[0] == "Struct":
                    # Set up defaults, in case there is no lookup data in the JSON
                    inner_struct_ctype = _camel_case(inner_struct_member[1])
                    inner_struct_cname = inner_struct_member[1]
                    # Update data if there is lookup data in the JSON
                    if inner_struct_member[1] in json_data["Struct"]:
                        if "ctype" in json_data["Struct"][inner_struct_member[1]]:
                            inner_struct_ctype = json_data["Struct"][inner_struct_member[1]]["ctype"]
                        if "cname" in json_data["Struct"][inner_struct_member[1]]:
                            inner_struct_cname = json_data["Struct"][inner_struct_member[1]]["cname"]
                    header_contents += "    struct " + inner_struct_ctype + " " + inner_struct_cname + ";\n"
            header_contents += "};\ntypedef struct " + struct_name + " " + struct_name + ";\n\n"

        top_struct_name = _camel_case(actuator_struct_id)
        header_contents += "struct " + top_struct_name + " {\n"
        top_struct_contents = json_data["Struct"][actuator_struct_id]["children"]
        for top_struct_member in top_struct_contents:
            header_contents += "    struct " +  _camel_case(top_struct_member[1]) + " "
            header_contents += json_data["Struct"][top_struct_member[1]]["cname"] + ";\n"
        header_contents += "};\ntypedef struct " + top_struct_name + " " + top_struct_name + ";\n\n"


    if "controlindexes" in caef_actuator:
        header_contents += _extract_constants(caef_actuator["controlindexes"], description, const_type="controlindexes")

    if "controlspaces" in caef_actuator:
        header_contents += _extract_constants(caef_actuator["controlspaces"], description, const_type="controlspaces")

    return header_contents


def _json_chain_to_cheader(json_data: Any, description: str, header_contents: str) -> str:
    """Convert legacy json file containing a CAEF 'Chain' into C header text

    Args:
        json_data (Any): Json data to be converted
        description (str): A text description of the CAEF component, to be used when appending to certain #defs
        header_contents (str): C header text

    Returns:
        str: C header text
    """

    # Add additional includes for CAEF chain JSONs
    header_contents += "#include \"caef_module.h\"\n"
    header_contents += "#include \"caef_chain.h\"\n"

    # Find the top of the JSON for this chain
    caef_chain = json_data["Chain"]
    caef_chain = caef_chain[next(iter(caef_chain.keys()))]

    # Iterate throught the child nodes, adding the required #includes
    for child in caef_chain["children"]:
        if child[0] == "Module":
            header_contents += "#include \"" + child[1].lower().replace(" ", "_") + ".h\"\n"

    header_contents += CONSTANTS_TYPES_TITLE

    if "controlindexes" in caef_chain:
        header_contents += _extract_constants(caef_chain["controlindexes"], description, const_type="controlindexes")

    return header_contents


def _convert_integer_type(int_type: str) -> str:
    """Convert integer type description into C syntax

    Args:
        int_type (str): The integer type described in words

    Returns:
        str: C integer text
    """
    if int_type == "unsigned long":
        return "uint32_t"
    if int_type in {"signed long", "long"}:
        return "int32_t"
    if int_type == "unsigned short":
        return "uint16_t"
    if int_type in {"signed short", "short"}:
        return "int16_t"
    if int_type == "unsigned char":
        return "uint8_t"
    if int_type in {"signed char", "char"}:
        return "int8_t"

    return int_type


def _process_input_enum(input_enum: InputEnum) -> str:
    """Convert InputEnum into C header syntax

    Args:
        input_enum (InputEnum): The input enum

    Returns:
        str: C header text
    """
    header_text: str = ""

    header_text += "enum " + input_enum.name + " {\n"

    num_members = len(input_enum.enumerators)
    for i in range(0, num_members):
        member_fullname = input_enum.name + "_" + input_enum.enumerators[i].name
        header_text += "    " + member_fullname.upper() + " = " + str(input_enum.enumerators[i].value)
        if i < num_members-1:
            header_text += ","
        header_text += "\n"

    header_text += "};\n"
    if "Flags" not in input_enum.name:
        header_text += "ADD_ENUM_TO_REGMAP(" + input_enum.name + ");\n"
    header_text += "\n"

    return header_text


def _process_input_regmap(input_regmap: InputRegmap) -> str:
    """Convert InputRegmap into C header syntax

    Args:
        input_regmap (InputRegmap): The input regmap

    Returns:
        str: C header text
    """
    header_text: str = ""

    num_members = len(input_regmap.members)
    for i in range(0, num_members):
        if input_regmap.members[i].brief is not None:
            header_text += "    // @regmap brief: \"" + input_regmap.members[i].brief + "\"\n"
        if "pad" in input_regmap.members[i].name.lower() or "reserved" in input_regmap.members[i].name.lower():
            header_text += "    // @regmap access: \"none\"\n"
        elif input_regmap.members[i].access is not None:
            header_text += "    // @regmap access: \"" + input_regmap.members[i].access + "\"\n"
        if input_regmap.members[i].format is not None:
            header_text += "    // @regmap format: \"" + input_regmap.members[i].format + "\"\n"
        if input_regmap.members[i].min is not None:
            header_text += "    // @regmap min: \"" + input_regmap.members[i].min + "\"\n"
        if input_regmap.members[i].max is not None:
            header_text += "    // @regmap max: \"" + input_regmap.members[i].max + "\"\n"
        if input_regmap.members[i].units is not None:
            header_text += "    // @regmap units: \"" + input_regmap.members[i].units + "\"\n"
        if input_regmap.members[i].array_enum is not None:
            header_text += "    // @regmap array_enum: \"" + input_regmap.members[i].array_enum + "\"\n"
        if input_regmap.members[i].mask_enum is not None:
            header_text += "    // @regmap mask_enum: \"" + input_regmap.members[i].mask_enum + "\"\n"
        if input_regmap.members[i].value_enum is not None:
            header_text += "    // @regmap value_enum: \"" + input_regmap.members[i].value_enum + "\"\n"
        if input_regmap.members[i].hif_access is not None:
            header_text += "    // @regmap hif_access: \"" + str(input_regmap.members[i].hif_access) + "\"\n"

        header_text += "    " + _convert_integer_type(input_regmap.members[i].type)
        header_text += " " + input_regmap.members[i].name
        if input_regmap.members[i].type == "struct":
            header_text += " " + _snake_case(input_regmap.members[i].name)
        if input_regmap.members[i].array_count is not None and input_regmap.members[i].array_count > 1:
            header_text += "[" + str(input_regmap.members[i].array_count) + "]"
        header_text += ";\n"

    return header_text


def _json_module_to_c_header(legacy_input_json: InputJson,
                             legacy_json_data: Any,
                             description: str,
                             header_contents: str) -> str:
    """Convert InputJson describing a CAEF 'Module' into C header syntax

    Args:
        legacy_input_json (InputJson): Path to the file containing the legacy json data
        legacy_json_data (Any): Json data corresponding to the legacy Json file
        description (str): A text description of the CAEF component, to be used when appending to certain #defs
        header_contents (str): C header text

    Returns:
        str: C header text
    """

    # Add addtional includes for CAEF module JSONs
    header_contents += "#include \"caef_module.h\"\n"

    header_contents += CONSTANTS_TYPES_TITLE

    num_enums = len(legacy_input_json.enums)
    for i in range(0, num_enums):
        header_contents += _process_input_enum(legacy_input_json.enums[i])

    num_regmaps = len(legacy_input_json.regmap)
    for j in range(0, num_regmaps):
        header_contents += "struct " + legacy_input_json.regmap[j].name + " {\n"
        header_contents += _process_input_regmap(legacy_input_json.regmap[j])
        header_contents += "};\n"
        header_contents += "typedef struct " + legacy_input_json.regmap[j].name
        header_contents += " " + legacy_input_json.regmap[j].name + ";\n\n"

    # Find the top of the JSON for this module
    caef_module = legacy_json_data["Module"]
    caef_module = caef_module[next(iter(caef_module.keys()))]
    # Add init constants if they exist for this CAEF module
    if "initvalues" in caef_module:
        header_contents += _extract_constants(caef_module["initvalues"], description, const_type="initvalues")

    return header_contents


def legacy_json_to_c_header(legacy_path: str) -> str:
    """Import a legacy json file and convert it into a C header

    Args:
        legacy_path (str): Path to the file containing the legacy json data

    Returns:
        str: C header text
    """

    # Determine the unique file name and derive some text that will go in the output
    filename = os.path.basename(legacy_path)
    caefname = filename[:filename.index('.')].upper()

    header_contents: str = ""

    # Open the input file
    with open(legacy_path, "r", encoding="utf-8") as file_in:
        json_data = json.load(file_in)

    # Start the output by putting the top boilerplate text
    boilerplate_top = Template(C_HEADER_BOILERPLATE).substitute({
        'year' : str(datetime.date.today().year),
        'unique_header_name' : caefname,
    })
    header_contents += boilerplate_top

    header_contents += CPP_IFDEF

    header_contents += INCLUDES_TITLE

    if "Regmap" in json_data:
        input_json = legacy_json_to_input_regmap(legacy_path)
        header_contents = _json_module_to_c_header(input_json, json_data, caefname, header_contents)
    if "Module" in json_data:
        input_json = legacy_json_to_input_regmap(legacy_path)
        header_contents = _json_module_to_c_header(input_json, json_data, caefname, header_contents)
    if "Chain" in json_data:
        header_contents = _json_chain_to_cheader(json_data, caefname, header_contents)
    if "Actuator" in json_data:
        header_contents = _json_actuator_to_cheader(json_data, caefname, header_contents)

    # End the output by putting the final boilerplate text
    boilerplate_end = Template(C_HEADER_ENDIF).substitute({
        'unique_header_name' : caefname,
    })
    header_contents += boilerplate_end

    return header_contents
