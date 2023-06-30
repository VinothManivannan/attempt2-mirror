"""
utilities.py: This module provides the mergebin function, which can be used to merge a firmware
binary with a parameter file binary (i.e. file system).
"""


def merge_bin(fw_bin: str, params_bin: str, load_addr: int, output: str):
    """Merge a firmware binary with a parameter file binary

    Args:
        fw_bin (str): specifies the path to the firmware binary file
        params_bin (str): specifies the path to the parameters binary file
        load_addr (int): the offset of the file system
        output (str): specifies the path to the output file
    """
    with open(fw_bin, 'rb') as firmware_file:
        firmware_binary = firmware_file.read()

    with open(params_bin, 'rb') as params_file:
        params_binary = params_file.read()

    with open(output, 'wb+') as output_file:
        output_file.write(firmware_binary)
        output_file.truncate(load_addr)
        output_file.seek(load_addr)
        output_file.write(params_binary)
