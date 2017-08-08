#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2016 Takeshi HASEGAWA
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

import time
import datetime
import json
import traceback
import uuid

import cv2

from ikalog.constants import fes_rank_titles, stages, rules, weapons, special_weapons
import ikalog.version
from ikalog.utils import *
from ikalog.utils.anonymizer import anonymize


def dprint(s):
    print("%s: %s" % (__name__, s))


def _encode_image(img):
    try:
        result, img_png = cv2.imencode('.png', img)
    except:
        reult = False

    if not result:
        dprint('Failed to encode the image (%s)' % (img.shape))
        return None

    s = img_png.tostring()

    dprint('Encoded screenshot (%dx%d %d bytes)' %
           (img.shape[1], img.shape[0], len(s)))

    return s


def _remove_none_keyvalues(d):
    for key in list(filter(lambda x: d[x] is None, d.keys())):
        del d[key]


def _set_values(fields, dest, src):
    for field in fields:
        f_type, f_statink, f_ikalog = field[0:3]

        valid = (f_ikalog in src) and (src[f_ikalog] is not None)
        if not valid:
            continue

        func = {
            'int': lambda x: int(x[f_ikalog]),
            'str': lambda x: str(x[f_ikalog]),
            'str_lower': lambda x: str(x[f_ikalog]).lower(),
        }
        dest[f_statink] = func[f_type](src)


def _validate_time(t):
    if t is None:
        return True
    return time.mktime(datetime.date(2014, 1, 1).timetuple()) <= t


