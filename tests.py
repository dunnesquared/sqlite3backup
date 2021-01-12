"""Unit tests public API of sqlite3backup.py."""

import unittest
import os
import stat
import pathlib
import sqlite3


import sqlite3backup as sq3bckup

# Need to have some fake app.db file if uploading to github

class Sql3BackupTests(unittest.TestCase):

    # Database stuff ----------------------------------------------------------------------------
    def create_table(self):
        cursor = self.conn.cursor()
        create_query = '''CREATE TABLE ACTORS_TNG
        ([generate_id] INTEGER PRIMARY KEY,
        [Actor] text,
        [Role] text)
        '''
        cursor.execute(create_query)
        self.conn.commit()
    
    def insert_record(self, actor: str, role: str) -> str:
        return  f"INSERT INTO actors_tng (actor, role) VALUES('{actor}', '{role}')"

    def populate_table(self):
        cursor = self.conn.cursor()
        cursor.execute(self.insert_record('Patrick Stewart', 'Captain Jean-Luc Picard'))
        cursor.execute(self.insert_record('Jonathan Frakes', 'First Officer William T. Riker'))
        cursor.execute(self.insert_record('Brent Spiner', 'Commander Data'))
        self.conn.commit()
    
    def drop_table(self):
        cursor = self.conn.cursor()
        cursor.execute('DROP TABLE actors_tng')
        self.conn.commit()

    # Setup / Tear Down  -------------------------------------------------------------------------
    def setUp(self):
        # Create and populate test database.
        self.conn = sqlite3.connect('test.db')
        self.create_table()
        self.populate_table()
        self.src_db = pathlib.Path('test.db')

        # Dummy backup file to which to copy original data to.
        with open('test-backup.db', 'w'):
            pass
        self.dest_db = pathlib.Path('test-backup.db')
        self.conn_backup = sqlite3.connect('test-backup.db')

        # Dummy file that is not an sqlite3 db file.
        # Need to write something in file for this to work. 
        with open('notdbfile.txt', 'w') as f:
            f.write("Random text!!")
        self.not_db = pathlib.Path('notdbfile.txt')

        # Dummy directory to write database file; make read-only
        self.testdir = pathlib.Path('testdir/')
        self.testdir.mkdir(mode=0o400)

        # Dummy directory path for non-existent directory
        self.dnedir = pathlib.Path('dnedir/')

    def tearDown(self):
        # Remove dummy files.
        if self.not_db.exists():
            self.not_db.unlink()
        if self.dest_db.exists():
            self.dest_db.unlink()
        if self.testdir.exists():
            self.testdir.rmdir()
        
        # Clear database.
        self.drop_table()

        # Close connections
        self.conn.close()
        self.conn_backup.close()
    
    # Tests --------------------------------------------------------------------------------------
    def test_backupdb(self):
        # Normal backup - check data by comparing data from two databases.
        sq3bckup.backup_database(self.src_db, self.dest_db)
        query = 'SELECT * FROM actors_tng'
        cursor_original = self.conn.cursor()
        result_original = cursor_original.execute(query)
        cursor_backup = self.conn_backup.cursor()
        result_backup = cursor_backup.execute(query)
        self.assertEqual(result_original.fetchall(), result_backup.fetchall())
        
        # Src db does not exist
        src_dne = pathlib.Path('dne.db')
        self.assertRaises(FileNotFoundError, sq3bckup.backup_database, src_dne, self.dest_db)

        # Backing up a non-sqlite3 database file
        self.assertRaises(sqlite3.OperationalError, sq3bckup.backup_database, self.not_db, 
                          self.dest_db)
        
        # Writing to file for which permission does not exist.
        os.chmod(self.dest_db, stat.S_IREAD)  # User read-only allowed.
        self.assertRaises(PermissionError, sq3bckup.backup_database, self.src_db, 
                          self.dest_db)
        
        # Writing to directory for which we do not have access.
        self.assertRaises(PermissionError, sq3bckup.backup_database, self.src_db, 
                          self.testdir.joinpath(self.dest_db))
        
        # Writing to a path that does not exist.
        self.assertRaises(sqlite3.OperationalError, sq3bckup.backup_database, self.src_db, 
                          self.dnedir.joinpath(self.dest_db))


# Main -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()