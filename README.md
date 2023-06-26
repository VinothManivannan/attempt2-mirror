# Register map based on Python 3 library

# Installation
Tahini can be installed into the local machine from a wheel in CML python package repository, which will enable the tahini commands. To install Tahini in the local machine, following command needs to be run from command line:
`pip install tahini --no-index --find-links=\\ws-fs1\company\Technical\Utilities\Continuous_Integration\python_packages`

## Caution
There is a public python package of same name _tahini_. To install the correct Tahini, i.e. the CML one, the option `--no-index` is necessary which makes sure pip will try to install the package from the given location and nowhere else.

# Tahini CLI
There are three tahini commands
tahini gimli <args> - TODO
tahini version <args>
tahini cmap <args> - TODO

## Usage
tahini version can be used as follows:
tahini version --project_path="Path/to/FW/project" --config_name="CONFIG_NAME" --config_id=1 --destination="version/info/json/output/directory"

# Testing in local machine
1. Set the directory to the top level Git repository in VS Code terminal.
2. Run the command "python3 -m unittest discover -v tests", this is needed to make sure the relative path to the test files are correct in the tests.
