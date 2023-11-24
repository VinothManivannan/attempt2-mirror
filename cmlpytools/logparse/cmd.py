"""
CLI command parser.
This module implements the CLI `logparse` which is installed on the user's machine after the package is installed.
The user should not interact directly with this module.
"""
from __future__ import print_function
from builtins import object
from os import path
import argparse
import textwrap
from .parse import LogTree


class CommandParser(object):
    def __init__(self):
        parser = argparse.ArgumentParser(usage="logparse <command> [args]",
                                         description="Cambridge Mechatronics Ltd. Release notes management tools.",
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog=textwrap.dedent('''\
        Available commands:
            render      Create or modify a regmap configuration file
            find-tag    Create or modify a calibration file
        For more detailed help, type "logparse <command> -h" '''))
        parser.add_argument('command', help='logparse subcommand', nargs=1)
        parser.add_argument(
            'otherthings', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        args = parser.parse_args()

        # argparse doesn't replace '-' with '_' in positional arguments automatically
        command = args.command[0].replace('-', '_')

        # Commands are methods of the CommandParser class.
        # This code checks if there's a method with the same name as the provided command.
        if not hasattr(self, command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, command)()

    def render(self):
        """
        Render command
        """
        parser = argparse.ArgumentParser(
            description="Cambridge Mechatronics Ltd. utility to render release notes.",
            usage='logparse render <options> [args]')
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument('--input', required=True,
                            help="Specify path for input release note file.")
        parser.add_argument('--output', required=True,
                            help="Specify path for output release note file.")
        parser.add_argument('--tag', help="(Optional) Specify tag to render.")
        parser.add_argument('--labels', nargs='+', metavar="[PATH]",
                            help="(Optional) Specify labels to keep.")

        args = parser.parse_args()

        node = LogTree.from_file(args.input)

        if args.tag:
            node = node.find_release(args.tag)
            if node is None:
                with open(args.output, "w", encoding="utf-8") as stream:
                    stream.write(f"No entry found for '{args.tag}'")
                    exit(0)

        if args.labels and node:
            node.filter_labels(args.labels)

        with open(args.output, "wb") as stream:
            node.render(stream)

    def find_tag(self):
        """
        Find version command
        """
        parser = argparse.ArgumentParser(
            description="Cambridge Mechatronics Ltd. Utility to check presence of a tag in release notes.",
            usage='minfs find-version <options> [args]')
        parser.add_argument('command', help=argparse.SUPPRESS)
        parser.add_argument('--input', required=True, nargs=1, metavar="[PATH]",
                            help="Specify path for input release note file.")
        parser.add_argument('--tag', required=True, nargs=1, metavar="[PATH]",
                            help="Specify path for input release note file.")
        args = parser.parse_args()

        log_tree = LogTree.from_file(args.input[0])

        if log_tree.has_release(args.tag[0]):
            print("Release {} was found.".format(args.tag[0]))
            exit(0)
        else:
            print("Release {} was not found.".format(args.tag[0]))
            exit(1)


def RunCommandParser():
    CommandParser()
