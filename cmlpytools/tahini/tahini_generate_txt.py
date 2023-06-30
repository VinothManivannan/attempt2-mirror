"""Generate txt output
"""
from io import TextIOWrapper
from typing import List
from .cmap_schema import FullRegmap as CmapFullRegmap
from .cmap_schema import Type as CmapType
from .cmap_schema import State as CmapState
from .cmap_schema import RegisterOrStruct as CmapRegisterOrStruct


def _indent(depth: int) -> str:
    """Method to create indent
    """
    return "  " * depth


class TahiniGenerateTxtError(Exception):
    """Class used to handle errors when generating txt output file
    """
    pass


class GenerateTxt():
    """Class for generating txt output file
    """
    @staticmethod
    def _write_info_entry(item: CmapRegisterOrStruct,
                          output: TextIOWrapper,
                          depth: int) -> None:
        """Add a single line entry for a register or struct in a txt file output

        Args:
            item (CmapRegisterOrStruct): Register or struct
            depth (int): Current depth of tabs in the file
            output (TextIOWrapper): File handle
        """
        output.write(f"{_indent(4*depth)}{item.addr:<#x}")

        if item.repeat_for is not None:
            repeat_for_count = "".join([f"[0-{(repeat_for.count - 1)}]" for repeat_for in item.repeat_for])
            output.write(f"{_indent(1)}{item.name}{repeat_for_count}".ljust(40))
        else:
            output.write(f"{_indent(1)}{item.name}".ljust(40))

        if item.type in CmapType.STRUCT:
            display_type = item.type.value
        else:
            display_type = item.register.ctype.value
        output.write(f"({display_type}){item.access.value:>20}\n")

    @staticmethod
    def _create_register_info(item: CmapRegisterOrStruct,
                              output: TextIOWrapper,
                              depth: int) -> None:
        """Create register information field
        """
        GenerateTxt._write_info_entry(item, output, depth)

        if item.register.bitfields is not None:
            for mask_item in item.register.bitfields:
                mask_addr = (2**mask_item.num_bits - 1) * (2 ** mask_item.position)
                output.write(f"{4*_indent(depth+1)}mask: " +
                             f"{mask_addr:#04x} {mask_item.name:40s}(flag)\n")

    @staticmethod
    def _create_register_brief(item: CmapRegisterOrStruct,
                               output: TextIOWrapper) -> None:
        """Create register brief field
        """

        def _create_brief_states(field: List[CmapState],
                                 output: TextIOWrapper,
                                 depth: int) -> None:
            """Create State field in bitfields

            Args:
                field (List[CmapState]): List of states to process
                output (TextIOWrapper): File IO to write to
                depth (int): Current level of indendations
            """
            for states_item in field:
                output.write(_indent(2*depth)+f"{states_item.value:5}:" +
                             _indent(1)+f"{states_item.name}")
                if states_item.brief is not None:
                    output.write(_indent(6)+f"{states_item.brief}\n")
                else:
                    output.write("\n")

        output.write(f"\n{item.name:30s}")
        if item.brief is not None:
            output.write(f"{item.brief}\n")
        else:
            output.write("\n")
        output.write(_indent(2)+f"Access:{item.access.value}" +
                     _indent(2)+f"Bytes:{item.size}" +
                     _indent(2)+f"Format:{item.register.format}" +
                     _indent(2)+f"Max:{item.register.max}" +
                     _indent(2)+f"Min:{item.register.min}\n")

        if item.register.bitfields is not None:
            output.write(_indent(2)+"Flags:\n")
            for mask_item in item.register.bitfields:
                mask_addr = (2**mask_item.num_bits - 1) * (2 ** mask_item.position)
                output.write(_indent(4)+f"mask: {mask_addr:#04x}" +
                             _indent(2)+f"{mask_item.name}")
                if mask_item.brief is not None:
                    output.write(_indent(2)+f"{mask_item.brief}\n")
                else:
                    output.write("\n")
                if mask_item.states is not None:
                    output.write(_indent(6)+"States:\n")
                    _create_brief_states(mask_item.states, output, depth=4)

        if item.register.states is not None:
            output.write(_indent(2)+"States:\n")
            _create_brief_states(item.register.states, output, depth=2)

    @staticmethod
    def _create_brief(field: List[CmapRegisterOrStruct],
                      output: TextIOWrapper) -> None:
        """Recursively get register brief

        Args:
            field (List[CmapRegisterOrStruct]): List of register or structs to process
            output (TextIOWrapper): File IO to write to
        """
        for item in field:
            if item.type == CmapType.REGISTER:
                GenerateTxt._create_register_brief(item, output)
            elif item.type == CmapType.STRUCT:
                GenerateTxt._create_brief(item.struct.children, output)

    @staticmethod
    def _create_info(field: List[CmapRegisterOrStruct],
                     output: TextIOWrapper,
                     depth: int) -> None:
        """Recursively get register information

        Args:
            field (List[CmapRegisterOrStruct]): List of register or struct to process
            output (TextIOWrapper): File IO to write to
            depth (int): Current level of indendation
        """
        for item in field:
            if item.type == CmapType.REGISTER:
                GenerateTxt._create_register_info(item, output, depth)
            elif item.type == CmapType.STRUCT:
                GenerateTxt._write_info_entry(item, output, depth)
                GenerateTxt._create_info(item.struct.children, output, depth+1)

    @staticmethod
    def create_txt_from_cmap(cmapsource_data: CmapFullRegmap, output: TextIOWrapper) -> None:
        """Create txt output file from cmap file data

        Args:
            cmapsource_data (CmapFullRegmap): Cmap object to process
            output (TextIOWrapper): File IO to write to (must be already opened)
        """
        # Output the register info
        GenerateTxt._create_info(cmapsource_data.regmap.children, output, depth=0)

        # Output the register briefs
        output.write(f"\n\n\n\n{'Register Briefs':*^80}\n\n")
        GenerateTxt._create_brief(cmapsource_data.regmap.children, output)

    @staticmethod
    def create_txt_from_cmap_path(cmapsource_path: str, output_txt_path: str) -> None:
        """Create txt output file from cmap file path

        Args:
            cmapsource_path (str): Cmapsource file path to process
            output_txt_path (str): Output file path
        """
        try:
            with open(output_txt_path, 'w', encoding='utf-8') as output:
                _ = GenerateTxt.create_txt_from_cmap(CmapFullRegmap.load_json(cmapsource_path), output)
        except Exception as exc:
            raise TahiniGenerateTxtError("Unable to create txt file") from exc
