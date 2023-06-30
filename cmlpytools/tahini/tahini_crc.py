"""
Repository class to generate a binary file with filesize and CRC metadata
"""
import sys
import os
import crcmod


class TahiniCrc():
    """Implements `tahini crc ...` sub-command
    """

    @staticmethod
    def main(input_file_path: str, verbose: bool) -> None:
        """Generate CRC-appended Griffin binary image and send to stdout

        Args:
            input_file_path (str): FW Binary file path to be processed
            verbose (bool): If True, also write process logs to `stderr`
        """

        if not os.path.exists(input_file_path):
            sys.stderr.write("File '" + input_file_path + "' does not exist\n")
        else:
            # Step 1: Get the file input
            try:
                with open(input_file_path, 'rb') as infile:
                    file_contents = infile.read()
                    infile.close()
            except IOError:
                sys.stderr.write("Error while opening input file\n")

            # Step 2: Produce output data by manipulating the input data
            file_contents_bytes = bytearray(file_contents)
            if verbose:
                sys.stderr.write("Input .bin image dump\n")
                sys.stderr.write(" ".join(f"{b:02x}" for b in file_contents_bytes) + "\n")

            # Step 2.1: Insert the image size at offset 0xC0. Griffin requires a minimum 48-position
            # vector table, and the image size is inserted in a reserved position after the table.
            # First do a couple of sanity checks
            file_size = os.path.getsize(input_file_path)
            assert file_size >= 0xC4, "Error: Input file too small"
            size_field = int.from_bytes(file_contents_bytes[0xC0:0xC4], byteorder='little')
            assert size_field == 0, "Error: Input file contains non-zero size placeholder"

            # Now update the dataset
            sys.stderr.write(f"File size {file_size} bytes (0x{file_size:08x})\n")
            file_size_bytes = file_size.to_bytes(4, byteorder='little')
            if verbose:
                sys.stderr.write("Size LE\n")
                sys.stderr.write(" ".join(f"{b:02x}" for b in file_size_bytes) + "\n")
            file_contents_bytes[0xC0] = file_size_bytes[0]
            file_contents_bytes[0xC1] = file_size_bytes[1]
            file_contents_bytes[0xC2] = file_size_bytes[2]
            file_contents_bytes[0xC3] = file_size_bytes[3]

            # Step 2.2: Calculate CRC over the entire image that now contains its own size
            # CRCmod seems to to something unexpected with the final xor (xorOut),
            # so this final step is done externally instead to produce the expected CRC32
            crc32_func = crcmod.mkCrcFun(0x1C9D204F5, initCrc=0xFFFFFFFF, rev=True, xorOut=0)
            crc32 = crc32_func(file_contents_bytes) ^ 0xFFFFFFFF
            sys.stderr.write(f"CRC value is 0x{crc32:08x}\n")

            # Step 2.3: Insert the CRC at the end of the file, little endian
            crc32_bytes = crc32.to_bytes(4, byteorder='little')
            if verbose:
                sys.stderr.write("CRC LE\n")
                sys.stderr.write(" ".join(f"{b:02x}" for b in crc32_bytes) + "\n")
            file_contents_bytes = file_contents_bytes + crc32_bytes

            # Step 3: Produce the output, send to stdout
            sys.stdout.write(file_contents_bytes)
