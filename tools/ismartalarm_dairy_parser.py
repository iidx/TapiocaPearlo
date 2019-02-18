"""
iSmartAlarm dairy parser v1.0

Extract dairy history for generating timeline events.

Developed by Namjun Kim <bunseokbot@gmail.com>
"""

from argparse import ArgumentParser

from utils.logging.log import Log

import sqlite3
import os


class DairyParser(object):
    """Parser for generating timeline from iSmartAlarm Application."""

    def __init__(self, database):
        self.database = database  # iSmartAlarm database

    @staticmethod
    def dict_factory(cursor, row):
        """SQLite row factory for converting into dict type."""
        data = {}
        for idx, col in enumerate(cursor.description):
            data[col[0]] = row[idx]

        return data

    def parse(self):
        """Parse dairies from database."""
        Log.debug("Extracting diaries from database...")

        tables = {
            'CameraDiary': {
                'name': 'TB_CameraDairy',
            },
            'IPUDiary': {
                'name': 'TB_IPUDairy',
            },
            'ISC3Diary': {
                'name': 'TB_ISC3Dairy',
            },
            'SensorDiary': {
                'name': 'TB_SensorDairy',
            }
        }

        # get dairies from database
        with sqlite3.connect(self.database) as con:
            con.row_factory = self.dict_factory
            cur = con.cursor()

            for key in tables.keys():
                name = tables[key]['name']
                cur.execute(f"SELECT * FROM {name}")
                tables[key]['data'] = cur.fetchall()

        Log.debug("Successfully parsed data from database.")

        self.save(tables)

    def save(self, tables):
        """Save history into elasticsearch."""
        for key in tables.keys():
            data = tables[key]['data']

    def __del__(self):
        del self


def main(args):
    """Main method for parsing dairies."""
    if not os.path.exists(args.database):
        Log.error("iSmartAlarm.DB file not found.", trace_exc=False)
        return

    dp = DairyParser(args.database)
    dp.parse()
    del dp


if __name__ == '__main__':
    parser = ArgumentParser(description="iSmartAlarm dairy parser v1.0")
    parser.add_argument("-d", "--database", dest="database", type=str, required=True,
                        help="iSmartAlarm.DB database file path")

    args = parser.parse_args()
    main(args)
