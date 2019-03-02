#!/usr/bin/env python
# -*- coding: utf8 -*-
# DFRWS2018 ISmartAlarm diagnotics stream parser
from argparse import ArgumentParser
from collections import namedtuple

from utils.elastic import Elastic
from utils.logging.log import Log
from utils.time import to_datetime

import re
import os
import json
import struct

"""
!!!THIS IS DEPRECATED FORMAT!!!
!!!THIS IS DEPRECATED FORMAT!!!
!!!THIS IS DEPRECATED FORMAT!!!
# Log stream header
- 0x0  ~ 0x0F (16byte): ??? (auth key: ref. network_collect.py)
- 0x10 ~ 0x1F (16byte): ??? (auth key: ref. network_collect.py)
- 0x20 ~ 0x2F (16byte): ??? (log signature: ref. brainfficial)
- 0x30 ~ 0x3B (12byte): ??? (???)

# Sliced log signature table
## table range: 0x3C ~ EOF
## unit : 6byte
- 0x0 ~ 0x4 (4byte): log signature
- 0x5 ~ 0x6 (2byte): ???

# slaced log
- 0x0 ~ 0x1 (2byte): log signature 2 ("$@")
- 0x2 ~ 0x5 (4byte): log data size
- 0x6 ~ 0x9 (4byte): log signature
- 0xA ~ EOF: log data
!!!THIS IS DEPRECATED FORMAT!!!
!!!THIS IS DEPRECATED FORMAT!!!
!!!THIS IS DEPRECATED FORMAT!!!
"""

class ISADiagnoticsStreamParser:
    def __init__(self, diagnotics_stream):
        try:
            with open(diagnotics_stream, 'rb') as f:
                self.stream = f.read()
        except:
            #alert error. need to logging.
            sys.exit(-1)

    def get_unstructured_log(self):
        self.unstructured_stream_parser(self.stream[0x60000:0xE0000])
        return self.unstructured_log

    def get_sensor_log(self):
        self.sensor_log_stream_parser(self.stream[0xE0000:])
        return self.sensor_log

    def sensor_log_stream_parser(self, stream):
        self.sensor_log = []
        stream = stream.replace(b'\x00', b'')
        stream = stream.split(b'$@')
        for s in stream:
            if not s:
                continue
            _, sign, desc = s.split(b"::")
            if sign == b'ALARMDOOR' or sign == b'ALARMPIR':
                try:
                    data = json.loads(desc)
                    log = self.__sensor_log_repackager(data, sign)
                    self.sensor_log.append(log)
                except:
                    pass

    def unstructured_stream_parser(self, stream):
        self.index = 0
        self.unstructured_log = []
        while True:
            self.log = dict()
            sign = stream.find(b'\x24\x40')
            if sign != -1:
                size = struct.unpack("<L", stream[sign+0x2:sign+0x6])[0]
                parsed_data = stream[sign+0xA:sign+0xA+size]
                parsed_data = parsed_data.split(b'::')
                stream = stream[sign+0xA+size:]
            else:
                break
            self.log.update({
                'idx': self.index,
                'tag1': parsed_data[1][:2],
                'tag2': parsed_data[1][2:],
                'size': len(parsed_data[2])
            })
            if len(parsed_data[2]) < 16:
                self.__general_parse(parsed_data[2])
            else:
                self.__isa_parse(parsed_data[2])
            self.__classifier()
            self.unstructured_log.append(self.log)
            self.index += 1

    def __sensor_log_repackager(self, log_data, sign):
        """
            000A8540: Contact Sensor
            0006B4E5: PIR Sensor
        """
        sensors = {
            '000A8540': 'Contact',
            '0006B4E5': 'PIR',
        }
        dt_ = to_datetime(log_data['TS'])
        package = {
            'datetime': dt_,
            'sign': sign,
            'sensor': sensors[log_data['SensorID']],
            'sensor_id': log_data['SensorID'],
            'event': False,
            'siren': False,
            'is_detected': False,
        }
        if log_data['MessageType'] == '0':
            package.update({'event':True})
        if log_data['MessageType'] == '0' and log_data['ModeId'] == '2':
            package.update({'siren':True})
        if log_data['DetectAlarm'] == '1':
            package.update({'is_detected':True})
        return package

    def __unpack_to_update(self, data, labels, unpack_tags):
        pseudo_tag = namedtuple('pseudo_tag', labels)
        structured = pseudo_tag(*struct.unpack(unpack_tags, data))._asdict()
        self.log.update(structured)

    def __isa_parse(self, data):
        data_size = self.log['size'] - 16
        self.__unpack_to_update(data, 'sign type1 type2 type3 data', '<4sLLL'+str(data_size)+'s')
        if self.log['sign'].startswith(b'ISA'):
            self.log.update({'desc': 'isa'})
        else:
            self.log.update({'desc': 'general'})

    def __general_parse(self, data):
        #8byte만 지원함
        #가끔 BC, TCP 태그 가진 애들 중에 9바이트인 애들 있음.
        if len(data) % 4 != 0:
            self.log['desc'] = 'dummy'
            return
        self.__unpack_to_update(data, 'type1 type2', '<LL')
        self.log['desc'] = 'general'

    def __classifier(self):
        if self.log['desc'] == 'isa':
            types = [self.log[x] for x in ['type1', 'type2', 'type3']]
            if types == [21, 1, 10]:
                self.log.update({
                    'data_type': 'datetime',
                    'data': to_datetime(self.log['data'])
                })            
            else:
                self.log.update({'data_type':'raw'})


def main(args):
    if not os.path.exists(args.server_stream):
        Log.error("server_stream file not exist.")
        return

    Log.info("Start parsing iSmartAlarm diagnotics stream...")

    isap = ISADiagnoticsStreamParser(args.server_stream)
    unstructured_log = isap.get_unstructured_log()
    sensor_log = isap.get_sensor_log()

    with Elastic(index='unstructured_log', doc_type='unstructured_log') as elastic:
        datetime_log = []

        for log in unstructured_log:
            if 'data_type' in log.keys():
                if log['data_type'] == 'datetime':
                    datetime_log.append(log)
        elastic.upload(datetime_log, 'datetime')

    with Elastic(index='sensor_log', doc_type='sensor_log') as elastic:
        elastic.upload(sensor_log, 'datetime')

    Log.i("Successfully upload server_stream data.")

    del isap


if __name__ == '__main__':
    parser = ArgumentParser(description="iSmartAlarm diagnotics server stream parser")
    parser.add_argument('-s', '--server-stream', type=str,
        help='iSmartAlarm server_stream file path')

    args = parser.parse_args()
    main(args)
