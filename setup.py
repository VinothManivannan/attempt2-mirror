"""
Import necessary tools to setup the project
"""
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
version_file_path = path.join(here, 'VERSION')

directory = path.dirname(path.realpath(__file__))
packagedir = path.join(path.dirname(path.realpath(__file__)), 'cmlpytools')

# Read version from existing VERSION file
VERSION_INFO = ""
if path.exists(version_file_path):
    with open(path.join(here, 'VERSION'), encoding='utf-8') as f:
        VERSION_INFO = f.read().strip()
else:
    # If no version file found, use this string instead to indicate local machine
    VERSION_INFO = "0.0.dev0"

setup(
    name="cmlpytools",
    version=VERSION_INFO,
    author="Cambridge Mechatronics Ltd.",
    author_email="electronicsgroup@cambridgemechatronics.com",
    url="http://gitlab.cm.local/devops/cmlpytools",
    description="CML Python tools used in our Firmware build system",
    install_requires=["marshmallow_dataclass", "marshmallow_enum", "crcmod", "future", "pythonnet"],
    entry_points={
        'console_scripts': [
            'tahini=cmlpytools.tahini.tahini:main',
            'logparse=cmlpytools.logparse.cmd:RunCommandParser',
            'minfs=cmlpytools.minfs.command_parser:run_command_parser'
        ],
    },
    package_data={'': [r'tahini/gimli/build-windows/gimli.exe',
                       r'tahini/gimli/build-windows/*.dll',
                       r'*.dll']},
    packages=find_packages(),
    # include_package_data=True,
    classifiers=[])
