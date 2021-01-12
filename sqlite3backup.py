#!/usr/bin/env python3
"""
Python script and module to back-up sqlite3 database using `sqlite3`'s backup function. 

To use on a console pass the absolute paths of the database file you want backed up and the file 
you want it backed up to. If destination file does not exist and the parent directory is good, 
the it will be created on the first run.

>> python3 sqlite3backup.py  ~/myproject/src.db ~/myproject/backup.db

A backup.log file is created in the directory where the script is launched.
"""
import os
import sys
import argparse
import pathlib
import platform
import logging
import sqlite3

# sqlite3 doesn't work on versions less than 3.7.
MIN_VERSION = 3.7


# Private API
def _version_ok(min_version : float = MIN_VERSION) -> bool:
    """Sqlite3.backup only exists in Python versions 3.7 or greater."""
    major, minor, _ = platform.python_version_tuple()
    curr_version =  int(major) + int(minor) / 10 
    return curr_version >= min_version


def _parse_args() -> (pathlib.Path, pathlib.Path):
    parser = argparse.ArgumentParser(description='Backup sqlite3 database.')
    parser.add_argument('src_path', type=pathlib.Path)
    parser.add_argument('dest_path', type=pathlib.Path)
    args = parser.parse_args()
    return  args.src_path, args.dest_path


def _check_files(srcdb : pathlib.Path, backupdb : pathlib.Path) -> bool:
    # Check file to be backed up.
    if not srcdb.exists() or not srcdb.is_file():
        raise FileNotFoundError(f"Source database file does not exist or is not a file:\n{str(srcdb)}")
    if not os.access(srcdb, os.R_OK):
        raise PermissionError(f"Read access to file denied:\n{str(srcdb)}")
    # Check backup copy.
    if backupdb.exists():
        if not os.access(backupdb, os.W_OK):
            raise PermissionError(f"Write access to file denied:\n{str(backupdb)}")
        else:
            if not os.access(backupdb.parent, os.W_OK):
                err = f"Write access to parent directory denied:\n{str(backupdb.parent)}"
                raise PermissionError(err)
    return True

    
# Public API
def backup_database(srcdb : pathlib.Path, backupdb : pathlib.Path):
    """Wrapper function that backups SQLite database even if it's being accessed by other clients 
    or concurrently by the same connection (so says documentation). Entire source databases
    copied in single step.

    Args:
        srcdb: Path object that represents file path to database file that is to be backed up.
        backupdb: Path object that represents the file path where the backup file resides.
    """
    # Backup database.
    if _check_files(srcdb, backupdb):
        con = sqlite3.connect(srcdb)
        bck = sqlite3.connect(backupdb)
        with bck:
            con.backup(bck)
        bck.close()
        con.close()


def run(test_params=None):
    """Runs backup script.

    Args:
        test_params: Tuple that contain two Path objects representing the source and destination 
                     paths to the original and backup database files respectively. For 
                     unit-testing purposes only.

    Raises:
        SystemExit: in case a Python3 version less than 3.7 is being used.
    """
    if not _version_ok():
            errstr = f"Unable to backup sqlite3 db. Minimum Python version required: {MIN_VERSION}"
            raise SystemExit(errstr)
    
    # test_params for unit-testing purposes.
    src_path, dest_path = _parse_args() if not test_params else test_params
    backup_database(srcdb=src_path, backupdb=dest_path)
   

# Main
if __name__ == "__main__":
    try:
        logging.basicConfig(filename='backup.log', level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')
        run()
        logging.info("Backup complete. No errors.")
    except (SystemExit, FileNotFoundError, sqlite3.OperationalError) as e: 
        print(f"{type(e).__name__}: {e}")
        logging.error(f"{type(e).__name__}: {e}")
    # Catches everything but SystemExit, KeyboardInterrupt and GeneratorExit exceptions.
    except Exception as e:
        logging.error(f"{type(e).__name__}: {e}")
    
    
 
   
    
    
    

