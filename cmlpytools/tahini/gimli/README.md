# gimli

Firmware C/C++ command-line tool that combines DWARF debug information with C source/header file comments to generate a JSON-based regmap.

## Getting Started [Windows]

Gimli can be built from a Visual Studio Developer or MSYS shell ... the former costs £££ so we'll use the latter.

1. Open a `GIT`-aware shell, and type the following

    * **Note: I will open a GIT-bash shell**
    * **Note: I use `/c/var/src` as the root folder for all `git clone ...`s**

    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 ~
    $ cd /c/var/src
    ```
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src
    $ git clone http://gitlab.cm.local/devops/gimli.git
    Cloning into 'gimli'...
    remote: Enumerating objects: 3, done.
    remote: Counting objects: 100% (3/3), done.
    remote: Compressing objects: 100% (2/2), done.
    remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
    Receiving objects: 100% (3/3), done.
    ```

2. Install MSYS by following the instructions [here](https://www.msys2.org/)

    - **Note: I install to `C:\usr\bin\msys64` but the default `C:\msys64` should work fine**
    - **Note: I accept the option to add `Start Menu` shortcuts**
    - **Note: I accept the option to `Run MSYS 64bit` ... click finish**

3. At the `MSYS2 MSYS` shell, type the following to update the package databases:

    ```
    pacman -Suy
    ```
    ```
    :: Synchronizing package databases...
    mingw32              1673.9 KiB  1003 KiB/s 00:02 [#####################] 100%
    mingw64              1684.8 KiB  2.75 MiB/s 00:01 [#####################] 100%
    ucrt64               1735.3 KiB  3.42 MiB/s 00:00 [#####################] 100%
    clang32              1629.5 KiB   682 KiB/s 00:02 [#####################] 100%
    clang64              1670.7 KiB  3.06 MiB/s 00:01 [#####################] 100%
    msys                  400.3 KiB  3.91 MiB/s 00:00 [#####################] 100%
    :: Starting core system upgrade...
    warning: terminate other MSYS2 programs before proceeding
    resolving dependencies...
    looking for conflicting packages...

    Packages (3) filesystem-2022.01-5  mintty-1~3.6.1-2  msys2-runtime-3.3.5-3

    Total Download Size:    4.13 MiB
    Total Installed Size:  14.10 MiB
    Net Upgrade Size:       0.06 MiB

    :: Proceed with installation? [Y/n]
    ```
    **Hit `Y` then `<enter>`**
    ```
    :: Retrieving packages...
    filesystem-2022....   108.1 KiB   318 KiB/s 00:00 [#####################] 100%
    mintty-1~3.6.1-2...   798.7 KiB   968 KiB/s 00:01 [#####################] 100%
    msys2-runtime-3....     3.2 MiB   727 KiB/s 00:05 [#####################] 100%
    Total (3/3)             4.1 MiB   899 KiB/s 00:05 [#####################] 100%
    (3/3) checking keys in keyring                     [#####################] 100%
    (3/3) checking package integrity                   [#####################] 100%
    (3/3) loading package files                        [#####################] 100%
    (3/3) checking for file conflicts                  [#####################] 100%
    (3/3) checking available disk space                [#####################] 100%
    :: Processing package changes...
    (1/3) upgrading filesystem                         [#####################] 100%
    (2/3) upgrading mintty                             [#####################] 100%
    (3/3) upgrading msys2-runtime                      [#####################] 100%
    :: To complete this update all MSYS2 processes including this terminal will be closed. Confirm to proceed [Y/n]
    ```
    **Hit `Y` then `<enter>`** ... the shell should have closed.

4. Open a `PowerShell` shell, and type the following:

    ```
    setx MSYS2_INSTALL_DIR <path-to-msys64>
    ```
    - **Note: I would enter `C:\usr\bin\msys64` as `<path-to-msys64>`**
 
    Close the shell.

5. Open an `MSYS MinGW x64` shell, and type the following:

    ```
    pacman -S mingw-w64-x86_64-cmake
    ```
    ```
    resolving dependencies...
    looking for conflicting packages...

    Packages (39) mingw-w64-x86_64-brotli-1.0.9-5  mingw-w64-x86_64-bzip2-1.0.8-2
                mingw-w64-x86_64-c-ares-1.18.1-1  mingw-w64-x86_64-ca-certificates-20211016-3
                mingw-w64-x86_64-curl-7.84.0-2  mingw-w64-x86_64-expat-2.4.8-1
                mingw-w64-x86_64-gcc-libs-12.2.0-1  mingw-w64-x86_64-gettext-0.21-3
                mingw-w64-x86_64-gmp-6.2.1-3  mingw-w64-x86_64-jansson-2.14-2
                mingw-w64-x86_64-jemalloc-5.3.0-1  mingw-w64-x86_64-jsoncpp-1.9.5-1
                mingw-w64-x86_64-libarchive-3.6.1-2  mingw-w64-x86_64-libb2-0.98.1-2
                mingw-w64-x86_64-libffi-3.4.2-2  mingw-w64-x86_64-libiconv-1.17-1
                mingw-w64-x86_64-libidn2-2.3.3-1  mingw-w64-x86_64-libpsl-0.21.1-4
                mingw-w64-x86_64-libssh2-1.10.0-1  mingw-w64-x86_64-libsystre-1.0.1-4
                mingw-w64-x86_64-libtasn1-4.18.0-1  mingw-w64-x86_64-libtre-git-r128.6fb7206-2
                mingw-w64-x86_64-libunistring-1.0-1  mingw-w64-x86_64-libuv-1.42.0-3
                mingw-w64-x86_64-libwinpthread-git-10.0.0.r68.g6eb571448-1
                mingw-w64-x86_64-libxml2-2.9.14-4  mingw-w64-x86_64-lz4-1.9.4-1
                mingw-w64-x86_64-mpc-1.2.1-1  mingw-w64-x86_64-mpfr-4.1.0.p13-1
                mingw-w64-x86_64-nghttp2-1.48.0-1  mingw-w64-x86_64-ninja-1.11.0-1
                mingw-w64-x86_64-openssl-1.1.1.q-1  mingw-w64-x86_64-p11-kit-0.24.1-3
                mingw-w64-x86_64-pkgconf-1.8.0-2  mingw-w64-x86_64-rhash-1.4.3-1
                mingw-w64-x86_64-xz-5.2.6-1  mingw-w64-x86_64-zlib-1.2.12-1
                mingw-w64-x86_64-zstd-1.5.2-2  mingw-w64-x86_64-cmake-3.24.1-2

    Total Download Size:    31.10 MiB
    Total Installed Size:  236.04 MiB

    :: Proceed with installation? [Y/n]
    ```
    **Hit `Y` then `<enter>`**
    ```
    :: Retrieving packages...
    mingw-w64-x86_64-curl-7.84...  1360.4 KiB   497 KiB/s 00:03 [###############################] 100%
    mingw-w64-x86_64-gettext-0...     3.1 MiB   785 KiB/s 00:04 [###############################] 100%
    mingw-w64-x86_64-libxml2-2...  1530.7 KiB   371 KiB/s 00:04 [###############################] 100%
    mingw-w64-x86_64-gcc-libs-...   876.2 KiB   473 KiB/s 00:02 [###############################] 100%
    mingw-w64-x86_64-libiconv-...   720.2 KiB  2.16 MiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-libuv-1.4...   571.0 KiB   801 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-gmp-6.2.1...   558.6 KiB  4.55 MiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-libarchiv...   823.7 KiB   446 KiB/s 00:02 [###############################] 100%
    mingw-w64-x86_64-zstd-1.5....   494.9 KiB  1107 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-openssl-1...     4.8 MiB   764 KiB/s 00:06 [###############################] 100%
    mingw-w64-x86_64-libunistr...   754.0 KiB   418 KiB/s 00:02 [###############################] 100%
    mingw-w64-x86_64-xz-5.2.6-...   427.7 KiB  3.24 MiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-ninja-1.1...   435.2 KiB   235 KiB/s 00:02 [###############################] 100%
    mingw-w64-x86_64-mpfr-4.1....   356.9 KiB   791 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-brotli-1....   385.4 KiB   439 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-ca-certif...   330.7 KiB  3.14 MiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-jemalloc-...   408.8 KiB   194 KiB/s 00:02 [###############################] 100%
    mingw-w64-x86_64-libssh2-1...   255.0 KiB  2.15 MiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-rhash-1.4...   227.5 KiB  2.02 MiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-nghttp2-1...   208.8 KiB   809 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-p11-kit-0...   345.2 KiB   461 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-c-ares-1....   204.8 KiB   816 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-jsoncpp-1...   228.6 KiB   248 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-expat-2.4...   158.3 KiB  1092 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-lz4-1.9.4...   147.4 KiB   976 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-zlib-1.2....   102.3 KiB  1124 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-bzip2-1.0...    89.1 KiB   498 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-libtre-gi...    84.2 KiB   597 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-libtasn1-...   187.4 KiB   169 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-pkgconf-1...    79.1 KiB   531 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-mpc-1.2.1...    72.7 KiB   720 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-jansson-2...    56.0 KiB   277 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-libidn2-2...   163.0 KiB   111 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-libsystre...    24.0 KiB   247 KiB/s 00:00 [###############################] 100%
    mingw-w64-x86_64-libpsl-0....    73.0 KiB  81.3 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-libwinpth...    28.1 KiB  53.9 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-libffi-3....    42.0 KiB  46.6 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-libb2-0.9...    23.7 KiB  18.3 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-cmake-3.2...    10.7 MiB   582 KiB/s 00:19 [###############################] 100%
    Total (39/39)                    31.1 MiB  1605 KiB/s 00:20 [###############################] 100%
    (39/39) checking keys in keyring                             [###############################] 100%
    (39/39) checking package integrity                           [###############################] 100%
    (39/39) loading package files                                [###############################] 100%
    (39/39) checking for file conflicts                          [###############################] 100%
    (39/39) checking available disk space                        [###############################] 100%
    :: Processing package changes...
    ( 1/39) installing mingw-w64-x86_64-gmp                      [###############################] 100%
    ( 2/39) installing mingw-w64-x86_64-mpfr                     [###############################] 100%
    ( 3/39) installing mingw-w64-x86_64-mpc                      [###############################] 100%
    ( 4/39) installing mingw-w64-x86_64-libwinpthread-git        [###############################] 100%
    ( 5/39) installing mingw-w64-x86_64-gcc-libs                 [###############################] 100%
    ( 6/39) installing mingw-w64-x86_64-pkgconf                  [###############################] 100%
    ( 7/39) installing mingw-w64-x86_64-c-ares                   [###############################] 100%
    ( 8/39) installing mingw-w64-x86_64-brotli                   [###############################] 100%
    ( 9/39) installing mingw-w64-x86_64-expat                    [###############################] 100%
    (10/39) installing mingw-w64-x86_64-libiconv                 [###############################] 100%
    (11/39) installing mingw-w64-x86_64-gettext                  [###############################] 100%
    (12/39) installing mingw-w64-x86_64-libunistring             [###############################] 100%
    (13/39) installing mingw-w64-x86_64-libidn2                  [###############################] 100%
    (14/39) installing mingw-w64-x86_64-libpsl                   [###############################] 100%
    (15/39) installing mingw-w64-x86_64-zlib                     [###############################] 100%
    (16/39) installing mingw-w64-x86_64-zstd                     [###############################] 100%
    (17/39) installing mingw-w64-x86_64-libtasn1                 [###############################] 100%
    (18/39) installing mingw-w64-x86_64-libffi                   [###############################] 100%
    (19/39) installing mingw-w64-x86_64-p11-kit                  [###############################] 100%
    (20/39) installing mingw-w64-x86_64-ca-certificates          [###############################] 100%
    (21/39) installing mingw-w64-x86_64-openssl                  [###############################] 100%
    (22/39) installing mingw-w64-x86_64-libssh2                  [###############################] 100%
    (23/39) installing mingw-w64-x86_64-jansson                  [###############################] 100%
    (24/39) installing mingw-w64-x86_64-jemalloc                 [###############################] 100%
    (25/39) installing mingw-w64-x86_64-xz                       [###############################] 100%
    (26/39) installing mingw-w64-x86_64-libxml2                  [###############################] 100%
    Optional dependencies for mingw-w64-x86_64-libxml2
        mingw-w64-x86_64-python: Python bindings
    (27/39) installing mingw-w64-x86_64-nghttp2                  [###############################] 100%
    (28/39) installing mingw-w64-x86_64-curl                     [###############################] 100%
    (29/39) installing mingw-w64-x86_64-jsoncpp                  [###############################] 100%
    (30/39) installing mingw-w64-x86_64-bzip2                    [###############################] 100%
    (31/39) installing mingw-w64-x86_64-libb2                    [###############################] 100%
    (32/39) installing mingw-w64-x86_64-lz4                      [###############################] 100%
    (33/39) installing mingw-w64-x86_64-libtre-git               [###############################] 100%
    (34/39) installing mingw-w64-x86_64-libsystre                [###############################] 100%
    (35/39) installing mingw-w64-x86_64-libarchive               [###############################] 100%
    (36/39) installing mingw-w64-x86_64-libuv                    [###############################] 100%
    (37/39) installing mingw-w64-x86_64-rhash                    [###############################] 100%
    (38/39) installing mingw-w64-x86_64-ninja                    [###############################] 100%
    (39/39) installing mingw-w64-x86_64-cmake                    [###############################] 100%
    Optional dependencies for mingw-w64-x86_64-cmake
        mingw-w64-x86_64-qt6-base: CMake Qt GUI
        mingw-w64-x86_64-emacs: for cmake emacs mode
    ```
    **Hit `Y` then `<enter>`**
    ```
    pacman -S mingw-w64-x86_64-clang
    ```
    ```
    resolving dependencies...
    looking for conflicting packages...

    Packages (9) mingw-w64-x86_64-binutils-2.39-2  mingw-w64-x86_64-crt-git-10.0.0.r68.g6eb571448-1
                mingw-w64-x86_64-gcc-12.2.0-1  mingw-w64-x86_64-headers-git-10.0.0.r68.g6eb571448-1
                mingw-w64-x86_64-isl-0.25-1  mingw-w64-x86_64-llvm-14.0.6-4
                mingw-w64-x86_64-windows-default-manifest-6.4-4
                mingw-w64-x86_64-winpthreads-git-10.0.0.r68.g6eb571448-1
                mingw-w64-x86_64-clang-14.0.6-4

    Total Download Size:    164.73 MiB
    Total Installed Size:  1204.46 MiB

    :: Proceed with installation? [Y/n]
    ```
    **Hit `Y` then `<enter>`**
    ```
    :: Retrieving packages...
    mingw-w64-x86_64-headers-g...     5.6 MiB  5.03 MiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-crt-git-1...     3.3 MiB   636 KiB/s 00:05 [###############################] 100%
    mingw-w64-x86_64-isl-0.25-...  1396.6 KiB   369 KiB/s 00:04 [###############################] 100%
    mingw-w64-x86_64-binutils-...     5.9 MiB   520 KiB/s 00:12 [###############################] 100%
    mingw-w64-x86_64-winpthrea...    39.3 KiB  54.3 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-windows-d...     3.1 KiB  4.02 KiB/s 00:01 [###############################] 100%
    mingw-w64-x86_64-gcc-12.2....    28.3 MiB  1148 KiB/s 00:25 [###############################] 100%
    mingw-w64-x86_64-clang-14....    47.4 MiB   861 KiB/s 00:56 [###############################] 100%
    mingw-w64-x86_64-llvm-14.0...    72.9 MiB   955 KiB/s 01:18 [###############################] 100%
    Total (9/9)                     164.7 MiB  2.08 MiB/s 01:19 [###############################] 100%
    (9/9) checking keys in keyring                               [###############################] 100%
    (9/9) checking package integrity                             [###############################] 100%
    (9/9) loading package files                                  [###############################] 100%
    (9/9) checking for file conflicts                            [###############################] 100%
    (9/9) checking available disk space                          [###############################] 100%
    :: Processing package changes...
    (1/9) installing mingw-w64-x86_64-llvm                       [###############################] 100%
    (2/9) installing mingw-w64-x86_64-binutils                   [###############################] 100%
    (3/9) installing mingw-w64-x86_64-headers-git                [###############################] 100%
    (4/9) installing mingw-w64-x86_64-crt-git                    [###############################] 100%
    (5/9) installing mingw-w64-x86_64-isl                        [###############################] 100%
    (6/9) installing mingw-w64-x86_64-windows-default-manifest   [###############################] 100%
    (7/9) installing mingw-w64-x86_64-winpthreads-git            [###############################] 100%
    (8/9) installing mingw-w64-x86_64-gcc                        [###############################] 100%
    (9/9) installing mingw-w64-x86_64-clang                      [###############################] 100%
    ```
    [Optional] **Close the shell**

6. Open an `MSYS MinGW x64` shell, and type the following:
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/Users/stephen.creswell
    $ cd <path-to-gimli-clone>
    ```
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src/gimli
    $ cmake -B build-windows -G Ninja
    ```
    ```
    -- The C compiler identification is Clang 14.0.6
    -- The CXX compiler identification is Clang 14.0.6
    -- Detecting C compiler ABI info
    -- Detecting C compiler ABI info - done
    -- Check for working C compiler: C:/usr/bin/msys64/mingw64/bin/clang.exe - skipped
    -- Detecting C compile features
    -- Detecting C compile features - done
    -- Detecting CXX compiler ABI info
    -- Detecting CXX compiler ABI info - done
    -- Check for working CXX compiler: C:/usr/bin/msys64/mingw64/bin/clang++.exe - skipped
    -- Detecting CXX compile features
    -- Detecting CXX compile features - done
    -- Performing Test HAVE_FFI_CALL
    -- Performing Test HAVE_FFI_CALL - Success
    -- Found FFI: C:/usr/bin/msys64/mingw64/lib/libffi.dll.a
    -- Found ZLIB: C:/usr/bin/msys64/mingw64/lib/libz.dll.a (found version "1.2.12")
    -- Found LibXml2: C:/usr/bin/msys64/mingw64/lib/libxml2.dll.a (found version "2.9.14")
    -- Configuring done
    -- Generating done
    -- Build files have been written to: C:/var/src/gimli/build
    ```
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src/gimli
    $ cmake --build build-windows
    ```
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src/gimli
    $ cd build-windows
    ```
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src/gimli/build-windows
    $ ./gimli.exe
    ```
    ```
    Usage:
    -       gimli <firmware-binary-path>
    -       gimli <firmware-binary-path> <compile-unit-name.c>
    -       gimli <firmware-binary-path> <compile-unit-name.c> ...

    Notes:
    -       The <compile-unit-name.c> is optional, it is derived from the <firmware-binary-path> if not specified.
    -       The ... represents 1 or more additional <compile-unit-name.c>.
    -       Gimli outputs error messages to `stderr`.
    -       Gimli outputs 'Input JSON File' formatted information to `stdout`.
    ```
    **Note: There are some example 'empty' firmware source files, in the `test` directory, that are built automatically**
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src/gimli/build-windows
    $ ./gimli.exe ./test/c_to_json_1.exe
    ```
    ```
    {
        "regmap": [
            {
                "type": "unsigned short",
                "name": "doe",
                "brief": "A deer, a female deer",
                "address": 1024,
                "byte_size": 2
            }
        ],
        "enums": []
    }
    ```
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src/gimli/build-windows
    $ ./gimli.exe ./test/c_to_json_2.exe
    ```
    ```
    {
        "regmap": [
            {
                "type": "unsigned short",
                "name": "ray",
                "brief": "A drop of golden sun",
                "address": 2048,
                "value_enum": "RAY",
                "byte_size": 2
            }
        ],
        "enums": [
            {
                "name": "RAY",
                "enumerators": [
                    {
                        "name": "RAY_OFF",
                        "value": 0
                    },
                    {
                        "name": "RAY_LOW",
                        "value": 1
                    },
                    {
                        "name": "RAY_MID",
                        "value": 2
                    },
                    {
                        "name": "RAY_HIGH",
                        "value": 3
                    }
                ]
            }
        ]
    }    
    ```
    [Optional] **Exercise for the reader: run remaining ./test/c_to_json_<blah>.exe files thru gimli**

## Getting Started [Linux]

Gimli can be built from a debian docker container ... albeit newer than used by our CI pipelines.

1. Open a `GIT`-aware shell, and type the following

    * **Note: I will open a GIT-bash shell**
    * **Note: I use `/c/var/src` as the root folder for all `git clone ...`s**

    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 ~
    $ cd /c/var/src
    ```
    ```
    stephen.creswell@DESKTOP-EKJ488P MINGW64 /c/var/src
    $ git clone http://gitlab.cm.local/devops/gimli.git
    Cloning into 'gimli'...
    remote: Enumerating objects: 3, done.
    remote: Counting objects: 100% (3/3), done.
    remote: Compressing objects: 100% (2/2), done.
    remote: Total 3 (delta 0), reused 0 (delta 0), pack-reused 0
    Receiving objects: 100% (3/3), done.
    ```

2. Open a `Command Prompt`, and type the following

    * **Note: the `docker run` command-line omits the `--rm` option so the container can be resumed**
    ```
    C:\Users\stephen.creswell>docker pull debian:sid
    ```
    ```
    TODO
    ```
    ```
    docker run -v <path-to-gimli-clone>:<path-to-gimli-mount> -it debian:sid bash
    ```
    * **Note: I would set `<path-to-gimli-clone>` to `C:\var\src\gimli`**
    * **Note: I would set `<path-to-gimli-mount>` to `/var/src/gimli`**

3. At the docker `bash` prompt, type the following
    
    * **Note: this will update the package database**

    ```
    root@0081f60bd526:/# apt-get update
    ```
    ```
    Get:1 http://deb.debian.org/debian sid InRelease [192 kB]
    Get:2 http://deb.debian.org/debian sid/main amd64 Packages [9347 kB]
    Fetched 9539 kB in 2s (5133 kB/s)   
    Reading package lists... Done
    ```

4. At the docker `bash` prompt, type the following
    
    * **Note: this will install the `wget` tool**
    ```
    root@0081f60bd526:/# apt-get install wget
    ```
    ```
    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    .
    .
    .
    0 added, 0 removed; done.
    Running hooks in /etc/ca-certificates/update.d...
    done.
    ```

5. At the docker `bash` prompt, type the following
    
    * **Note: this will install the `unzip` tool**
    ```
    root@0081f60bd526:/# apt-get install unzip
    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    .
    .
    .
    Unpacking unzip (6.0-27) ...
    Setting up unzip (6.0-27) ...
    ```

6. At the docker `bash` prompt, type the following
    
    * **Note: this will install the `cmake` build tool**
    ```
    root@0081f60bd526:/# apt-get install cmake
    ```
    ```
    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    .
    .
    .
    Setting up binutils (2.38.90.20220713-2) ...
    Setting up libtirpc-dev:amd64 (1.3.3+ds-1) ...
    Setting up gcc-12 (12.2.0-1) ...
    Setting up libnsl2:amd64 (1.3.0-2) ...
    Setting up cmake (3.24.1-1) ...
    Setting up gcc (4:12.1.0-3) ...
    Setting up libnsl-dev:amd64 (1.3.0-2) ...
    Setting up libc6-dev:amd64 (2.34-4) ...
    Processing triggers for libc-bin (2.34-4) ...
    Processing triggers for sgml-base (1.30) ...
    Setting up libfontconfig1:amd64 (2.13.1-4.4) ...
    Setting up libgd3:amd64 (2.3.3-6) ...
    Setting up libc-devtools (2.34-4) ...
    Processing triggers for libc-bin (2.34-4) ...
    ```
7. At the docker `bash` prompt, type the following
    
    * **Note: this will fetch and install the `ninja` build tool**
    ```
    root@0081f60bd526:/# cd /usr/bin
    ```
    ```
    root@0081f60bd526:/usr/bin# wget https://github.com/ninja-build/ninja/releases/download/v1.11.0/ninja-linux.zip
    ```
    ```
    Saving to: 'ninja-linux.zip'
    .
    .
    .
    2022-08-24 07:58:19 (14.8 MB/s) - 'ninja-linux.zip' saved [119182/119182]
    ```
    ```
    root@0081f60bd526:/usr/bin# unzip ninja-linux.zip
    ```
    ```
    Archive:  ninja-linux.zip
    inflating: ninja
    ```
    ```            
    root@0081f60bd526:/usr/bin# rm ninja-linux.zip
    ```

8. At the docker `bash` prompt, type the following
    
    * **Note: this will install the `clang-14` tools**
    ```
    root@0081f60bd526:/usr/bin# apt-get install clang-14
    ```
    ```
    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    .
    .
    .
    ```

9. At the docker `bash` prompt, type the following
    
    * **Note: this will create symbolic links to `clang-14` and `clang++-14` without the `-14` suffix**

    ```
    root@0081f60bd526:/usr/bin# ln -s clang-14 clang
    ```
    ```
    root@0081f60bd526:/usr/bin# ln -s clang++-14 clang++
    ```

10. At the docker `bash` prompt, type the following
    
    * **Note: this will install the `llvm-dev` development headers & libraries**

    ```
    root@0081f60bd526:/usr/bin# apt-get install llvm-dev-14
    ```
    ```
    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    E: Unable to locate package llvm-dev-14
    root@0081f60bd526:/var/src/gimli# apt search llvm-dev   
    Sorting... Done
    Full Text Search... Done
    llvm-dev/unstable 1:14.0-55.1 amd64
    Low-Level Virtual Machine (LLVM), libraries and headers
    ```

11. At the docker `bash` prompt, type the following

    * **Note: this will install the `zlib` development headers, the `zlib` library is already installed**
    ```
    root@0081f60bd526:/usr/bin# apt-get install zlib1g-dev
    ```
    ```
    Reading package lists... Done
    Building dependency tree... Done
    Reading state information... Done
    The following NEW packages will be installed:
    zlib1g-dev
    0 upgraded, 1 newly installed, 0 to remove and 2 not upgraded.
    Need to get 193 kB of archives.
    After this operation, 592 kB of additional disk space will be used.
    Get:1 http://deb.debian.org/debian sid/main amd64 zlib1g-dev amd64 1:1.2.11.dfsg-4.1 [193 kB]
    Fetched 193 kB in 0s (3468 kB/s)  
    debconf: delaying package configuration, since apt-utils is not installed
    Selecting previously unselected package zlib1g-dev:amd64.
    (Reading database ... 22550 files and directories currently installed.)
    Preparing to unpack .../zlib1g-dev_1%3a1.2.11.dfsg-4.1_amd64.deb ...
    Unpacking zlib1g-dev:amd64 (1:1.2.11.dfsg-4.1) ...
    Setting up zlib1g-dev:amd64 (1:1.2.11.dfsg-4.1) ...
    ```

12. At the docker `bash` prompt, type the following

    * **Note: this will build gimli**
    ```
    root@0081f60bd526:/usr/bin# cd <path-to-gimli-mount>
    ```
    ```
    root@0081f60bd526:/var/src/gimli# cmake -B build-linux -G Ninja -DCMAKE_SYSTEM_NAME=Linux
    -- The C compiler identification is Clang 14.0.6
    -- The CXX compiler identification is Clang 14.0.6
    -- Detecting C compiler ABI info
    -- Detecting C compiler ABI info - done
    -- Check for working C compiler: /usr/bin/clang - skipped
    -- Detecting C compile features
    -- Detecting C compile features - done
    -- Detecting CXX compiler ABI info
    -- Detecting CXX compiler ABI info - done
    -- Check for working CXX compiler: /usr/bin/clang++ - skipped
    -- Detecting CXX compile features
    -- Detecting CXX compile features - done
    -- Found ZLIB: /usr/lib/x86_64-linux-gnu/libz.so (found version "1.2.11") 
    -- Performing Test HAVE_FFI_CALL
    -- Performing Test HAVE_FFI_CALL - Success
    -- Found FFI: /usr/lib/x86_64-linux-gnu/libffi.so  
    -- Performing Test Terminfo_LINKABLE
    -- Performing Test Terminfo_LINKABLE - Success
    -- Found Terminfo: /usr/lib/x86_64-linux-gnu/libtinfo.so  
    -- Found LibXml2: /usr/lib/x86_64-linux-gnu/libxml2.so (found version "2.9.14") 
    -- Configuring done
    -- Generating done
    -- Build files have been written to: /var/src/gimli/build-linux
    ```
    ```
    root@0081f60bd526:/var/src/gimli# cmake --build build-linux/
    ```
    ```
    [0/1] Re-running CMake...
    -- Configuring done
    -- Generating done
    -- Build files have been written to: /var/src/gimli/build-linux
    [1/1] Linking CXX executable gimli
    ```
