# CML Python Tools

This package contains a number of python tools used in our Firmware build process.

## Installation

### Using option `--find-links`

After a release has been deployed it can be installed using the following command:

```
pip install --find-links="%PYPIPATH%" --no-index cmlpytools
```

Where `PYPIPATH` should be a system variable set to `\\ws-fs1\company\Technical\Utilities\Continuous_Integration\python_packages`

### Using pip.ini
Alternatively, users can also add the look-up path permanently to their `pip.ini` file in `C:/Users/%USER%/pip`.

**pip.ini:**
```
[install]
find-links = W:/Technical/Utilities/Continuous_Integration/python_packages
```

CML packages (and dependencies) can then be installed using the following command:

```
pip install cmlpytools
```

## Python 3 Static Analysis
This repository uses `Pylint` as a static analysis tool to enforce the best python 3 guidelines and code styles. `Pylint` follows the "Style Guide for Python Code" -- `PEP 8`, which can be a quick and easy way of seeing if your code has captured the essence of `PEP 8`.

`PEP 8`: https://peps.python.org/pep-0008/

## Getting started with Python 3

Some training document is available at `W:\projects\P0069_Firmware_Development\Training\Introduction to Python3.pptx`

## Projects

This repository is used to store multiple projects:
- [tahini](doc/tahini.md)
- [minfs](doc/minfs.md)
- [logparse](doc/logparse.md)
