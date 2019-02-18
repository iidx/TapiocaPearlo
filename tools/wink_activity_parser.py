"""
Wink Activity Parser Tool v1.0

Parse wink activity from database.

Developed by Namjun Kim <bunseokbot@gmail.com>
"""

from argparse import ArgumentParser

from utils.logging.log import Log
from utils.database.misc import dict_factory

import sqlite3
import json
import os


class WinkActivityParser(object):
    """Wink database activity parser."""

    def __init__(self, database):
        self.database = database

    def parse(self):
        """Parse activity from database."""
        Log.debug("Extracting activities from database...")

        with sqlite3.connect(self.database) as con:
            con.row_factory = dict_factory
            cur = con.cursor()

            cur.execute("SELECT * FROM Elements WHERE Type='activity'")
            data = cur.fetchall()

        Log.debug("Successfully parsed activities from database.")

        self.save(data)

    def save(self, data):
        """Save activity into elasticsearch."""
        activities = [json.loads(activity['Json']) for activity in data]

    def __del__(self):
        del self


def main(args):
    """Main method for parsing dairies."""
    if not os.path.exists(args.database):
        Log.error("persistenceDB file not found.", trace_exc=False)
        return

    wap = WinkActivityParser(args.database)
    wap.parse()
    del wap


if __name__ == '__main__':
    parser = ArgumentParser(description="Wink Activity parser v1.0")
    parser.add_argument("-d", "--database", dest="database", type=str, required=True,
                        help="persistenceDB database file path")

    args = parser.parse_args()
    main(args)
