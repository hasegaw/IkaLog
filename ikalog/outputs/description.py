#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#  Copyright (C) 2016 Hiroyuki KOMATSU
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
# IkaLog Output Plugin: Output the video description to the specified file.
#
# Usage:
#   python3 ./IkaLog.py -f video.avi --desc description.txt

from datetime import datetime
import time

from ikalog.utils import *

def normalize_name(name):
  normalization_dict = {
    "ガロン52": ".52ガロン",
    "ガロン96": ".96ガロン",
    "ガロンデコ52": ".52ガロンデコ",
    "ガロンデコ96": ".96ガロンデコ",
  }
  return normalization_dict.get(name, name)


class Description(object):
    def __init__(self, output_filepath, verbose=True):
        self._description = ""
        self._last_death_time = ""
        self._first_act = True
        self._session_active = True
        self._output_filepath = output_filepath
        self._verbose = verbose

    def _print(self, message):
        if self._verbose:
            print(message)

    def get_timestamp(self, context):
        time_sec = context['engine']['msec'] / 1000
        video_time_str = "%d:%02d" % (time_sec / 60, time_sec % 60)
        return video_time_str

    def append_description(self, message, time=None, type=None):
        if time:
            self._description += (time + " ")
        if type == "we_got":
            self._description += "　　□ "
        elif type == "they_got":
            self._description += "　　■ "
        elif type == "we_lost" or type == "they_lost":
            self._description += "　　└ "
        self._description += (message + "\n")
        self._print(self._description)

    def on_game_start(self, context):
        time = self.get_timestamp(context)
        self.append_description("ステージ入場", time)

    def on_game_go_sign(self, context):
        time = self.get_timestamp(context)
        self.append_description("ゲーム開始", time)

    def on_game_finish(self, context):
        time = self.get_timestamp(context)
        self.append_description("ゲーム終了", time)

    def on_game_killed(self, context):
        time = self.get_timestamp(context)
        self.append_description("く8彡 プレイヤーをたおした！", time)

    def on_game_dead(self, context):
        if self._last_death_time:
          self.append_description("くX彡 やられた！", self._last_death_time)
        else:
          self._print("くX彡 やられた！")

        self._last_death_time = self.get_timestamp(context)

    def on_game_death_reason_identified(self, context):
        reason = IkaUtils.death_reason2text(
            context['game']['last_death_reason'])
        self.append_description("くX彡 %s でやられた！" % normalize_name(reason),
                                self._last_death_time)
        self._last_death_time = ""

    def on_game_ranked_we_lead(self, context):
        time = self.get_timestamp(context)
        self.append_description("　　〚カウントリードした！〛", time)

    def on_game_ranked_they_lead(self, context):
        time = self.get_timestamp(context)
        self.append_description("　　〚カウントリードされた！〛", time)

    def on_game_splatzone_we_got(self, context):
        time = self.get_timestamp(context)
        self.append_description("ガチエリア確保した！", time, type="we_got")

    def on_game_splatzone_we_lost(self, context):
        time = self.get_timestamp(context)
        self.append_description("カウントストップされた！", time, type="we_lost")

    def on_game_splatzone_they_got(self, context):
        time = self.get_timestamp(context)
        self.append_description("ガチエリア確保された！", time, type="they_got")

    def on_game_splatzone_they_lost(self, context):
        time = self.get_timestamp(context)
        self.append_description("カウントストップした！", time, type="they_lost")

    def on_game_rainmaker_we_got(self, context):
        time = self.get_timestamp(context)
        self.append_description("ガチホコをうばった！", time, type="we_got")

    def on_game_rainmaker_we_lost(self, context):
        time = self.get_timestamp(context)
        self.append_description("ガチホコを失った！", time, type="we_lost")

    def on_game_rainmaker_they_got(self, context):
        time = self.get_timestamp(context)
        self.append_description("ガチホコをうばわれた！", time, type="they_got")

    def on_game_rainmaker_they_lost(self, context):
        time = self.get_timestamp(context)
        self.append_description("ガチホコを防いだ！", time, type="they_lost")

    def run_once(self, context, message, type=None):
        if not self._first_act:
            return
        time = self.get_timestamp(context)
        self.append_description(message, time, type)
        self._first_act = False

    def on_game_towercontrol_we_took(self, context):
        self.run_once(context, "ガチヤグラをうばった！", type="we_got")

    def on_game_towercontrol_we_lost(self, context):
        self.run_once(context, "ガチヤグラをもどされた！", type="we_lost")

    def on_game_towercontrol_they_took(self, context):
        self.run_once(context, "ガチヤグラをうばわれた！", type="they_got")

    def on_game_towercontrol_they_lost(self, context):
        self.run_once(context, "ガチヤグラをもどした！", type="they_lost")

    def get_my_summary(self, context):
        '''Returns weapon, kills, deaths, score.'''
        if not context['game'].get('players', None):
            return '', '', '', ''

        me = IkaUtils.getMyEntryFromContext(context)
        weapon = normalize_name(
            IkaUtils.death_reason2text(me.get('weapon', '')))
        kills = str(me.get('kills', ''))
        deaths = str(me.get('deaths', ''))
        score = me.get('score', '')
        return weapon, kills, deaths, score

    def get_game_summary(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        result = IkaUtils.getWinLoseText(context['game']['won'],
                                         win_text="Win",
                                         lose_text="Lose",
                                         unknown_text="")

        summary_list = [rule, map]

        weapon, kills, deaths, score = self.get_my_summary(context)

        if weapon:
            summary_list.append(weapon)

        summary_list.append(result)

        if kills and deaths:
            summary_list.append('%sk%sd' % (kills, deaths))

        if score:
            summary_list.append('%sp' % score)

        udemae_before = ''
        udemae_after = ''
        if 'result_udemae' in context['scenes']:
            udemae = context['scenes']['result_udemae']
            udemae_before = '%s%d' % (udemae['udemae_str'].upper(),
                                      udemae['udemae_exp'])
            udemae_after = '%s%d' % (udemae['udemae_str_after'].upper(),
                                     udemae['udemae_exp_after'])
            summary_list.append('%s→%s' % (udemae_before, udemae_after))

        tsv_data = ['IKA', rule, map, result, kills, deaths,
                    udemae_before, udemae_after, weapon]

        return '\t'.join(tsv_data) + '\n' + ' '.join(summary_list)


    def get_players(self, context):
        players_list = []
        index = 1
        for player in context['game']['players']:
            if index == 1:
                if player['team'] == 1:
                    players_list.append('勝ちチーム')
                else:
                    players_list.append('負けチーム')

            result_list = []
            # name
            if player['me']:
                result_list.append('[%d]' % index)
            else:
                result_list.append(' %d ' % index)

            # rank (udemae) for ranked battle (gachi match).
            if 'udemae_pre' in player:
                result_list.append('%-2s' % player['udemae_pre'])

            # kd
            result_list.append('%2dk%2dd' % (player['kills'], player['deaths']))

            # weapon
            result_list.append(normalize_name(
                IkaUtils.death_reason2text(player['weapon'])))

            players_list.append(' '.join(result_list))

            if index == 4:
                index = 1
            else:
                index += 1

        return '\n'.join(players_list)

    def on_game_individual_result(self, context):
        time = self.get_timestamp(context)
        self.append_description('結果発表', time)
        players = '\n' + self.get_players(context)
        self.append_description(players)

    def on_result_udemae(self, context):
        self._print("on_result_udemae")

    def on_result_gears(self, context):
        gear_list = ['使用ギア']
        for gear in context['scenes']['result_gears']['gears']:
          gear_list.append('□ ' + IkaUtils.gear_ability2text(gear['main']))
          if gear.get('sub1'):
            if 'sub2' in gear:
              gear_list.append('├ ' + IkaUtils.gear_ability2text(gear['sub1']))
            else:
              gear_list.append('└ ' + IkaUtils.gear_ability2text(gear['sub1']))
          if gear.get('sub2'):
            if 'sub3' in gear:
              gear_list.append('├ ' + IkaUtils.gear_ability2text(gear['sub2']))
            else:
              gear_list.append('└ ' + IkaUtils.gear_ability2text(gear['sub2']))
          if gear.get('sub3'):
            gear_list.append('└ ' + IkaUtils.gear_ability2text(gear['sub3']))
        self.append_description('\n' + '\n'.join(gear_list))

    def on_game_session_end(self, context):
        summary = self.get_game_summary(context)
        self._print(summary)
        self._print(self._description)
        with open(self._output_filepath, 'w') as datafile:
          datafile.write(summary + '\n\n')
          datafile.write(self._description)
        self._session_active = False

    def on_game_session_abort(self, context):
        if self._session_active:
          self.on_game_session_end(context)
