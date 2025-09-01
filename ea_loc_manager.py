"""
Copyright © 2025  Bartłomiej Duda
License: GPL-3.0 License
"""

import argparse
import os
import sys
from reversebox.common.logger import get_logger
from reversebox.io_files.file_handler import FileHandler

logger = get_logger(__name__)


def export_data(loc_file_path: str, ini_file_path: str) -> None:
    """
    Function for exporting data
    """
    logger.info("Starting export data...")

    loc_file = FileHandler(loc_file_path, "rb")
    signature = loc_file.read_str(4, "utf8")

    if signature != "LOCH":
        raise Exception("Invalid EA Loc file!")


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
