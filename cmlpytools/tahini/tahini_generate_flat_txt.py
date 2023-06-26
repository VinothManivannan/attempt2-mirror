"""Generate Flat txt output
"""
from io import TextIOWrapper
from typing import List, Tuple
from tahini.cmap_schema import FullRegmap as CmapFullRegmap
from tahini.cmap_schema import Type as CmapType
from tahini.cmap_schema import RegisterOrStruct as CmapRegisterOrStruct


class TahiniGenerateFlatError(Exception):
    """Class used to handle errors when generating flat txt file
    """
    pass


class GenerateFlatTxt():
    """Class for generating flat txt output file
    """

    @staticmethod
    def _write_instances(instances: List[Tuple[int, str]], output: TextIOWrapper) -> None:
        """Write a new register entry to the output file

        Args:
            instances (List[Tuple[int, str]]): List of register instances to write to the file
            output (TextIOWrapper): File handle
        """
        for instance in instances:
            output.write(f"{instance[0]:>#6x} {instance[1]:<30}\n")

    @staticmethod
    def _get_all_instances(field: List[CmapRegisterOrStruct]) -> List[Tuple[int, str]]:
        """Recursively get address and name info from each register

        Args:
            field (List[CmapRegisterOrStruct]): List of regmap or structs to process

        Returns:
            List[Tuple[int, str]]: List of tuples containing register address and name
        """
        all_instances = []
        for item in field:
            if item.type == CmapType.REGISTER:
                if item.repeat_for is None:
                    all_instances.append((item.addr, item.name))
                else:
                    for instance in item.get_instances():
                        instance_name = item.name + instance.get_legacy_suffix()
                        all_instances.append((instance.addr, instance_name))
            elif item.type == CmapType.STRUCT:
                all_instances.extend(GenerateFlatTxt._get_all_instances(item.struct.children))

        return all_instances

    @staticmethod
    def create_flat_from_cmap(cmapsource_data: CmapFullRegmap, output_flat_path: str) -> None:
        """Create flat txt output file from cmap file data

        Args:
            cmapsource_data (CmapFullRegmap): Cmap object to process
            output_flat_path (str): Output file path
        """
        try:
            with open(output_flat_path, 'w', encoding='utf-8') as output:
                output.write(f"{'address':*^20}\n")
                all_instances = GenerateFlatTxt._get_all_instances(cmapsource_data.regmap.children)

                # Ensure all instances are sorted by address: This is required to handle correctly repeated structs
                all_instances.sort(key=lambda instance: instance[0])

                GenerateFlatTxt._write_instances(all_instances, output)

        except Exception as exc:
            raise TahiniGenerateFlatError("Unable to create flat txt file") from exc

    @staticmethod
    def create_flat_from_cmap_path(cmapsource_path: str, output_flat_path: str) -> None:
        """Create flat txt output file from cmap file path
        """
        return GenerateFlatTxt.create_flat_from_cmap(CmapFullRegmap.load_json(cmapsource_path), output_flat_path)
