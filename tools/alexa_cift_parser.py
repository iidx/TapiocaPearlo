"""
Alexa CIFT database tool parser v1.0

Extract information from alexa cift tool's exported database.

Developed by Namjun Kim <bunseokbot@gmail.com>
"""

from argparse import ArgumentParser
from datetime import datetime

from utils.logging.log import Log
from utils.database.misc import dict_factory
from utils.elastic import Elastic

import sqlite3
import os


class CIFTDatabaseParser(object):
    """Parser for parse information from cift database."""

    def __init__(self, database, timezone):
        self.database = database
        self.timezone = timezone

    def parse(self):
        """Parse timeline from database."""
        Log.debug("Extracting activities from database...")

        with sqlite3.connect(self.database) as con:
            con.row_factory = dict_factory
            cur = con.cursor()

            cur.execute("SELECT * FROM TIMELINE")
            activities = cur.fetchall()

        documents = []

        for activity in activities:
            documents.append({
                'time': self.convert_time(activity['date'], activity['time']),
                'user': activity['user'],
                'short': activity['short'],
                'desc': activity['desc'],
                'notes': activity['notes']
            })

        Log.info("Successfully parsed data from database.")

        self.save(documents)

    def save(self, documents):
        with Elastic(index='alexa', doc_type='activity') as elastic:
            elastic.upload(documents, 'time')

        Log.info("Successfully uploaded data into elasticsearch.")

    def convert_time(self, date, time):
        """Convert splited time into datetime."""
        return datetime.strptime(
            f"{date} {time} {self.timezone}", "%Y-%m-%d %H:%M:%S.%f %Z%z")


    def __del__(self):
        del self


def main(args):
    """Main method for parsing activities."""
    if not os.path.exists(args.database):
        Log.error("cift_amazon_alexa.db file not found.", trace_exc=False)
        return

    cdp = CIFTDatabaseParser(args.database, args.timezone)
    cdp.parse()
    del cdp


if __name__ == '__main__':
    parser = ArgumentParser(description="Amazon Alexa CIFT database parser v1.0")
    parser.add_argument("-d", "--database", dest="database", type=str, required=True,
                        help="cift_amazon_alexa.db database file path")
    parser.add_argument("-t", "--timezone", dest="timezone", type=str, required=True,
                        help="Timezone which used at Amazon Alexa. ex) UTC+2 -> UTC+0200")

    args = parser.parse_args()
    main(args)
