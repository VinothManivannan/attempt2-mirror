"""Generate appnote CSV output
"""
import csv
from io import TextIOWrapper
from tahini.cmap_schema import Type as CmapType
from tahini.cmap_schema import FullRegmap as CmapFullRegmap
from tahini.cmap_schema import RegisterOrStruct as CmapRegisterOrStruct


class TahiniGenerateCSVError(Exception):
    """Class used to handle errors when generating csv output file
    """
    pass


class GenerateAppnoteCSV():
    """Class for generating appnote csv output file
    """

    @staticmethod
    def _create_csv_from_cmap(field: list[CmapRegisterOrStruct], reg: list[str], addr: list[int]) -> None:
        """Recursively get register name and addr

        Args:
            field (list[CmapRegisterOrStruct]): Cmap register or struct to process
            reg (list[str]): Current list of register names found
            addr (list[int]): Current list of register addresses found
        """
        for item in field:
            if item.type == CmapType.REGISTER:
                if item.repeat_for:
                    for instance in item.get_instances():
                        instance_name = item.name + instance.get_legacy_suffix()
                        reg.append(instance_name.upper())
                        addr.append(f"{instance.addr:#04x}")
                else:
                    reg.append(item.name.upper())
                    addr.append(f"{item.addr:#04x}")
            elif item.type == CmapType.STRUCT:
                GenerateAppnoteCSV._create_csv_from_cmap(item.struct.children, reg, addr)

    @staticmethod
    def create_csv_from_cmap(cmapsource_data: CmapFullRegmap, output: TextIOWrapper) -> None:
        """Create csv output file from cmap source file

        Args:
            cmapsource_data (CmapFullRegmap): Cmap object to process
            output (TextIOWrapper): File IO to write to (must be already open)
        """
        try:
            regnames = []
            addresses = []
            GenerateAppnoteCSV._create_csv_from_cmap(cmapsource_data.regmap.children, regnames, addresses)

            writer = csv.writer(output)
            writer.writerow(regnames)
            writer.writerow(addresses)
        except Exception as exc:
            raise TahiniGenerateCSVError("Unable to create appnote csv file") from exc

    @staticmethod
    def create_csv_from_cmap_path(cmapsource_path: str, output_path: str) -> None:
        """Create appnote csv output file from cmap file path

        Args:
            cmapsource_path (str): Cmap source file path to read
            output_path (str): Output file path
        """
        with open(output_path, 'w', encoding='utf-8', newline='') as output:
            _ = GenerateAppnoteCSV.create_csv_from_cmap(CmapFullRegmap.load_json(cmapsource_path), output)
