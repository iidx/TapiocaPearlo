#!/usr/bin/env python
# -*- coding: utf8 -*-
# DFRWS2018 ISmartAlarm diagnotics stream parser
import re
import sys
import json
import struct
from collections import namedtuple

import utils.time
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
        self.index = 0
        self.dataset = []
        try:
            with open(diagnotics_stream, 'rb') as f:
                stream = f.read()
        except:
            #alert error. need to logging.
            sys.exit(-1)

        #exclude signatures table
        #self.unstructured_stream_parser(stream[0x60000:0xE0000])
        self.readable_stream_parser(stream[0xE0000:])

    def readable_stream_parser(self, stream):
        stream = str(stream).replace('\r\n', '\x0d\x0a')
        print(stream)


    def unstructured_stream_parser(self, stream):
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
            self.dataset.append(self.log)
            self.index += 1

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
                    'data': utils.time.to_datetime(self.log['data'])
                })            
            else:
                self.log.update({'data_type':'raw'})

isa_parser = ISADiagnoticsStreamParser(sys.argv[1])
#print(isa_parser.dataset)