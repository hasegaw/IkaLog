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

from ikalog.plugin import IkaLogPlugin
from ikalog.utils import *

from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np

from ikalog.utils.ikamatcher2.matcher import MultiClassIkaMatcher2 as MultiClassIkaMatcher


class PlayerNamesPlugin(IkaLogPlugin):

    plugin_name = 'player_names'

    def __init__(self, dest_dir=None):
        super(PlayerNamesPlugin, self).__init__()
        self._scale = 8
        self.enabled = True
        try:
            self._font = ImageFont.truetype("Splatoon2.otf", 18 * self._scale)
        except OSError:
            IkaUtils.dprint("Could not read font size - player_names disabled")
            self.enabled = False

    def _add_player_name_mask(self, name, team=0):
        pil_im = Image.new("RGB", (150*self._scale, 25 *
                           self._scale), (255, 255, 255))
        draw = ImageDraw.Draw(pil_im)
        draw.text((4.5 * self._scale, -5.25*self._scale), name,
                  (0, 0, 0), font=self._font, features=["kern"])
        pil_im.thumbnail((150, 25))
        player_name_im = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

        mask = IkaMatcher(
            0, 0, 150, 25,
            img=player_name_im,
            threshold=0.9,
            orig_threshold=0.02,
            bg_method=matcher.MM_BLACK(visibility=(0, 215)),
            fg_method=matcher.MM_WHITE(visibility=(150, 255)),
            label=name,
            # call_plugins=self._call_plugins,
            debug=False
        )

        if team == 1:
            self._player_masks_team1.add_mask(mask)
        else:
            self._player_masks_team0.add_mask(mask)

    def _matches_name(self, img, team=0, label=''):
        if team == 1:
            (bg, fg, mask) = self._player_masks_team1.match_best_bg_fg(
                img, label=label)
        else:
            (bg, fg, mask) = self._player_masks_team0.match_best_bg_fg(
                img, label=label)
        if mask:
            return mask._label
        return None

    def on_result_scoreboard_players(self, context, params=None):
        if not self.enabled:
            return

        # self._call_plugins('get_player_names')

        self._player_masks_team0 = MultiClassIkaMatcher()
        self._player_masks_team1 = MultiClassIkaMatcher()

        player_names_list = context.get('game', {}).get('player_names', [])
        for index, name in enumerate(context['game']['player_names']):
            team = 1 if index < 4 else 0
            if context['game']['won']:
                team = 0 if index < 4 else 1
            if name:
                self._add_player_name_mask(name, team)

        for index, p in enumerate(context.get('game', {}).get('players', {})):
            p['name'] = \
                self._matches_name(p['img_name'], 0 if index < 4 else 1, index)

    def on_validate_configuration(self, config):
        pass

    def on_reset_configuration(self):
        pass

    def on_set_configuration(self, config):
        pass


if __name__ == '__main__':
    import pprint
    from ikalog.scenes.v2.result.scoreboard.simple import Spl2ResultScoreboard

    obj = PlayerNamesPlugin()
    obj2 = Spl2ResultScoreboard(None)

    frame = cv2.imread('screenshots/ikabattle_20220218_204007.png', 1)
    ctx = {
        'engine': {'frame': frame, 'msec': 0},
        'game': {
            'won': True,
            'player_names': ['______', 'らぴす', '______', '______', '______', '______', '______', '______'],
        }
    }
    obj2.match(ctx)
    obj.on_result_scoreboard_players(ctx)

    def _remove_arrays(d, _path=''):
        for key in d.keys():
            path = '.'.join([_path, key])
            if type(d[key]) is dict:
                _remove_arrays(d[key], path)
            if type(d[key]) is np.ndarray:
                d[key] = 'ndarray'
            if key.startswith('img_'):
                d[key] = 'image'

    _remove_arrays(ctx)
    for p in ctx['game']['players']:
        _remove_arrays(p)

    pprint.pprint(ctx)