class StatInkCompositor(object):

    @staticmethod
    def dprint(s):
        IkaUtils.dprint(s)

    def composite_lobby(self, context, payload):
        lobby = context.get('lobby', {})
        lobby_type = lobby.get('type')

        if context['game'].get('is_fes'):
            lobby_type = 'festa'

        func = {
            'public': lambda x: 'standard',
            'private': lambda x: 'private',
            'festa': lambda x: 'fest',
            'tag': lambda x: 'squad_%d' % x.get('team_members', 0),

            'testfire': lambda x: 'standard',
        }

        payload['lobby'] = None
        if lobby_type in func.keys():
            payload['lobby'] = func[lobby_type](lobby)

        valid_lobby_types = ['standard', 'private',
                             'fest', 'squad_2', 'squad_3', 'squad_4']
        if not (payload['lobby'] in valid_lobby_types):
            if payload['lobby']:
                dprint('invalid lobby %s' % payload['lobby'])
            del payload['lobby']
            return False
        return True

    def composite_stage_and_mode(self, context, payload):
        game = context.get('game', {})

        stage = game.get('map')
        if stage in stages.keys():
            payload['map'] = stage

        rule = game.get('rule')
        if rule in rules.keys():
            payload['rule'] = rule

    def composite_kill_death(self, context, payload):
        game = context.get('game', {})

        cause_of_death = game.get('death_reasons', {})
        # ToDo: key check
        if len(cause_of_death.keys()) > 0:
            payload['death_reasons'] = cause_of_death.copy()

        if game.get('max_kill_combo') is not None:
            payload['max_kill_combo'] = int(game['max_kill_combo'])

        if game.get('max_kill_streak') is not None:
            payload['max_kill_streak'] = int(game['max_kill_streak'])

    def composite_team_colors(self, context, payload):
        game = context.get('game')
        if ('my_team_color' in game):
            payload['my_team_color'] = {
                'hue': game['my_team_color']['hsv'][0] * 2,
                'rgb': game['my_team_color']['rgb'],
            }

        if ('counter_team_color' in game):
            payload['his_team_color'] = {
                'hue': game['counter_team_color']['hsv'][0] * 2,
                'rgb': game['counter_team_color']['rgb'],
            }

    def composite_agent_information(self, context, payload):
        payload['agent'] = 'IkaLog'
        payload['agent_version'] = ikalog.version.IKALOG_VERSION
        payload['agent_game_version'] = ikalog.version.GAME_VERSION
        payload['agent_game_version_date'] = ikalog.version.GAME_VERSION_DATE

    def composite_agent_custom(self, context):
        custom = {}

        if 'exceptions_log' in context['engine']:
            if len(context['engine']['exceptions_log']) > 0:
                custom['exceptions'] = \
                    context['engine']['exceptions_log'].copy()

        if len(custom) == 0:
            return None

        return json.dumps(custom, separators=(',', ':'))

    def composite_agent_variables(self, context):
        variables = {}

        variables['input_class'] = \
            context['engine'].get('input_class', 'unknown')

        variables['primary_language'] = \
            Localization.get_game_languages()[0]

        # variables['exceptions']
        #
        # e.g. "InklingsTracker(10) GameStart(4) ..."
        if 'exceptions_log' in context['engine']:
            if len(context['engine']['exceptions_log']) > 0:

                exceptions = context['engine']['exceptions_log'].items()
                # FIXME: Sorting
                s = []
                for e in exceptions:
                    s.append('%s(%d)' % (e[0], e[1]['count']))
                variables['exceptions'] = ', '.join(s)

        return variables

    def _composite_result_judge_turf(self, context, payload):
        if not (payload.get('rule') in ['nawabari']):
            return

        scores = context['game'].get('nawabari_scores_pct')
        if scores is None:
            return

        payload['my_team_final_percent'] = scores[0]
        payload['his_team_final_percent'] = scores[1]

    def _composite_result_judge_ranked(self, context, payload):
        if payload.get('rule', None) in ['area', 'yagura', 'hoko']:
            scores = context['game'].get('ranked_scores', None)
            print('ranked scores = %s' % scores)
            if scores is not None:
                payload['my_team_count'] = scores[0]
                payload['his_team_count'] = scores[1]

        scores = context['game'].get('earned_scores', None)
        if 0:  # scores is not None:
            payload['my_team_final_point'] = scores[0]
            payload['his_team_final_point'] = scores[1]

    def composite_result_judge(self, context, payload):
        self._composite_result_judge_turf(context, payload)
        self._composite_result_judge_ranked(context, payload)

    def composite_result_scoreboard(self, context, payload):
        me = IkaUtils.getMyEntryFromContext(context)
        if me is None:
            return

        # Spl2: Use IkaLog-counted values for kill and death counts
        kills = context['game'].get('kills')
        if kills is not None:
            me['kills'] = kills
            payload['kill'] = kills

        death = context['game'].get('death')
        if death is not None:
            me['death'] = death
            payload['death'] = death

        payload['result'] = IkaUtils.getWinLoseText(
            context['game']['won'],
            win_text='win',
            lose_text='lose',
            unknown_text=None
        )

        # weapon = me.get('weapon')
        # if weapon:
        #     payload['weapon'] = weapon

        if context['game'].get('is_fes'):
            payload['gender'] = me['gender_en']
            payload['fest_title'] = str(me['prefix_en']).lower()

        _set_values(
            [  # 'type', 'stat.ink Field', 'IkaLog Field'
                ['int', 'rank_in_team', 'rank_in_team'],
                ['int', 'kill', 'kills'],
                ['int', 'death', 'deaths'],
                ['int', 'special', 'special'],
                ['int', 'level', 'rank'],
                ['int', 'my_point', 'score'],
            ], payload, me)

        players = []
        for e in context['game']['players']:
            player = {}
            player['team'] = 'my' if (e['team'] == me['team']) else 'his'
            player['is_me'] = 'yes' if e['me'] else 'no'
            _set_values(
                [  # 'type', 'stat.ink Field', 'IkaLog Field'
                    ['int', 'rank_in_team', 'rank_in_team'],
                    ['int', 'kill', 'kills'],
                    ['int', 'death', 'deaths'],
                    ['int', 'special', 'special'],
                    ['int', 'level', 'rank'],
                    ['int', 'point', 'score'],
                ], player, e)

            #weapon = e.get('weapon')
            # if weapon:
            #    player['weapon'] = weapon

            if payload.get('rule') != 'nawabari':
                if 'udemae_pre' in e:
                    player['rank'] = str(e['udemae_pre']).lower()

            players.append(player)

        payload['players'] = players

    def composite_result_gears(self, context, payload):
        if ('result_gears' in context['scenes']) and ('gears' in context['scenes']['result_gears']):
            try:
                gears_list = []
                for e in context['scenes']['result_gears']['gears']:
                    primary_ability = e.get('main', None)
                    secondary_abilities = [
                        e.get('sub1', None),
                        e.get('sub2', None),
                        e.get('sub3', None),
                    ]

                    gear = {'secondary_abilities': []}
                    if primary_ability is not None:
                        gear['primary_ability'] = primary_ability

                    # when:
                    #   "Run Speed Up" "Locked" "Empty"
                    # should be: (json-like)
                    #   [ "run_speed_up", null ]
                    #       - "Locked":  send `null`
                    #       - "Empty":   not send
                    #       - Otherwise: predefined id string ("key")
                    for ability in secondary_abilities:
                        if (ability is None) or (ability == 'empty'):
                            continue

                        if (ability == 'locked'):
                            gear['secondary_abilities'].append(None)
                        else:
                            gear['secondary_abilities'].append(ability)

                    gears_list.append(gear)

                payload['gears'] = {
                    'headgear': gears_list[0],
                    'clothing': gears_list[1],
                    'shoes': gears_list[2],
                }
            except:
                IkaUtils.dprint(
                    '%s: Failed in ResultGears payload. Fix me...' % self)
                IkaUtils.dprint(traceback.format_exc())

        result_gears = context.get('scenes', {}).get('result_gears', {})
        _set_values(
            [  # 'type', 'stat.ink Field', 'IkaLog Field'
                ['int', 'cash_after', 'cash'],
            ], payload, result_gears)

    def composite_result_udemae(self, context, payload):
        if payload.get('rule') == 'nawabari':
            return True

        _set_values([  # 'type', 'stat.ink Field', 'IkaLog Field'
            ['str_lower', 'rank', 'result_udemae_str_pre'],
            ['int', 'rank_exp', 'result_udemae_exp_pre'],
            ['str_lower', 'rank_after', 'result_udemae_str'],
            ['int', 'rank_exp_after', 'result_udemae_exp'],
        ], payload, context['game'])

        knockout = context['game'].get('knockout', None)
        if knockout in [True, False]:
            payload['knock_out'] = {True: 'yes', False: 'no'}[knockout]

    def composite_result_splatfest(self, context, payload):

        if payload.get('lobby', None) == 'fest':
            _set_values(
                [  # 'type', 'stat.ink Field', 'IkaLog Field'
                    ['int', 'fest_exp', 'result_festa_exp_pre'],
                    ['int', 'fest_exp_after', 'result_festa_exp'],
                ], payload, context['game'])

            if payload.get('fest_title', None) is not None:
                current_title = payload['fest_title']
                if context['game'].get('result_festa_title_changed', False):
                    try:
                        index = fes_rank_titles.index(current_title)
                        current_title = fes_rank_titles[index + 1]
                    except IndexError:
                        IkaUtils.dprint(
                            '%s: IndexError at fes_rank_titles' % self)

                payload['fest_title_after'] = current_title.lower()

    def composite_screenshots(self, payload):
        if self._parent is None:
            return

        if self._parent.img_scoreboard is not None:
            img_scoreboard = anonymize(
                self._parent.img_scoreboard,
                anonOthers=self._parent.config['anon_others'],
                anonAll=self._parent.config['anon_all'],
            )
            payload['image_result'] = _encode_image(img_scoreboard)
        else:
            dprint('img_result_detail is empty.')

        if self._parent.img_judge is not None:
            payload['image_judge'] = _encode_image(self._parent.img_judge)
        else:
            dprint('img_judge is empty.')

        if self._parent.img_gears is not None:
            payload['image_gear'] = _encode_image(self._parent.img_gears)
        else:
            dprint('img_gear is empty.')

    def composite_payload(self, context):
        payload = {
            'uuid': uuid.uuid1().hex,
        }

        game = context['game']
        if ('start_time' in game) and _validate_time(game.get('start_time')):
            try:
                payload['start_at'] = int(context['game']['start_time'])
            except:
                pass

        if ('end_time' in game) and _validate_time(game.get('end_time')):
            try:
                payload['end_at'] = int(context['game']['end_time'])
            except:
                pass

        self.composite_lobby(context, payload)
        self.composite_stage_and_mode(context, payload)
        self.composite_kill_death(context, payload)
        self.composite_result_judge(context, payload)
        self.composite_result_scoreboard(context, payload)
        self.composite_result_gears(context, payload)
        self.composite_result_udemae(context, payload)
        self.composite_result_splatfest(context, payload)

        self.composite_team_colors(context, payload)
        self.composite_screenshots(payload)

        # Video URL
        if isinstance(self._parent.video_id, str) and (self._parent.video_id != ''):
            payload['link_url'] = \
                'https://www.youtube.com/watch?v=%s' % self._parent.video_id

        # In-game events (timeline)
        if len(self._parent.events) > 0:
            payload['events'] = list(self._parent.events)

        # Agent Information

        self.composite_agent_information(context, payload)
        payload['agent_variables'] = self.composite_agent_variables(context)
        payload['agent_custom'] = self.composite_agent_custom(context)

        _remove_none_keyvalues(payload)

        return payload

    def __init__(self, parent=None):
        self._parent = parent


if __name__ == '__main__':
    import pickle

    def _load(file):
        f = open(file, 'rb')
        d = pickle.load(f)
        f.close()
        return d

    context = {}
    context['game'] = _load('context.data')
    print('---start context---')
    print(context)
    context['lobby'] = {'type': 'private'}
    print('---end context---')
    payload = {}
    compo = StatInkCompositor(None)

    payload = compo.composite_payload(context)
    print(payload)
