#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

#
#  This module is still in proof of concept, and subject to change.
#

from IkaUtils import *
from datetime import datetime
import time

# IkaLog Output Plugin: Write 'Alive Squids' CSV data
#


class IkaOutput_CSV_AliveSquids:

    ##
    # Write a line to text file.
    # @param self     The Object Pointer.
    # @param record   Record (text)
    #
    def writeRecord(self, file, record):
        try:
            csv_file = open(file, "a")
            csv_file.write(record)
            csv_file.close
        except:
            print("CSV: Failed to write CSV File")

    def writeAliveSquidsCSV(self, context, basename="ikabattle_log", debug=False):
        csv = ["tick,y\n", "tick,y\n"]

        for sample in context['game']['livesTrack']:
            if debug:
                print('lives sample = %s', sample)
            time = sample[0]
            del sample[0]
            num_team = 0
            for team in sample:
                num_squid = 0
                for alive in team:
                    num_squid = num_squid + 1

                    if alive:
                        csv[num_team] = "%s%d, %d\n" % (
                            csv[num_team], time, num_squid)
                num_team = num_team + 1

        num_team = 0

        t = datetime.now()
        t_str = t.strftime("%Y%m%d_%H%M")

        for f in csv:
            self.writeRecord('%s/%s_team%d.csv' %
                             (self.dest_dir, basename, num_team), f)
            num_team = num_team + 1

    def writeFlagsCSV(self, context, basename="ikabattle_log", debug=False):
        # データがない場合は書かない
        if len(context['game']['towerTrack']) == 0:
            return

        csv = "tick,pos,max,min\n"

        for sample in context['game']['towerTrack']:
            if debug:
                print('tower sample = %s', sample)
            time = sample[0]
            sample = sample[1]
            csv = "%s%d, %d, %d, %d\n" % (
                csv, time, sample['pos'], sample['max'], sample['min'])

        self.writeRecord('%s/%s_tower.csv' % (self.dest_dir, basename), csv)

    ##
    # onGameIndividualResult Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def onGameIndividualResult(self, context):
        t = datetime.now()
        basename = t.strftime("ikabattle_log_%Y%m%d_%H%M")
        self.writeAliveSquidsCSV(context, basename=basename, debug=self.debug)
        self.writeFlagsCSV(context, basename=basename, debug=self.debug)

    ##
    # Constructor
    # @param self         The Object Pointer.
    # @param dest_dir     Destionation directory (Relative path, or absolute path)
    def __init__(self, dir='./log/', debug=False):
        self.dest_dir = dir
        self.debug = debug
