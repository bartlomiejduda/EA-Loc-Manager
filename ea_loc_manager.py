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
    b'\x1B\x68': b'<LOC_INIT_CODE>',
    b'\x80': b'<LOC_CROSS_BUTTON>',
    b'\x81': b'<LOC_CIRCLE_BUTTON>',
    b'\x82': b'<LOC_SQUARE_BUTTON>',
    b'\x83': b'<LOC_TRIANGLE_BUTTON>',
    b'\x85': b'<LOC_L2_BUTTON>',
    b'\x86': b'<LOC_R1_BUTTON>',
    b'\x87': b'<LOC_R2_BUTTON>',
    b'\x88': b'<LOC_KEY8>',
    b'\x8A': b'<LOC_HAND_ICON>',
    b'\x8F': b'<LOC_KEY10>',
    b'\x90': b'<LOC_KEY11>',
}

control_codes_backward_mapping = {v: k for k, v in control_codes_mapping.items()}


def export_data(loc_file_path: str, ini_file_path: str, string_encoding: str) -> None:
    """
    Function for exporting data
    """
    logger.info(f"Starting export data from \"{os.path.basename(loc_file_path)}\" file to \"{os.path.basename(ini_file_path)}\" file...")
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

    logger.info(f"Texts from file \"{os.path.basename(loc_file_path)}\" exported to \"{os.path.basename(ini_file_path)}\" file successfully...")
    return


def import_data(ini_file_path: str, loc_file_path: str, string_encoding: str) -> None:
    """
    Function for importing data
    """
    logger.info(f"Starting import data from \"{os.path.basename(ini_file_path)}\" file to \"{os.path.basename(loc_file_path)}\" file...")
    logger.info(f"Text encoding set to: {string_encoding}")

    ini_file = open(ini_file_path, "rt", encoding=string_encoding)

    # process INI file
    locl_chunks_list: list = []
    locl_chunks_count: int = 0
    for ini_line in ini_file:
        if ini_line.startswith("#"):
            continue
        elif ini_line.startswith("["):
            locl_binary_strings: list[bytes] = []
            locl_chunks_list.append(locl_binary_strings)
            locl_chunks_count += 1
        else:
            ini_text: str = ini_line.rstrip("\n").split("=")[-1]
            ini_text_binary: bytes = ini_text.encode(encoding=string_encoding, errors="strict")
            for k, v in control_codes_backward_mapping.items():
                ini_text_binary = ini_text_binary.replace(k, v)
            locl_chunks_list[locl_chunks_count-1].append(ini_text_binary)

    # copy binary data
    loc_file = FileHandler(loc_file_path, "rb")
    total_file_size: int = loc_file.get_file_size()
    if total_file_size < 4:
        raise Exception("LOC file is too small!")

    loch_chunk_signature: bytes = loc_file.read_bytes(4)

    if loch_chunk_signature != b'LOCH':
        raise Exception("Invalid LOCH chunk signature!")

    loch_chunk_size: int = loc_file.read_uint32()
    flags: int = loc_file.read_uint32()
    loc_file.seek(0)
    LOCH_CHUNK_DATA: bytes = loc_file.read_bytes(loch_chunk_size)
    LOCI_CHUNK_DATA: bytes = b''

    if flags == 1:
        loci_chunk_offset: int = loc_file.get_position()
        loci_chunk_signature = loc_file.read_bytes(4)  # chunk signature (LOCI)
        if loci_chunk_signature != b'LOCI':
            raise Exception("Invalid LOCI chunk signature!")
        loci_chunk_size: int = loc_file.read_uint32()  # chunk size
        loc_file.seek(loci_chunk_offset)
        LOCI_CHUNK_DATA = loc_file.read_bytes(loci_chunk_size)

    loc_file.close()

    # save LOCH/LOCI chunks in LOC file
    loc_file = FileHandler(loc_file_path, "wb")
    loc_file.write_bytes(LOCH_CHUNK_DATA)
    loc_file.write_bytes(LOCI_CHUNK_DATA)

    # save LOCL chunks in LOC file
    # TODO
    for i in range(locl_chunks_count):
        locl_chunk_offset: int = loc_file.get_position()
        loc_file.write_bytes(b'LOCL')
        loc_file.write_uint32(0)  # chunk size
        loc_file.write_uint32(0)  # language ID
        number_of_strings: int = len(locl_chunks_list[i])
        loc_file.write_uint32(number_of_strings)
        total_all_str_length: int = 0
        for s in range(number_of_strings):
            string_offset: int = locl_chunk_offset + (4 * number_of_strings) + total_all_str_length
            loc_file.write_uint32(string_offset)
            total_all_str_length += len(locl_chunks_list[i][s])
        for ss in range(number_of_strings):
            loc_file.write_bytes(locl_chunks_list[i][ss])

    loc_file.close()
    logger.info(f"Texts from file \"{os.path.basename(ini_file_path)}\" imported to \"{os.path.basename(loc_file_path)}\" file successfully...")
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
                        default="latin-1",
                        choices=["utf8", "utf16", "latin-1"],
                        help="Encoding to use (default: latin-1)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    logger.info(f"Running {PROGRAM_NAME}...")
    encoding_type: str = getattr(args, "encoding")

    if getattr(args, "export"):
        loc_path, ini_path = getattr(args, "export")

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
        import_data(ini_path, loc_path, encoding_type)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
