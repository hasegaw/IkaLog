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

import json
import os
import sys
import threading
import time

try:
    import tornado.ioloop
    import tornado.web
    import tornado.websocket
    import tornado.template
    _tornado_imported = True
except:
    _tornado_imported = False

from ikalog.utils import *

websockets = []

# IkaLog Output Plugin: WebSocket server.


class IndexHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        # For testing....
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        IkaUtils.dprint("%s: Connected" % self)
        websockets.append(self)

    def on_message(self, message):
        pass

    def on_close(self):
        IkaUtils.dprint("%s: Closed" % self)
        del websockets[websockets.index(self)]


class WebSocketServer(object):

    def _send_message(self, d):
        if len(websockets) == 0:
            return

        IkaUtils.dprint('%s: number of websockets = %d' %
                        (self, len(websockets)))
        d_json = json.dumps(d, separators=(',', ':'), ensure_ascii=False)

        for s in websockets:
            IkaUtils.dprint('  Sending a message to %s' % s)
            s.write_message(d_json)

    def on_game_killed(self, context):
        self._send_message({
            'event': 'on_game_killed'
        })

    def on_game_dead(self, context):
        self._send_message({
            'event': 'on_game_dead'
        })

    def on_game_death_reason_identified(self, context):
        self._send_message({
            'event': 'on_death_reason_identified',
            'reason': context['game'].get('last_death_reason', ''),
        })

    def on_game_go_sign(self, context):
        self._send_message({
            'event': 'on_game_go_sign'
        })

    def on_game_start(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        self._send_message({
            'event': 'on_game_start',
            'stage': IkaUtils.map2text(context['game']['map'], 'unknown'),
            'rule': IkaUtils.rule2text(context['game']['rule'], 'unknown'),
        })

    def on_game_team_color(self, context):
        self._send_message({
            'event': 'on_game_team_color',
            'my_team_color_hsv': context['game']['team_color_hsv'][0].tolist()[0],
            'counter_team_color_hsv': context['game']['team_color_hsv'][1].tolist()[0],
        })

    def on_game_paint_score_update(self, context):
        self._send_message({
            'event': 'on_game_paint_score_update',
            'paint_score': context['game'].get('paint_score', 0)
        })

    def on_lobby_matching(self, context):
        self._send_message({
            'event': 'on_lobby_matching',
            'lobby_state': context['lobby'].get('state', None),
            'lobby_type': context['lobby'].get('type', None),
        })

    def on_lobby_matched(self, context):
        self._send_message({
            'event': 'on_lobby_matched',
            'lobby_state': context['lobby'].get('state', None),
            'lobby_type': context['lobby'].get('type', None),
        })

    def on_game_finish(self, context):
        self._send_message({
            'event': 'on_game_finish',
        })

    def on_result_judge(self, context):
        self._send_message({
            'event': 'on_result_judge',
            'judge': context['game'].get('judge', None),
            'knockout': context['game'].get('knockout', None),
        })

    def on_game_individual_result(self, context):
        me = IkaUtils.getMyEntryFromContext(context)
        print(me)
        self._send_message({
            'event': 'on_result_detail',
            'won': context['game'].get('won', None),
            'rank': me.get('rank', None),
            'score': me.get('score', None),
            'udemae': me.get('udemae_pre', None),
            'kills': me.get('kills', None),
            'deaths': me.get('deaths', None),
            'weapon': me.get('weapon', None),

        })

    def on_result_udemae(self, context):
        d = context['scenes']['result_udemae']
        self._send_message({
            'event': 'on_result_udemae',
            'udemae_str': d.get('udemae_str_after', None),
            'udemae_exp': d.get('udemae_exp_after', None),
        })

    def on_result_gears(self, context):
        self._send_message({
            'event': 'on_result_gears',
        })

    def on_game_session_end(self, context):
        self._send_message({
            'event': 'on_game_session_end',
        })

    def on_option_tab_create(self, notebook):
        pass

    def worker(self):
        tornado.ioloop.IOLoop.instance().start()

    def __init__(self, bind_addr='127.0.0.1', port=9090):
        if not _tornado_imported:
            print("モジュール tornado がロードできませんでした。 WebSocet サーバが起動できません。")
            print("インストールするには以下のコマンドを利用してください。\n    pip install tornado\n")
            return

        # FIXME: bind_addr
        self.application = tornado.web.Application([
            (r'/', IndexHandler),
            (r'/ws', WebSocketHandler),
        ])

        self.application.listen(port)
        thread = threading.Thread(target=self.worker)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    obj = WebSocketServer(object)
