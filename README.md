# sqlite3backup 

Python script and module to back up sqlite3 database using `sqlite3`'s [`backup`](https://docs.python.org/3.8/library/sqlite3.html) function. 

To run the script, pass the absolute paths of the database file you want backed up and the file you want it backed up to. If the backup file does not exist and its parent directory is valid, then the backup file will be created on the first run.

```sh
python3 sqlite3backup.py  ~/myproject/src.db ~/myproject/backup.db
```

A `backup.log` file is created in the directory where the script is launched.
