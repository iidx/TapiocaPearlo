"""
Nest Video Recovery tool v1.0

Extract video frame from database and recovery to mp4 file format.

Developed by Namjun Kim <bunseokbot@gmail.com>
"""

from argparse import ArgumentParser
from pathlib import Path

from utils.logging.log import Log
from utils.elastic import Elastic
from utils.time import to_datetime

import sqlite3
import os


class VideoExtractor(object):
    """Extractor for recovering video frame from Nest Application."""

    def __init__(self, database, output):
        self.database = database
        self.rawvideos = []  # video file list for convert and merge file
        self.videotimes = {}  # video recording time
        self.output = output  # video and log output directory

        # make directory when directory not exist
        if not os.path.exists(output):
            os.mkdir(output)

    def extract(self, merge, add_timeline):
        """Extract frames from database."""
        Log.debug("Extracting videos from database...")

        with sqlite3.connect(self.database) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM frame_raw_data_table")
            rows = cur.fetchall()

        videobuf = ""  # temporary buffer for constructing video
        videoname = ""  # name of video file
        count = 0  # video file counter

        for row in rows:
            if row[4]:
                if videoname:
                    with open(videoname, "wb") as f:
                        f.write(videobuf)
                    self.rawvideos.append(videoname)

                videobuf = row[5]
                videobuf += row[4]
                videobuf += row[6]

                videoname = os.path.join(self.output, f"{count}.tmp")
                self.videotimes[videoname] = [row[0]]

                count += 1
            else:
                videobuf = videobuf + row[6]

                if row[0] not in self.videotimes[videoname]:
                    self.videotimes[videoname].append(row[0])

        if videobuf:
            with open(videoname, "wb") as f:
                f.write(videobuf)
            self.rawvideos.append(videoname)

        Log.info(f"Successfully extrated {count} video files.")

        self.save(merge)

        documents = []

        for filename in self.videotimes.keys():
            runtime = self.videotimes[filename]
            start, end = to_datetime(runtime[0]), to_datetime(runtime[-1])
            filename = os.path.basename(filename).replace('tmp', 'mp4')

            documents.append({
                'start_time': start,
                'end_time': end,
                'filename': filename
            })

        # write history as file
        with open(os.path.join(self.output, 'video_list.txt'), 'w') as f:
            for document in documents:
                f.write(f"{document['filename']}: {document['start_time']} - {document['end_time']}\n")

        # upload to elasticsearch for add timeline
        if add_timeline:
            with Elastic(index='dfrws', doc_type='NestVideo') as elastic:
                elastic.upload(documents)

    def save(self, merge):
        """Convert and save into playable video."""
        Log.info("Converting video file codec format...")

        for video in self.rawvideos:
            os.system(f"ffmpeg -f h264 -r 10 -i {video} -c copy {video.split('.')[0]}.mp4")

            # remove original file
            if os.path.exists(video):
                os.remove(video)

        Log.info("Successfully convert the video file codec.")

        if merge:
            Log.info("Merging videos..")

            videos = '|'.join([video.split('.')[0] + ".mp4" for video in self.rawvideos])
            os.system(f"ffmpeg -f concat -i \"concat:{videos}\" -c copy video.mp4")

            for video in self.rawvideos:
                os.remove(f"{video.split('.')[0]}.mp4")

            Log.info(f"Successfully merged {len(self.rawvideos)} videos.")

    def __del__(self):
        del self

def main(args):
    """Main method for recovering video."""
    # if frame_database file not found
    if not os.path.exists(args.database):
        Log.error("frame_database file not found.", trace_exc=False)
        return

    ve = VideoExtractor(args.database, args.output)
    ve.extract(args.merge, args.add_timeline)
    del ve


if __name__ == "__main__":
    parser = ArgumentParser(description="Nest video recovery tool v1.0")
    parser.add_argument("-d", "--database", dest="database", type=str, required=True,
                        help="frame_database file path")
    parser.add_argument("-o", "--output", dest="output", type=str, default="output",
                        help="extracted video output file directory")
    parser.add_argument("-m", "--merge", dest="merge", type=bool, default=False,
                        help="merge all frames extracted from database")
    parser.add_argument("-a", "--add-timeline", dest="add_timeline", type=bool, default=False,
                        help="Add recording history at timeline with filename")

    args = parser.parse_args()
    main(args)
