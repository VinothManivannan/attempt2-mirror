"""
This module implements the tahini command line argument.
"""
import argparse
import textwrap
import sys
from .tahini_cmap import TahiniCmap
from .tahini_crc import TahiniCrc
from .tahini_gimli import TahiniGimli
from .tahini_version import TahiniVersion
from .legacy_json_to_header import legacy_json_to_c_header
from .legacy_json_converter import legacy_json_to_input_regmap
from .tahini_generate_flat_txt import GenerateFlatTxt
from .tahini_generate_appnote_csv import GenerateAppnoteCSV
from .tahini_generate_txt import GenerateTxt
from .tahini_generate_api_cheader import GenerateApiCheader
from .tahini_add_json_info import TahiniAddJsonInfo

class Tahini():
    """Class for Tahini Command Line implementation
    """

    def __init__(self):
        parser = argparse.ArgumentParser(usage="tahini <command> [args]",
                                         description="Cambridge Mechatronics Ltd. regmap tools.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''\
        Available commands:
            gimli         Generate JSON input file from C definitions from a compiled file (elf, o, exe).
                            Usage: tahini gimli <firmware-file-path> --output <json-path.json>
            addjsoninfo   Combine gimli generated JSON input file with additional one with extra information when needed (e.g. Rumba S10)
                            Usage: tahini addjsoninfo <json-path.json> <additional-json-path.json> --output <json-path.json>
            version       Generate version json file
                            Usage: tahini version <device-type> <project-path> <build-config-name> <build-config-id> --output <version.info.json>
            cmap          Generate cmap source file. This file is a source for other interpretations of the regmap (txt, csv, etc...)
                            Usage: tahini cmap <project-path> <version-info-file> <input-json-path> outputs a Cmapsource File to stdout
            crc           Create a CRC-appended ARM Cortex-M firmware binary
                            Usage: tahini crc <firmware-file.bin> --output <firmware-file.bin>
            flattxt       Generate flat txt regmap. 
                            Usage: tahini flattxt <cmap-json-path> --output <flat-txt-path.txt>
            csv           Generate csv regmap file (usually for appnotes).
                            Usage: tahini csv <cmap-json-path> --output <csv-file.csv>
            txt           Generate human-readable regmap txt file
                            Usage: tahini txt <cmap-json-path> --output <txt-path.txt>
            legacycheader Generate old-style json header for compatipiliti with Tzatziki
                            Usage: tahini legacycheader <legacy-json-path> --output <legacy-header.json>
            apicheader    Generate API c header for the API code
                            Usage: tahini apicheader <cmap-json-path> --output <c-header.h>
        All these commands can output the result to stdout if `--output` is not set.
        For more detailed help, type "tahini <command> -h" '''))

        parser.add_argument('command', help='tahini subcommand', nargs=1)
        parser.add_argument(
            'otherthings', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        args = parser.parse_args()

        # argparse doesn't replace '-' with '_' in positional arguments automatically
        command = args.command[0].replace('-', '_')

        # Commands are methods of the RegmapCli class.
        # This code checks if there's a method with the same name as the provided command.
        if not hasattr(self, command):
            print('Unrecognized command')
            parser.print_help()
            sys.exit(1)
        getattr(self, command)()

    def gimli(self):
        """
        Generate input json file
        """

        usage = textwrap.dedent('''
            - tahini gimli <firmware-binary-path> [--output=<file-path>]
            - tahini gimli <firmware-binary-path> <compile-unit-name.c> [--output=<file-path>]
            - tahini gimli <firmware-binary-path> <compile-unit-name.c> ... [--output=<file-path>]
            ''')
        descr = "Extract C definitons from a firmware elf file and generate an input json file"
        parser = argparse.ArgumentParser(description=descr, usage=usage)
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("elf_path",
            help=textwrap.dedent('''
                Path to a compiled file to extract dwarf information from.
                It can be `.elf`, `.o`, `.exe` or other formats.
            '''))
        parser.add_argument("compile_unit_names", nargs='*',
            help="Name(s) of compile unit(s). "
            + "This is derived from the <firmware-binary-path> if this argument is not specified.")
        parser.add_argument("--output", required=False,
            help="Write the input json file to the path specified instead of the standard output.")
        args = parser.parse_args()

        # pylint: disable=consider-using-with
        stdout = sys.stdout
        if args.output is not None:
            sys.stdout = open(args.output, "w", encoding="UTF-8")

        TahiniGimli.main(args.elf_path, args.compile_unit_names)

        if args.output is not None:
            sys.stdout.close()
        sys.stdout = stdout
        # pylint: enable=consider-using-with

    def addjsoninfo(self):
        """
        Combine input json and additional json files
        """
        parser = argparse.ArgumentParser(
            description="Combine gimli generated JSON input file with additional one with extra information",
            usage=
                "tahini addjsoninfo <json-path.json> <additional-json-path.json> --output <json-path.json>")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("input_json_path", help="Path to gimli generated input json file. Example: path/to/stmh")
        parser.add_argument("additional_json_path", help="Path to additional json file. Example: path/to/stmh")
        parser.add_argument("--output", required=False,
            help="Write the result into the file specified instead of the standard output.")
        args = parser.parse_args()

        combined_json_output = TahiniAddJsonInfo.combine_json_files(args.input_json_path,
                                                                    args.additional_json_path)

        # pylint: disable=consider-using-with
        stdout = sys.stdout
        if args.output is not None:
            sys.stdout = open(args.output, "w", encoding="UTF-8")
        else:
            sys.stdout = open(args.input_json_path, "w", encoding="UTF-8")

        sys.stdout.write(combined_json_output.to_json(indent=4))

        if args.output is not None:
            sys.stdout.close()
        sys.stdout = stdout
        # pylint: enable=consider-using-with

    def version(self):
        """
        Write version.info.json file
        """

        parser = argparse.ArgumentParser(
            description="Generate basic version info",
            usage="\
            tahini version <project-path> <device-type> <build-config-name> <build-config-id> [--output=<file-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("project_path", help="Firmware Project Path. Example: path/to/stmh")
        parser.add_argument("device_type", help="Device Type. Example: cm824_4ws")
        parser.add_argument("config_name", help="Build Configuration Name. Example fw_cm8x4_4ws")
        parser.add_argument("config_id", help="Build ID. Example: 9")
        parser.add_argument("--output", required=False,
            help="Write the result into the file specified instead of the standard output.")
        args = parser.parse_args()

        version_info = TahiniVersion.create_version_info(args.project_path,
                                                         args.device_type,
                                                         args.config_name,
                                                         args.config_id)

        # pylint: disable=consider-using-with
        stdout = sys.stdout
        if args.output is not None:
            sys.stdout = open(args.output, "w", encoding="UTF-8")

        sys.stdout.write(version_info.to_json(indent=4))

        if args.output is not None:
            sys.stdout.close()
        sys.stdout = stdout
        # pylint: enable=consider-using-with

    def cmap(self):
        """
        Generate cmap source file
        """

        parser = argparse.ArgumentParser(
            description="Combine version info with an Input JSON file to form a Cmapsource file",
            usage="tahini cmap <project-path> <version-info-path> <input-json-path> [--output=<file-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("project_path", help="Path to the git repository")
        parser.add_argument("version_info_path", help="Path to Version info file")
        parser.add_argument("input_json_path", help="Path to Input JSON file")
        parser.add_argument("--output", required=False,
                            help="Write the result into the file specified instead of the standard output.")
        args = parser.parse_args()

        cmap = TahiniCmap.cmap_fullregmap_from_input_json_path(project_path=args.project_path,
                                                               version_info_path=args.version_info_path,
                                                               input_json_path=args.input_json_path)

        # pylint: disable=consider-using-with
        stdout = sys.stdout
        if args.output is not None:
            sys.stdout = open(args.output, "w", encoding="UTF-8")

        sys.stdout.write(cmap.to_json(indent=4))

        if args.output is not None:
            sys.stdout.close()
        sys.stdout = stdout
        # pylint: enable=consider-using-with

    def crc(self):
        """
        Add CRC and size fields to Griffin binary file
        """

        parser = argparse.ArgumentParser(
            description="Create a CRC-appended ARM Cortex-M firmware binary",
            usage="tahini crc <input-binary-file> [-v] [--output=<file-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("input_file", help="Input binary file")
        parser.add_argument('-v', '--verbose', action="store_true", help="Activate verbose output")
        parser.add_argument("--output", required=False,
            help="Write the result into the file specified instead of the standard output.")
        args = parser.parse_args()

        # pylint: disable=consider-using-with
        stdout = sys.stdout
        if args.output is not None:
            sys.stdout = open(args.output, "wb")
        else:
            sys.stdout = sys.stdout.buffer

        TahiniCrc.main(args.input_file, args.verbose)

        if args.output is not None:
            sys.stdout.close()
        sys.stdout = stdout
        # pylint: enable=consider-using-with

    def legacy(self):
        """
        Generate an input regmap from a legacy json file
        """
        parser = argparse.ArgumentParser(
            description="Combine version info with an Input JSON file to form a Cmapsource file",
            usage="tahini legacy <legacy-json-path> [--output=<input-json-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("legacy_json_path", help="Path to the Legacy json file")
        parser.add_argument("--output", required=False,
            help="Write the result into the file specified instead of the standard output.")
        args = parser.parse_args()

        input_json = legacy_json_to_input_regmap(args.legacy_json_path).to_json()

        if args.output is not None:
            with open(args.output, "w", encoding="utf-8") as output:
                output.write(input_json)
        else:
            print(input_json)

    def legacycheader(self):
        """
        Generate a C header file from a legacy json file
        """
        parser = argparse.ArgumentParser(
            description="Generate a C header file from a legacy json file",
            usage="tahini legacycheader <legacy-json-path> [--output=<input-json-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("legacy_json_path", help="Path to the Legacy json file")
        parser.add_argument("--output", required=False,
            help="Write the result into the file specified instead of the standard output.")
        args = parser.parse_args()

        header_file = legacy_json_to_c_header(args.legacy_json_path)

        if args.output is not None:
            with open(args.output, "w", encoding="utf-8") as output:
                output.write(header_file)
        else:
            print(header_file)

    def flattxt(self):
        """
        Generate a flat txt file from cmap source file
        """
        parser = argparse.ArgumentParser(
            description="Generate flat txt file",
            usage="tahini flattxt <cmap-path> [--output=<flat-txt-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("cmap_path", help="Path to the CmapSource json file")
        parser.add_argument("--output", required=True,
            help="Write the result into the file specified.")

        args = parser.parse_args()
        GenerateFlatTxt.create_flat_from_cmap_path(args.cmap_path, args.output)

    def csv(self):
        """
        Generate a csv file from cmap source file
        """
        parser = argparse.ArgumentParser(
            description="Generate csv file",
            usage="tahini csv <cmap-path> [--output=<csv-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("cmap_path", help="Path to the CmapSource json file")
        parser.add_argument("--output", required=True,
            help="Write the result into the file specified.")

        args = parser.parse_args()
        GenerateAppnoteCSV.create_csv_from_cmap_path(args.cmap_path, args.output)

    def txt(self):
        """
        Generate a txt file from cmap source file
        """
        parser = argparse.ArgumentParser(
            description="Generate a human-readable txt file",
            usage="tahini txt <cmap-path> [--output=<txt-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("cmap_path", help="Path to the CmapSource json file")
        parser.add_argument("--output", required=True,
            help="Write the result into the file specified.")

        args = parser.parse_args()
        GenerateTxt.create_txt_from_cmap_path(args.cmap_path, args.output)

    def apicheader(self):
        """
        Generate an API C Header from a cmap source file
        """
        parser = argparse.ArgumentParser(
            description="Generate api c header file for the API code",
            usage="tahini apicheader <cmap-path> [--output=<api-c-header-path>]")
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument("cmap_path", help="Path to the CmapSource json file")
        parser.add_argument("--output", required=True,
            help="Write the result into the file specified.")

        args = parser.parse_args()
        GenerateApiCheader.from_cmapsource_path(args.cmap_path, args.output)


def main():
    """This function is the entry point for command line invocation
    """
    Tahini()
    # Command line example
    # tahini version <project-path> <build-config-name> <build-config-id> > <version-info-file-path>
    # tahini version "C:\work\FW-2518" "CONFIG" 3 > C:/work/FW-2518/regmap/version.info.json
