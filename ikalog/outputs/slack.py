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

from ikalog.utils import *

# Needed in GUI mode
try:
    import wx
except:
    pass

_ = Localization.gettext_translation('slack', fallback=True).gettext

# IkaOutput_Slack: IkaLog Output Plugin for Slack
#
# Post game results to Slack, using Incoming Hook


class Slack(object):

    def apply_ui(self):
        self.enabled = self.checkEnable.GetValue()
        self.url = self.editURL.GetValue()
        self.username = self.editBotName.GetValue()

    def refresh_ui(self):
        self._internal_update = True

        self.checkEnable.SetValue(self.enabled)

        if not self.url is None:
            self.editURL.SetValue(self.url)
        else:
            self.editURL.SetValue('')

        if not self.username is None:
            self.editBotName.SetValue(self.username)
        else:
            self.editBotName.SetValue('')

        self._internal_update = False

    def on_config_reset(self, context=None):
        self.enabled = False
        self.url = ''
        self.username = 'IkaLog'

    def on_config_load_from_context(self, context):
        self.on_config_reset(context)

        try:
            conf = context['config']['slack']
        except:
            conf = {}

        if 'Enable' in conf:
            self.enabled = conf['Enable']

        if 'url' in conf:
            self.url = conf['url']

        if 'botName' in conf:
            self.username = conf['botName']

        self.refresh_ui()
        return True

    def on_config_save_to_context(self, context):
        context['config']['slack'] = {
            'Enable': self.enabled,
            'url': self.url,
            'botName': self.username,
        }

    def on_config_apply(self, context):
        self.apply_ui()

    def on_option_tab_create(self, notebook):
        self.panel = wx.Panel(notebook, wx.ID_ANY)
        self.panel_name = _('Slack')
        self.layout = wx.BoxSizer(wx.VERTICAL)

        self.checkEnable = wx.CheckBox(
            self.panel, wx.ID_ANY, _('Post game results to a Slack channel'))
        self.editURL = wx.TextCtrl(self.panel, wx.ID_ANY, u'http:')
        self.editBotName = wx.TextCtrl(self.panel, wx.ID_ANY, _('IkaLog bot'))

        layout = wx.BoxSizer(wx.HORIZONTAL)
        layout.Add(wx.StaticText(self.panel, wx.ID_ANY, _('Bot Name')))
        layout.Add(self.editBotName, flag=wx.EXPAND)
        self.layout.Add(self.checkEnable)
        self.layout.Add(wx.StaticText(
            self.panel, wx.ID_ANY, _('Incoming WebHook API URL')))
        self.layout.Add(self.editURL, flag=wx.EXPAND)
        self.layout.Add(layout, flag=wx.EXPAND)

        self.panel.SetSizer(self.layout)

    ##
    # Post a bot message to slack.
    # @param self     The Object Pointer.
    # @param text     Text message.
    # @param username Username.
    #
    def post(self, text='', username='IkaLog bot'):
        try:
            import slackweb
            slack = slackweb.Slack(url=self.url)
            slack.notify(text=text, username=self.username)
        except:
            print("Slack: Failed to post a message to Slack")

    ##
    # Generate a record for on_game_individual_result.
    # @param self      The Object Pointer.
    # @param context   IkaLog context
    #
    def get_text_game_individual_result(self, context):
        map = IkaUtils.map2text(context['game']['map'])
        rule = IkaUtils.rule2text(context['game']['rule'])
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text="勝ち", lose_text="負け", unknown_text="不明")
        return "%sで%sに%sました" % (map, rule, won)

    ##
    # on_game_session_end Hook
    # @param self      The Object Pointer
    # @param context   IkaLog context
    #
    def on_game_session_end(self, context):
        if not self.enabled:
            return False

        s = self.get_text_game_individual_result(context)

        fes_info = IkaUtils.playerTitle(
            IkaUtils.getMyEntryFromContext(context))
        if not fes_info is None:
            s = s + _(' (Fest title %s)') % (fes_info)

        self.post(text=s, username=self.username)

    ##
    # Check availability of modules this plugin depends on.
    # @param self      The Object Pointer.
    #
    def check_import(self):
        try:
            import slackweb
        except:
            print("モジュール slackweb がロードできませんでした。 Slack 投稿ができません。")
            print("インストールするには以下のコマンドを利用してください。\n    pip install slackweb\n")

    ##
    # Constructor
    # @param self     The Object Pointer.
    # @param url      Slack Incoming Hook Endpoint
    # @param username Name the bot use on Slack
    def __init__(self, url=None, username="＜8ヨ"):
        self._internal_update = False
        self.url = url
        self.username = username
        self.enabled = (not url is None)
        self.check_import()

if __name__ == "__main__":
    import sys
    obj = Slack(
        url=sys.argv[1],
    )
    s = obj.get_text_game_individual_result({
        "game": {
            "map": {"name": "map_name"},
            "rule": {"name": "rule_name"},
            "won": True, }})
    print(s)
    obj.post(s)
