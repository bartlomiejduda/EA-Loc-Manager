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
    b'\x80': b'<HP_KEY1>',
    b'\x86': b'<HP_KEY2>',
    b'\x8A': b'<HP_KEY3>',
    b'\x8F': b'<HP_KEY4>',
    b'\x90': b'<HP_KEY5>',
    b'\x83': b'<HP_KEY6>',
    b'\x81': b'<HP_KEY7>',
    b'\x82': b'<HP_KEY8>',
    b'\x88': b'<HP_KEY9>',
    b'\x85': b'<HP_KEY10>',
    b'\x87': b'<HP_KEY11>',
    b'\xA9': b'<COPYRIGHT_CODE>',
}

control_codes_backward_mapping = {v: k for k, v in control_codes_mapping.items()}


def export_data(loc_file_path: str, ini_file_path: str) -> None:
    """
    Function for exporting data
    """
    logger.info("Starting export data...")

    loc_file = FileHandler(loc_file_path, "rb")
    signature = loc_file.read_str(4, "utf8")

    if signature != "LOCH":
        raise Exception("Invalid EA Loc file!")

    ini_file = open(ini_file_path, "wt")

    loc_file.read_uint32()  # header size
    flags: int = loc_file.read_uint32()
    number_of_locl_chunks = loc_file.read_uint32()
    base_offset: int = loc_file.read_uint32()

    if flags == 1:
        loc_file.read_str(4, "utf8")  # chunk signature (LOCI)
        loc_file.read_uint32()  # chunk size
        loc_file.read_uint32()  # string count
        loc_file.read_uint32()  # nulls

    for i in range(number_of_locl_chunks):
        chunk_signature = loc_file.read_str(4, "utf8")  # chunk signature (LOCL)
        if chunk_signature != "LOCL":
            raise Exception("Invalid LOCL chunk signature!")

        loc_file.read_uint32()  # chunk size
        loc_file.read_uint32()  # language ID
        number_of_strings: int = loc_file.read_uint32()
        string_offset_list: List[int] = []

        for j in range(number_of_strings):
            string_offset: int = loc_file.read_uint32()
            string_offset_list.append(string_offset + base_offset)

        total_file_size: int = loc_file.get_file_size()
        string_offset_list.append(total_file_size)

        strings_list: List[str] = []
        for k in range(number_of_strings):
            string_start_position: int = string_offset_list[k]
            string_end_position: int = string_offset_list[k+1]
            string_length: int = string_end_position - string_start_position

            loc_file.seek(string_start_position)
            string_entry_bytes: bytes = loc_file.read_bytes(string_length)
            for k, v in control_codes_mapping.items():
                string_entry_bytes = string_entry_bytes.replace(k, v)
            string_entry: str = string_entry_bytes.decode("utf8", errors="strict").replace("\n", "\\n")

            strings_list.append(string_entry)
            # TODO
            ini_file.write(string_entry + "\n")

    # TODO

    logger.info("Text exported successfully...")
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

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    logger.info(f"Running {PROGRAM_NAME}...")

    if getattr(args, "export"):
        loc_path, ini_path = getattr(args, "export")
        if not os.path.isfile(loc_path):
            logger.error(f"[ERROR] File does not exist: {loc_path}")
            sys.exit(1)
        export_data(loc_path, ini_path)

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
