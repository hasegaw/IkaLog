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

# Needed in GUI mode
try:
    import wx
except:
    pass

try:
    import tornado.ioloop
    import tornado.web
    import tornado.websocket
    import tornado.template
    _tornado_imported = True
except:
    _tornado_imported = False

from ikalog.utils import *

_ = Localization.gettext_translation('websocket_server', fallback=True).gettext

# IkaLog Output Plugin: WebSocket server.

websockets = []


class IndexHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        # For testing....
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        print('%s: origin %s' % (self, origin))
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

    # In-game basic events

    def on_game_killed(self, context, params):
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
        self._send_message({
            'event': 'on_game_start',
            'stage': (context['game']['map'] or 'unknown'),
            'rule': (context['game']['rule'] or 'unknown'),
        })

    def on_game_team_color(self, context):
        self._send_message({
            'event': 'on_game_team_color',
            'my_team_color_hsv': context['game']['team_color_hsv'][0].tolist()[0],
            'counter_team_color_hsv': context['game']['team_color_hsv'][1].tolist()[0],
        })

    def on_game_finish(self, context):
        self._send_message({
            'event': 'on_game_finish',
        })

    # Common events to ranked battles.

    def on_game_ranked_we_lead(self, context):
        self._send_message({'event': 'on_game_ranked_we_lead'})

    def on_game_ranked_they_lead(self, context):
        self._send_message({'event': 'on_game_ranked_they_lead'})

    # Ranked, Splatzone battles

    def on_game_splatzone_we_got(self, context):
        self._send_message({'event': 'on_game_splatzone_we_got'})

    def on_game_splatzone_we_lost(self, context):
        self._send_message({'event': 'on_game_splatzone_we_lost'})

    def on_game_splatzone_they_got(self, context):
        self._send_message({'event': 'on_game_splatzone_they_got'})

    def on_game_splatzone_they_lost(self, context):
        self._send_message({'event': 'on_game_splatzone_they_lost'})

    # Ranked, Rainmaker battles

    def on_game_rainmaker_we_got(self, context):
        self._send_message({'event': 'on_game_rainmaker_we_got'})

    def on_game_rainmaker_we_lost(self, context):
        self._send_message({'event': 'on_game_rainmaker_we_lost'})

    def on_game_rainmaker_they_got(self, context):
        self._send_message({'event': 'on_game_rainmaker_they_got'})

    def on_game_rainmaker_they_lost(self, context):
        self._send_message({'event': 'on_game_rainmaker_they_lost'})

    # Ranked, Tower control battles

    def on_game_tower_we_got(self, context):
        self._send_message({'event': 'on_game_tower_we_got'})

    def on_game_tower_we_lost(self, context):
        self._send_message({'event': 'on_game_tower_we_lost'})

    def on_game_tower_they_got(self, context):
        self._send_message({'event': 'on_game_tower_they_got'})

    def on_game_tower_they_lost(self, context):
        self._send_message({'event': 'on_game_tower_they_lost'})

    # Counter / ObjectTracking.

    def on_game_paint_score_update(self, context):
        self._send_message({
            'event': 'on_game_paint_score_update',
            'paint_score': context['game'].get('paint_score', 0)
        })

    # Result scenes.

    def on_result_judge(self, context):
        self._send_message({
            'event': 'on_result_judge',
            'judge': context['game'].get('judge', None),
            'knockout': context['game'].get('knockout', None),
        })

    def on_result_udemae(self, context):
        # FIXME: データ追加
        self._send_message({
            'event': 'on_result_udemae',
        })

    def on_result_gears(self, context):
        # FIXME: データ追加
        self._send_message({
            'event': 'on_result_gears',
        })

    def on_result_festa(self, context):
        # FIXME: フェスの自分のタイトルが知りたい
        game = context['game']
        self._send_message({
            'event': 'on_result_festa',
            'festa_exp_pre': game.get('reslut_festa_exp_pre', None),
            'festa_exp': game.get('reslut_festa_exp', None),
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

    # Lobby events

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

    # Inkpolis events

    def on_inkopolis_lottery_done(self, context):
        self._send_message({
            'event': 'on_inkopolis_lottery',
            'gear_brand': context['game']['downie']['brand'],
            'gear_level': context['game']['downie']['level'],
            'sub_abilities': context['game']['downie']['sub_abilities'],
        })

    # Session close

    def on_game_session_end(self, context):
        self._send_message({
            'event': 'on_game_session_end',
        })

    # stat.ink
    def on_output_statink_submission_done(self, context, params):
        self._send_message({
            'event': 'on_output_statink_submission_done',
            'response': params,
        })

    def on_output_statink_submission_dryrun(self, context, params):
        self._send_message({
            'event': 'on_output_statink_submission_dryrun',
            'response': params,
        })

    def on_output_statink_submission_error(self, context, params):
        self._send_message({
            'event': 'on_output_statink_submission_error',
            'response': params,
        })

    def worker_func(self, websocket_server):
        print(websocket_server)
        self.application = tornado.web.Application([
            (r'/', IndexHandler),
            (r'/ws', WebSocketHandler),
        ])

        # FIXME: bind_addr
        self.application.listen(websocket_server._port)

        IkaUtils.dprint('%s: Listen port %d' % (self, websocket_server._port))
        IkaUtils.dprint('%s: Started server thread' % self)
        tornado.ioloop.IOLoop.instance().start()
        IkaUtils.dprint('%s: Stopped server thread' % self)

    def shutdown_server(self):
        tornado.ioloop.IOLoop.instance().stop()

    def initialize_server(self):
        if self.worker_thread is not None:
            if self.worker_thread.is_alive():
                IkaUtils.dprint(
                    '%s: Waiting for shutdown of server thread' % self)
                self.shutdown_server()

            # XXX
            while self.worker_thread.is_alive():
                time.sleep(2)

            IkaUtils.dprint('%s: server is shut down.' % self)

        if not self._enabled:
            return

        self.worker_thread = threading.Thread(
            target=self.worker_func, args=(self,))
        self.worker_thread.daemon = True
        self.worker_thread.start()

   # IkaUI Handlers

    def apply_ui(self):
        self._enabled = self.check_enable.GetValue()
        self._port = int(self.edit_port.GetValue())
        self.initialize_server()

    def refresh_ui(self):
        self.check_enable.SetValue(self._enabled)

        if not self._port is None:
            self.edit_port.SetValue(str(self._port))
        else:
            self.edit_port.SetValue('9090')

        self._internal_update = False

    def on_config_reset(self, context=None):
        self._enabled = False
        self._host = '127.0.0.1'
        self._port = '9090'

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)

        try:
            conf = context['config']['websocket_server']
        except:
            conf = {}

        if 'Enable' in conf:
            self._enabled = conf['Enable']

        if 'port' in conf:
            try:
                self._port = int(conf['port'])
            except ValueError:
                IkaUtils.dprint('%s: port must be an integer' % self)
                self._port = 9090

        self.refresh_ui()
        self.initialize_server()
        return True

    def on_config_save_to_context(self, context):
        context['config']['websocket_server'] = {
            'Enable': self._enabled,
            'port': self._port,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.panel_name = _('WebSocket Server')
        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.check_enable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Enable WebSocket Server'))
        self.edit_port = wx.TextCtrl(self.panel, wx.ID_ANY, 'port')

        layout = wx.GridSizer(2)
        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, _('Listen port')))
        layout.Add(self.edit_port)

        self.layout.Add(self.check_enable)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY,
            _('WARNING: The server is accessible by anyone.'),
        ))
        self.layout.Add(layout, flag=wx.EXPAND)

        self.panel.SetSizer(self.layout)

    def __init__(self, enabled=False, bind_addr='127.0.0.1', port=9090):
        if not _tornado_imported:
            print("モジュール tornado がロードできませんでした。 WebSocket サーバが起動できません。")
            print("インストールするには以下のコマンドを利用してください。\n    pip install tornado\n")
            return
        self._enabled = enabled
        self._port = 9090
        self.worker_thread = None
        self.initialize_server()


if __name__ == "__main__":
    obj = WebSocketServer(object)
