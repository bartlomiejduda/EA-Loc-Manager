"""
Copyright © 2025  Bartłomiej Duda
License: GPL-3.0 License
"""

import argparse
import os
import sys
from typing import List

from reversebox.common.logger import get_logger
from reversebox.io_files.file_handler import FileHandler

logger = get_logger(__name__)

control_codes_mapping: dict = {
    b'\x1B\x68': b'<COLOR_CODE>',
    b'\x80': b'<LOC_KEY1>',
    b'\x86': b'<LOC_KEY2>',
    b'\x8A': b'<LOC_KEY3>',
    b'\x8F': b'<LOC_KEY4>',
    b'\x90': b'<LOC_KEY5>',
    b'\x83': b'<LOC_KEY6>',
    b'\x81': b'<LOC_KEY7>',
    b'\x82': b'<LOC_KEY8>',
    b'\x88': b'<LOC_KEY9>',
    b'\x85': b'<LOC_KEY10>',
    b'\x87': b'<LOC_KEY11>',
    b'\xA9': b'<COPYRIGHT_CODE>',
}

control_codes_backward_mapping = {v: k for k, v in control_codes_mapping.items()}


def export_data(loc_file_path: str, ini_file_path: str, string_encoding: str) -> None:
    """
    Function for exporting data
    """
    logger.info(f"Starting export data from \"{os.path.basename(loc_file_path)}\" file...")
    logger.info(f"Text encoding set to: {string_encoding}")

    loc_file = FileHandler(loc_file_path, "rb")
    total_file_size: int = loc_file.get_file_size()
    if total_file_size < 4:
        raise Exception("LOC file is too small!")

    chunk_signature: bytes = loc_file.read_bytes(4)

    if chunk_signature != b'LOCH':
        raise Exception("Invalid LOCH chunk signature!")

    ini_file = open(ini_file_path, "wt", encoding=string_encoding)

    loc_file.read_uint32()  # chunk size
    flags: int = loc_file.read_uint32()
    number_of_locl_chunks = loc_file.read_uint32()
    locl_chunk_offsets: List[int] = []
    for i in range(number_of_locl_chunks):
        locl_offset: int = loc_file.read_uint32()
        locl_chunk_offsets.append(locl_offset)

    if flags == 1:
        chunk_signature = loc_file.read_bytes(4)  # chunk signature (LOCI)
        if chunk_signature != b'LOCI':
            raise Exception("Invalid LOCI chunk signature!")
        loc_file.read_uint32()  # chunk size
        index_count: int = loc_file.read_uint32()  # index count
        loc_file.read_uint32()  # nulls
        for i in range(index_count):
            loc_file.read_uint16()
            loc_file.read_uint16()

    for i in range(number_of_locl_chunks):
        locl_start_offset: int = loc_file.get_position()
        chunk_signature = loc_file.read_bytes(4)  # chunk signature (LOCL)
        if chunk_signature != b'LOCL':
            raise Exception("Invalid LOCL chunk signature!")

        locl_unique_id: str = f"LOCL_CHUNK_{i}"
        ini_file.write(f"[{locl_unique_id}]\n")

        locl_chunk_size: int = loc_file.read_uint32()  # chunk size
        loc_file.read_uint32()  # nulls
        number_of_strings: int = loc_file.read_uint32()
        string_offset_list: List[int] = []
        locl_end_offset: int = locl_start_offset + locl_chunk_size

        for j in range(number_of_strings):
            string_offset: int = loc_file.read_uint32()
            string_offset_list.append(string_offset + locl_chunk_offsets[i])

        string_offset_list.append(locl_end_offset)

        strings_list: List[str] = []
        for s in range(number_of_strings):
            string_start_position: int = string_offset_list[s]
            string_end_position: int = string_offset_list[s+1]
            string_length: int = string_end_position - string_start_position

            loc_file.seek(string_start_position)
            string_entry_bytes: bytes = loc_file.read_bytes(string_length)
            for k, v in control_codes_mapping.items():
                string_entry_bytes = string_entry_bytes.replace(k, v)

            while 1:
                try:
                    # try to decode as it is
                    string_entry: str = string_entry_bytes.decode(string_encoding, errors="strict").replace("\n", "\\n").rstrip('\x00')
                    break
                except Exception:
                    # remove 1 padding byte from string
                    string_entry_bytes = string_entry_bytes[:-1]

            # logger.info(f"[{string_start_position}] AAA: " + string_entry)
            unique_string_id: str = locl_unique_id + f"_STRING_{s}"
            strings_list.append(string_entry)
            ini_file.write(unique_string_id + "=" + string_entry + "\n")

    logger.info(f"Text from file \"{os.path.basename(loc_file_path)}\" exported successfully...")
    return


VERSION_NUM = "v1.0"
EXE_FILE_NAME = f"ea_loc_manager_{VERSION_NUM}.exe"
PROGRAM_NAME = f'EA Loc Manager {VERSION_NUM}'


def main():
    """
    Main function of this program.
    """

    parser = argparse.ArgumentParser(prog=EXE_FILE_NAME, description=PROGRAM_NAME)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--export", nargs=2, metavar=("loc_file_path", "ini_file_path"), help="Export from LOC file")
    group.add_argument("-i", "--import", nargs=2, metavar=("ini_file_path", "loc_file_path"), help="Import to LOC file")

    parser.add_argument("-enc", "--encoding",
                        default="utf8",
                        choices=["utf8", "utf16", "latin-1"],
                        help="Encoding to use (default: utf8)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    logger.info(f"Running {PROGRAM_NAME}...")

    if getattr(args, "export"):
        loc_path, ini_path = getattr(args, "export")
        encoding_type: str = getattr(args, "encoding")

        if not os.path.isfile(loc_path):
            logger.error(f"[ERROR] File does not exist: {loc_path}")
            sys.exit(1)
        export_data(loc_path, ini_path, encoding_type)

    elif getattr(args, "import"):
        ini_path, loc_path = getattr(args, "import")
        if not os.path.isfile(ini_path):
            logger.error(f"[ERROR] File does not exist: {ini_path}")
            sys.exit(1)
        if not os.path.isfile(loc_path):
            logger.error(f"[ERROR] File does not exist: {loc_path}")
            sys.exit(1)
        # TODO - import function
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
