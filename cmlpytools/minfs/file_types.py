"""
File types supported by MinFS
"""
from enum import IntEnum


class FileTypes(IntEnum):
    """Enum representing supported file types in a file system
    """
    REGMAP_CFG = 1
    CSA_FILE = 2
    STRUCT_BIN = 3
    CALMAP = 4
