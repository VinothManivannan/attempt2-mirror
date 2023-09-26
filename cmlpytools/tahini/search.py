"""Implement the search algorithms to find elements in a regmap
"""

from typing import Union, Optional
from dataclasses import dataclass
from .cmap_schema import Type as CMapType
from .cmap_schema import FullRegmap as CMapFullRegmap
from .cmap_schema import Regmap as CMapRegmap
from. cmap_schema import RegisterOrStruct as CMapRegisterOrStruct


@dataclass
class SearchMatch:
    """Represent a match by the search algorithm
    """
    result: CMapRegisterOrStruct
    address: int = 0


def _search_regmap(name: str,
                   cmap_type: CMapType,
                   regmap: CMapRegmap,
                   namespace: str = None,
                   ) -> Optional[SearchMatch]:
    """Implementation of the search function when called using a fullregmap instance.

    Args:
        name (str): Name of the element to be looked-up
        cmap_type (CMapType): Type of the element
        regmap (CMapRegmap): Cmap regmap to look into
        namespace (str): Namespace of the element

    Returns:
        Optional[SearchMatch]: Match object or None if no match
    """
    for node in regmap.children:
        match = search(name, cmap_type, node, namespace)
        if match:
            return match
    return None


def _shallow_search(name: str,
                    cmap_type: CMapType,
                    node: CMapRegisterOrStruct,
                    namespace: str = None,
                    ) -> Optional[SearchMatch]:
    """Perform a non-recursive search on a node object (struct or register).

    Args:
        name (str): Name of the element to look-up
        cmap_type (CMapType): Type of the element to look-up
        node (CMapRegisterOrStruct): Cmap element to look into
        namespace (str): Namespace of the element

    Returns:
        Optional[SearchMatch]: Match object or None if no match
    """
    if cmap_type != node.type:
        return None

    if not name.lower().startswith(node.name.lower()):
        return None

    if namespace is not None:
        if node.namespace is None:
            return None
        if namespace.lower() != node.namespace.lower():
            return None

    # Get suffix and convert into list of indexes.
    suffix = name[len(node.name):]
    if suffix == "":
        return SearchMatch(node, node.addr)
    indexes_or_aliases = suffix.split("_")

    # if split resulted in more than one element then it means that the node name is not the correct
    # one, but it is completely identical to a part of the name that we are looking for.
    # Example: tempest_terr_cutoff and tempest_terr_cutoff_offset
    if len(indexes_or_aliases) > 1:
        return None

    if node.repeat_for is not None:
        if node.repeat_for[0].aliases is not None:
            # if aliases exist then the suffix must be in it
            if indexes_or_aliases[0].lower() not in node.repeat_for[0].aliases:
                return None
        elif int(indexes_or_aliases[0]) >= node.repeat_for[0].count:
            # if the suffix is a number then it should be larger than the repeatfor count
            return None

    indexes = []
    for index_or_alias, repeat_for in zip(indexes_or_aliases, node.repeat_for):
        index = None
        try:
            # Try converting the suffix into an index
            index = int(index_or_alias)

        except ValueError:
            if repeat_for.aliases:
                alias_num = 0
                for alias in repeat_for.aliases:
                    if alias.lower() == index_or_alias.lower():
                        index = alias_num
                        break
                    alias_num += 1

        if index is None:
            return None

        indexes.append(index)

    # Calculate exact address of the match
    address = node.addr
    for index, repeat_for in zip(indexes, node.repeat_for):
        address += index * repeat_for.offset
    return SearchMatch(node, address)


def _search_struct_members(name: str,
                           cmap_type: CMapType,
                           struct: CMapRegisterOrStruct,
                           namespace: str = None,
                           ) -> Optional[SearchMatch]:
    """_summary_

    Args:
        name (str): Name of the element to look-up
        cmap_type (CMapType): Type of the element to look-up
        struct (CMapRegisterOrStruct): Cmap struct to look into
        namespace (str): Namespace of the element

    Returns:
        Optional[SearchMatch]: Perform a search on the members of a struct and returns the first match found.
    """

    match = None
    for node in struct.struct.children:
        match = search(name, cmap_type, node, namespace)
        if match:
            break

    return match


def search(name: str,
           cmap_type: CMapType,
           node: Union[CMapFullRegmap, CMapRegisterOrStruct],
           namespace: str = None,
           ) -> Optional[SearchMatch]:
    """Search for a register or struct using its name in a full regmap or a node of.

    Args:
        name (str): Name of the register or struct to be looked-up
        cmap_type (CMapType): Type of the node to be looked up (register or struct)
        node (Union[CMapFullRegmap, CMapRegisterOrStruct]): The regmap or node to look into.
        namespace (str): Namespace of the element

    Returns:
        Optional[SearchMatch]: Match result if found, None otherwise.
    """

    if isinstance(node, CMapFullRegmap):
        return _search_regmap(name, cmap_type, node.regmap, namespace)

    if isinstance(node, CMapRegmap):
        return _search_regmap(name, cmap_type, node, namespace)

    match = _shallow_search(name, cmap_type, node, namespace)
    if match:
        return match

    if node.type == CMapType.STRUCT:
        return _search_struct_members(name, cmap_type, node, namespace)

    return None
