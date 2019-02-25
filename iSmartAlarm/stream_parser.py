"""
    server_stream 내 모션센서 및 컨택트 센서 로그 및 시간 파싱
    is_detected가 0이고, 문을 열고 있는 이벤트라면 사이렌 알람도 발생한다.
    SIRENOP::door is open, all the siren need doorbell!!!
"""
import sys

import re
import json
import datetime

class Analyzer:
    def __init__(self, file_path):
        with open(file_path, 'rb') as f:
            s = f.read()
        s = s[0xe0000:]
        self.contents = str(s)
    def __timestamp_to_datetime(self, ts):
        utc_plus_2hr = datetime.timedelta(hours=2)
        resp_dt = datetime.datetime.utcfromtimestamp(int(ts))
        resp_dt += utc_plus_2hr
        return resp_dt

    def __split_log(self, logs):
        log_message = None
        for i, log in enumerate(logs):
            if i % 2 == 0:
                log_message = log
            else:
                log = json.loads(log)
                ts = log['TS'][:10]
                detected = int(log['DetectAlarm'])
                yield self.__timestamp_to_datetime(ts), log_message, detected

    def get_logs(self, tag):
        logs = re.findall(r'\$\@[A-Za-z0-9]+::'+tag+'::(.+)', self.contents)
        print(logs[0])
        for dt, log, is_detected in self.__split_log(logs):
            print(dt, ':', log, ' - is detected:', is_detected)

tags = ['ALARMPIR',  #Motion Sensor
        'ALARMDOOR', #Contact Sensor
       ]
analyzer = Analyzer(sys.argv[1])
for tag in tags:
    analyzer.get_logs(tag)

