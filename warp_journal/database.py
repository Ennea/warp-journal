import logging
import sqlite3
from shutil import copyfile

from .util import get_data_path, show_error
from .enums import ItemType


# convert a bytestring stored in sqlite back to our enum
def convert_reward_type(b):
    return ItemType(int(b))

# register converter for the item type enum
sqlite3.register_converter('ITEM_TYPE', convert_reward_type)


DATABASE_VERSION = 1

class DatabaseConnectionContextManager:
    def __init__(self, database_path):
        self._database_path = database_path
        self._connection = sqlite3.connect(self._database_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self._connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.cursor.close()
        self._connection.close()

        # to not ignore any exceptions that happened inside a with block
        return False

    def commit(self):
        self._connection.commit()

class Database:
    def __init__(self):
        data_path = get_data_path()
        self._database_path = data_path / 'database.sqlite3'

        # create the database if it does not exist yet
        if not self._database_path.exists():
            self._create_database()
        elif self._database_path.is_dir():
            show_error(f'{self._database_path} exists, but is not a file.')

        # the database exists, let's check the version of our data
        logging.info('Checking database version')
        with self._get_database_connection() as db:
            try:
                version = db.cursor.execute('SELECT data FROM meta WHERE name = "version"').fetchall()[0][0]
            except (IndexError, sqlite3.DatabaseError, sqlite3.OperationalError):
                show_error('Could not find version information in the database. The database might be corrupt.')

        # exit if the version does not match. in the future, migrate if version is lower
        if version != DATABASE_VERSION:
            show_error('Unknown database version. Shutting down to not mess with any data.')

        # create a backup
        logging.info('Creating database backup')
        copyfile(self._database_path, data_path / 'database.sqlite3.bak')

    def _get_database_connection(self):
        return DatabaseConnectionContextManager(self._database_path)

    def _create_database(self):
        logging.info('No existing database found, creating new one')

        with self._get_database_connection() as db:
            # create tables
            db.cursor.execute('CREATE TABLE meta (name TEXT PRIMARY KEY, data BLOB)')
            db.cursor.execute('''
                CREATE TABLE warp_history (
                    id INTEGER,
                    uid INTEGER,
                    banner_id INTEGER,
                    banner_type INTEGER,
                    type ITEM_TYPE,
                    rarity INTEGER,
                    time TEXT,
                    item_id INTEGER,
                    name TEXT,
                    UNIQUE (id, uid)
                )
            ''')

            # insert version
            db.cursor.execute('INSERT INTO meta VALUES ("version", ?)', (DATABASE_VERSION,))
            db.commit()

    def get_uids(self):
        with self._get_database_connection() as db:
            uids = db.cursor.execute('SELECT DISTINCT uid FROM warp_history').fetchall()

        for uid in uids:
            yield uid[0]

    def get_warp_history(self, uid):
        with self._get_database_connection() as db:
            warp_history = db.cursor.execute('''
                SELECT
                    id,
                    banner_type,
                    type,
                    rarity,
                    time,
                    name
                FROM warp_history WHERE uid = ? ORDER BY time ASC
            ''', (uid,)).fetchall()

        keys = [ 'id', 'banner_type', 'type', 'rarity', 'time', 'name' ]
        for warp in warp_history:
            yield dict(zip(keys, warp))

    def get_latest_warp_id(self, uid, banner_type):
        with self._get_database_connection() as db:
            try:
                id_ = db.cursor.execute('SELECT MAX(id) FROM warp_history WHERE uid = ? AND banner_type = ?', (uid, banner_type)).fetchone()[0]
            except IndexError:
                id_ = None

        return id_

    def store_warp_history(self, warps):
        if len(warps) == 0:
            return

        logging.info('Storing warp history')
        with self._get_database_connection() as db:
            db.cursor.executemany('''
                INSERT OR IGNORE INTO warp_history
                ( id, uid, banner_id, banner_type, type, rarity, time, item_id, name )
                VALUES
                ( :id, :uid, :banner_id, :banner_type, :type, :rarity, :time, :item_id, :name )
            ''', warps)
            db.commit()
