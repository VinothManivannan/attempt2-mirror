"""CLI command parser
"""

from __future__ import print_function
from builtins import range
from os import path
import argparse
import textwrap
import sys
from .regmap_cfg_file import RegmapCfgFile
from .calmap_file import CalmapFile
from .file import File
from .file_system import FileSystem
from .utilities import merge_bin
from .regmap_struct_file import RegmapStructFile


class MinFsHelpFormatter(argparse.RawTextHelpFormatter):
    """This class is used to format the "+" arguments of some subcommands
    """

    def _format_args(self, action, default_metavar):

        if action.nargs == argparse.ONE_OR_MORE:
            metavar = self._metavar_formatter(action, default_metavar)(2)
            result = f"{metavar[0]} {metavar[1]}"
        else:
            result = super()._format_args(action, default_metavar)
        return result


class CommandParser():
    """Implement the logic to parse commands on the console
    """

    def __init__(self):
        parser = argparse.ArgumentParser(
            usage="minfs <command> [args]",
            description="Cambridge Mechatronics Ltd. MinFS tools.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent('''\
            Available commands:
                regmap-cfg    Create or modify a regmap configuration file
                calmap        Create or modify a calibration file
                regmap-struct Create a packed C structure file
                fs            Create or modify a file system
                mergebin      Merge binary files

            For more detailed help, type "minfs <command> -h" '''))
        parser.add_argument('command', help='minfs subcommand', nargs=1)
        parser.add_argument('otherthings', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        args = parser.parse_args()

        # argparse doesn't replace '-' with '_' in positional arguments automatically
        command = args.command[0].replace('-', '_')

        # minfs commands are methods of the CommandParser class.
        # This code checks if there's a method with the same name as the provided command.
        if not hasattr(self, command):
            print('Unrecognized command')
            parser.print_help()
            sys.exit(1)
        getattr(self, command)()

    def regmap_cfg(self):
        """Regmap configuration file command
        """
        parser = argparse.ArgumentParser(
            description=textwrap.dedent('''\
                Cambridge Mechatronics Ltd.
                Utility for creating regmap configuration files for MinFS.'''),
            usage='minfs regmap-cfg <options> [args]',
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument('--regmap-cfg-json', nargs=1, metavar="[path]",
                            help='Specify json configuration file.')
        parser.add_argument('--regmap', required=True, nargs=1, metavar="[path]",
                            help="Path to a .json or .pickle file that can be loaded using the regmap module")
        parser.add_argument('-c', nargs='?', metavar="path",
                            help="Generate a C header file at the specified location.")
        parser.add_argument('-o', nargs='?', metavar="path",
                            help="Generate a binary file at the specified location.")
        parser.add_argument('--compress-regmap', type=int, default=0, metavar="[mode]",
                            help=textwrap.dedent('''\
            Specify the regmap config file compression mode.
                0: No compression. Make an entry for each inidividual register (default).
                1: Contiguous registers result as 1 entry.
                2: Not contiguous but close registers result as 1 entry.'''))
        args = parser.parse_args()
        regmap_cfg_file = RegmapCfgFile(args.regmap_cfg_json[0], args.regmap[0], None,
                                        args.compress_regmap)
        if args.o:
            regmap_cfg_file.tobin(args.o)
            print(path.basename(args.o)+" has been succesfully created")
        else:
            print("binary file path is not specified")
        if args.c:
            regmap_cfg_file.tocheader(args.c)
            print(path.basename(args.c)+" has been succesfully created")
        else:
            print("c header file path is not specified")

    def calmap(self):
        """Calibration map file command
        """
        parser = argparse.ArgumentParser(
            description="Cambridge Mechatronics Ltd. Utility for creating calibration map\
                         files for MinFS.",
            usage='minfs calmap <options> [args]')
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument('--calmap-json', required=True, nargs=1, metavar="[path]",
                            help="Specify the calibration map file")
        parser.add_argument('--regmap', required=True, nargs=1, metavar="[path]",
                            help="Path to a .json or .pickle file that can be loaded using the regmap module")
        parser.add_argument('-c', nargs='?', metavar="path",
                            help="Generate a C header file at the specified location.")
        parser.add_argument('-o', nargs='?', metavar="path",
                            help="Generate a binary file at the specified location.")
        args = parser.parse_args()
        calmap_file = CalmapFile(args.regmap[0], args.calmap_json[0])
        if args.o:
            calmap_file.tobin(args.o)
            print(path.basename(args.o)+" has been succesfully created")
        else:
            print("binary file path is not specified")
        if args.c:
            calmap_file.tocheader(args.c)
            print(path.basename(args.c)+" has been succesfully created")
        else:
            print("c header file path is not specified")

    def regmap_struct(self):
        """C structure binary file command
        """
        files = []
        parser = argparse.ArgumentParser(
            description=textwrap.dedent('''\
                Cambridge Mechatronics Ltd.
                Utility for C struct initialisation files'''),
            usage='minfs regmap-struct <options> [args]',
            formatter_class=MinFsHelpFormatter)
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument('--regmap-struct-json', action='append', nargs='+',
                            metavar=('[path] ...', '[path]'),
                            help='Specify json configuration file.')
        parser.add_argument('--regmap', nargs=1, metavar="[path]",
                            help="Path to a .json or .pickle file that can be loaded using the regmap module")
        parser.add_argument('--struct', nargs=1, metavar="[name]",
                            help="Name of a structure to pack")
        parser.add_argument('--bin-file', action='append', nargs='+',
                            metavar=('[path]', '[type] [name]'), help='Specify binary file.')
        parser.add_argument('-c', nargs='?', metavar="path",
                            help="Generate a C header file at the specified location.")
        parser.add_argument('-o', nargs='?', metavar="path",
                            help="Generate a binary file at the specified location.")

        args = parser.parse_args()

        if args.regmap_struct_json:
            for json_files in args.regmap_struct_json:
                for json_file in json_files:
                    files.append(json_file)
        else:
            print('Please specify a config file')

        # Pack the structure. The file name is discarded because this command only creates
        # binary data files with no additional information.
        regmap_struct_packed = RegmapStructFile(files, args.regmap[0], args.struct[0])

        if args.o:
            regmap_struct_packed.tobin(args.o)
            print(path.basename(args.o)+" has been succesfully created")
        else:
            print("binary file path is not specified")
        if args.c:
            regmap_struct_packed.tocheader(args.c)
            print(path.basename(args.c)+" has been succesfully created")
        else:
            print("c header file path is not specified")

    def fs(self):  # pylint: disable=invalid-name,too-many-branches
        """File system command
        """
        files = []
        json_struct_files = []
        cfg_paths = []
        parser = argparse.ArgumentParser(
            description=textwrap.dedent('''\
                Cambridge Mechatronics Ltd.
                Utility for creating MinFS file systems'''),
            usage='minfs fs <options> [args]',
            formatter_class=MinFsHelpFormatter)
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument('--regmap-cfg-json', action='append', nargs='+',
                            metavar=('[path]', '[name]'), help=textwrap.dedent('''\
            Specify json configuration file.'''))
        parser.add_argument('--compress-regmap', action='append', nargs=1, metavar="[mode]",
                            help=textwrap.dedent('''\
            Specify the regmap config file compression mode.
                0: No compression. Make an entry for each inidividual register (default).
                1: Contiguous registers result as 1 entry.
                2: Not contiguous but close registers result as 1 entry.
            If this parameter is used, then the compression mode must be specified for every regmap
            configuration file.
            i.e. the number of "--compress-regmap" must be equal to the number of
            "--regmap-cfg-json" '''))
        parser.add_argument('--calmap-json', action='append', nargs='+',
                            metavar=('[path]', '[name]'), help='Specify json calibration map file.')
        parser.add_argument('--regmap-struct-json', action='append', nargs='+',
                            metavar=('[path]...', '[name]'), help='Specify json configuration file.')
        parser.add_argument('--struct', nargs=1, metavar="[name]",
                            help="Name of a structure to pack")
        parser.add_argument('--regmap', nargs=1, metavar="[path]",
                            help="Path to a .json or .pickle file that can be loaded using the regmap module")
        parser.add_argument('--bin-file', action='append', nargs='+',
                            metavar=('[path]', '[type] [name]'), help='Specify binary file.')
        parser.add_argument('-c', nargs='?', metavar="path",
                            help="Generate a C header file at the specified location.")
        parser.add_argument('-o', nargs='?', metavar="path",
                            help="Generate a binary file at the specified location.")

        args = parser.parse_args()

        if args.regmap_cfg_json:
            if not args.regmap:
                print('Please specify a regmap file')
                sys.exit(1)
            if args.compress_regmap and (len(args.compress_regmap) != len(args.regmap_cfg_json)):
                print('Compression mode is enabled, but not specified for all files')
                sys.exit(1)
            i = 0
            for json_file in args.regmap_cfg_json:
                compression_mode = 0
                if args.compress_regmap:
                    compression_mode = int(args.compress_regmap[i][0])
                    if compression_mode not in list(range(3)):
                        print('Invalid compression mode')
                        sys.exit(1)
                if len(json_file) > 1:
                    file_name = json_file[1]
                else:
                    file_name = None
                files.append(RegmapCfgFile(json_file[0], args.regmap[0], file_name,
                                           compression_mode))
                cfg_paths.append(json_file[0])
                i += 1

        if args.calmap_json:
            if not args.regmap:
                print('Please specify a regmap file')
                sys.exit(1)
            for json_file in args.calmap_json:
                if len(json_file) > 1:
                    file_name = json_file[1]
                else:
                    file_name = None
                files.append(CalmapFile(args.regmap[0], json_file[0], file_name))
                cfg_paths.append(json_file[0])

        if args.regmap_struct_json:
            if not args.regmap:
                print('Please specify a regmap file')
                sys.exit(1)
            if not args.struct:
                print('The structure name is not specified')
                sys.exit(1)
            for json_files in args.regmap_struct_json:
                json_found = 0
                for json_file in json_files:
                    if len(json_file) > 1:
                        if path.splitext(json_file)[1] == ".json":
                            json_found = 1
                            json_struct_files.append(json_file)
                            cfg_paths.append(json_file)
                if json_found == 0:
                    print('Please specify a config file')
                    sys.exit(1)
                file_name = None
                if len(json_files) > 1:
                    if len(path.splitext(json_files[-1])) == 1:
                        file_name = json_files[-1]
                files.append(RegmapStructFile(json_struct_files, args.regmap[0], args.struct[0], file_name))

        if args.bin_file:
            for bin_file in args.bin_file:
                if len(bin_file) > 2:
                    file_name = bin_file[2]
                elif len(bin_file) == 2:
                    file_name = None
                else:
                    print("The file type is missing")
                    sys.exit(1)
                files.append(File(bin_file[0], bin_file[1], file_name))
                cfg_paths.append(bin_file[0])

        file_system = FileSystem(files)

        if args.o:
            output_dir = path.dirname(args.o)
            file_system.generate_file_report(cfg_paths, output_dir)
        elif args.c:
            output_dir = path.dirname(args.c)
            file_system.generate_file_report(cfg_paths, output_dir)

        if args.o:
            file_system.tobin(args.o)
            print(path.basename(args.o)+" has been succesfully created")
        else:
            print("binary file path is not specified")
        if args.c:
            file_system.tocheader(args.c)
            print(path.basename(args.c)+" has been succesfully created")
        else:
            print("c header file path is not specified")

    def mergebin(self):
        """Merge bin command
        """
        parser = argparse.ArgumentParser(
            description=textwrap.dedent('''\
                Cambridge Mechatronics Ltd.
                Utility for merging firmware with MinFS file systems'''),
            usage='minfs mergebin <options> [args]',
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument('--firmware', required=True, nargs=1, metavar="[path]",
                            help="Firmware binary")
        parser.add_argument('--params', required=True, nargs=2, metavar="[param]",
                            help=textwrap.dedent('''\
            Specify the parameter file to merge in the firmware binary.
            [Parameter 1] - offster of the file system in the final binary in hexadeximal format.
                            Example: '0x7000'
            [Parameter 2] - Path to the binary which can be a file system bin,
                            or a regmap configuration file bin.'''))
        parser.add_argument('-o', required=True, nargs=1, metavar="[path]",
                            help="Generate a binary file at the specified location.")

        args = parser.parse_args()

        offset = int(args.params[0], 0)
        merge_bin(args.firmware[0], args.params[1], offset, args.o[0])


def run_command_parser():
    """Entry-point of the command parsing tool
    """
    CommandParser()
