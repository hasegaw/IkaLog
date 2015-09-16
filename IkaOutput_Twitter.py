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

## @package IkaOutput_Twitter

from IkaUtils import *

from datetime import datetime
import json
import cv2

# Needed in GUI mode
try:
	import wx
except:
	pass

## IkaOutput_Twitter: IkaLog Output Plugin for Twitter
# 
# Tweet Splatton game events.
class IkaOutput_Twitter:
	## API Endpoint for Tweets
	url = "https://api.twitter.com/1.1/statuses/update.json"
	## API Endpoint for Medias (screenshots)
	url_media = "https://upload.twitter.com/1.1/media/upload.json"

	last_me = None

	def ApplyUI(self):
		self.enabled =           self.checkEnable.GetValue()
		self.AttachImage =       self.checkAttachImage.GetValue()
		self.ConsumerKey =       self.editConsumerKey.GetValue()
		self.ConsumerSecret =    self.editConsumerSecret.GetValue()
		self.AccessToken =       self.editAccessToken.GetValue()
		self.AccessTokenSecret = self.editAccessTokenSecret.GetValue()
		self.Footer =            self.editFooter.GetValue()

	def RefreshUI(self):
		self._internal_update = True
		self.checkEnable.SetValue(self.enabled)
		self.checkAttachImage.SetValue(self.AttachImage)

		if not self.ConsumerKey is None:
			self.editConsumerKey.SetValue(self.ConsumerKey)
		else:
			self.editConsumerKey.SetValue('')

		if not self.ConsumerSecret is None:
			self.editConsumerSecret.SetValue(self.ConsumerSecret)
		else:
			self.editConsumerSecret.SetValue('')

		if not self.AccessToken is None:
			self.editAccessToken.SetValue(self.AccessToken)
		else:
			self.editAccessToken.SetValue('')

		if not self.AccessTokenSecret is None:
			self.editAccessTokenSecret.SetValue(self.AccessTokenSecret)
		else:
			self.editAccessTokenSecret.SetValue('')

		if not self.Footer is None:
			self.editFooter.SetValue(self.Footer)
		else:
			self.editFooter.SetValue('')

		self._internal_update = False

	def onConfigReset(self, context = None):
		self.enabled = False
		self.AttachImage = False
		self.ConsumerKey = ''
		self.ConsumerSecret = ''
		self.AccessToken = ''
		self.AccessTokenSecret = ''
		self.Footer = ''

	def onConfigLoadFromContext(self, context):
		self.onConfigReset(context)

		try:
			conf = context['config']['twitter']
		except:
			conf = {}

		if 'Enable' in conf:
			self.enabled = conf['Enable']

		if 'AttachImage' in conf:
			self.AttachImage = conf['AttachImage']

		if 'ConsumerKey' in conf:
			self.ConsumerKey = conf['ConsumerKey']

		if 'ConsumerSecret' in conf:
			self.ConsumerSecret = conf['ConsumerSecret']

		if 'AccessToken' in conf:
			self.AccessToken = conf['AccessToken']

		if 'AccessTokenSecret' in conf:
			self.AccessTokenSecret = conf['AccessTokenSecret']

		if 'Footer' in conf:
			self.Footer = conf['Footer']

		self.RefreshUI()
		return True

	def onConfigSaveToContext(self, context):
		context['config']['twitter'] = {
			'Enable' : self.enabled,
			'AttachImage': self.AttachImage,
			'ConsumerKey' : self.ConsumerKey,
			'ConsumerSecret': self.ConsumerSecret,
			'AccessToken': self.AccessToken,
			'AccessTokenSecret': self.AccessTokenSecret,
			'Footer': self.Footer,
		}

	def onConfigApply(self, context):
		self.ApplyUI()

		if not self.ConsumerKey is None:
			self.editConsumerKey.SetValue(self.ConsumerKey)
		else:
			self.editConsumerKey.SetValue('')

		if not self.ConsumerSecret is None:
			self.editConsumerSecret.SetValue(self.ConsumerSecret)
		else:
			self.editConsumerSecret.SetValue('')

		if not self.AccessToken is None:
			self.editAccessToken.SetValue(self.AccessToken)
		else:
			self.editAccessToken.SetValue('')

		if not self.AccessTokenSecret is None:
			self.editAccessTokenSecret.SetValue(self.AccessTokenSecret)
		else:
			self.editAccessTokenSecret.SetValue('')

		if not self.Footer is None:
			self.editAccessTokenSecret.SetValue(self.Footer)
		else:
			self.editAccessTokenSecret.SetValue('')

		self._internal_update = False

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY, size = (640, 360))
		self.page = notebook.InsertPage(0, self.panel, 'Twitter')
		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.layout)
		self.checkEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'Twitter へ戦績を通知する')
		self.checkAttachImage = wx.CheckBox(self.panel, wx.ID_ANY, u'戦績画面を画像添付する')
		self.editFooter = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

		self.radioIkaLogKey = wx.RadioButton(self.panel, wx.ID_ANY, u'IkaLog内部キー')
		self.radioOwnKey = wx.RadioButton(self.panel, wx.ID_ANY, u'自分のキー')

		self.buttonIkaLogAuth = wx.Button(self.panel, wx.ID_ANY, u'Twitter 連携認証')
		self.editConsumerKey = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
		self.editConsumerSecret= wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
		self.editAccessToken = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')
		self.editAccessTokenSecret = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

		try:
			layout = wx.GridSizer(2, 2)
		except:
			layout = wx.GridSizer(2)

		layout.Add(self.radioIkaLogKey)
		layout.Add(self.buttonIkaLogAuth)
		layout.Add(self.radioOwnKey)

		self.layout.Add(self.checkEnable)
		self.layout.Add(self.checkAttachImage)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'フッタ'))

		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'使用するAPIキー'))
		self.layout.Add(layout)

		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Consumer Key'))
		self.layout.Add(self.editConsumerKey, flag = wx.EXPAND)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Consumer Key Secret'))
		self.layout.Add(self.editConsumerSecret, flag = wx.EXPAND)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Access Token'))
		self.layout.Add(self.editAccessToken, flag = wx.EXPAND)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'Access Token Secret'))
		self.layout.Add(self.editAccessTokenSecret, flag = wx.EXPAND)
		self.layout.Add(wx.StaticText(self.panel, wx.ID_ANY, u'フッタ'))
		self.layout.Add(self.editFooter, flag = wx.EXPAND)

		self.panel.SetSizer(self.layout)

	##
	# Post a tweet
	# @param self    The object pointer.
	# @param s       Text to tweet
	# @param media   Media ID
	#
	def tweet(self, s, media = None):
		if media is None:
			params = { "status": s }
		else:
			params = { "status": s, "media_ids": [media] }

		try:
			from requests_oauthlib import OAuth1Session
			twitter = OAuth1Session(self.ConsumerKey, self.ConsumerSecret, self.AccessToken, self.AccessTokenSecret)
			twitter.post(self.url, params = params)
		except:
			print("Twitter: failed to post")

	##
	# Post a screenshot to Twitter
	# @param  self    The object pointer.
	# @param  frame   The image to be posted.
	# @return media   The media ID
	#
	def postMedia(self, frame):
		try:
			from requests_oauthlib import OAuth1Session
			twitter = OAuth1Session(self.ConsumerKey, self.ConsumerSecret, self.AccessToken, self.AccessTokenSecret)

			IkaUtils.writeScreenshot('_image_for_twitter.jpg', cv2.resize(frame, (640,360)))
			files = { "media" : open("_image_for_twitter.jpg", "rb") }
			req = twitter.post(self.url_media, files = files)

			if req.status_code == 200:
				return json.loads(req.text)['media_id']
		except:
			print("Twitter: failed to post image")

		return None

	##
	# getTextGameIndividualResult
	# Generate a record for onGameIndividualResult.
	# @param self      The Object Pointer.
	# @param context   IkaLog context
	#
	def getTextGameIndividualResult(self, context):
		map = IkaUtils.map2text(context['game']['map'])
		rule = IkaUtils.rule2text(context['game']['rule'])
		won = IkaUtils.getWinLoseText(context['game']['won'], win_text ="勝ち", lose_text = "負け", unknown_text = "不明")
		t = datetime.now().strftime("%Y/%m/%d %H:%M")
		return "%sで%sに%sました (%s) %s #IkaLog" % (map, rule, won, t, self.Footer)

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):

		me = IkaUtils.getMyEntryFromContext(context)
		fes_title = IkaUtils.playerTitle(me)
		if IkaUtils.playerTitle(me) and IkaUtils.playerTitle(self.last_me):
			if me['prefix'] != self.last_me['prefix']:
				s = '%sになった！ #IkaLog' % fes_title
				self.tweet(s, media = None)
		self.last_me = me

		s = self.getTextGameIndividualResult(context)
		if not fes_title is None:
			s = "%s (%s)" % (s, fes_title)

		media = self.postMedia(context['engine']['frame']) if self.AttachImage else None
		self.tweet(s, media = media)

	##
	# checkImport
	# Check availability of modules this plugin depends on.
	# @param self      The Object Pointer.
	#
	def checkImport(self):
		try:
			from requests_oauthlib import OAuth1Session
		except:
			print("モジュール requests_oauthlib がロードできませんでした。 Twitter 投稿ができません。")
			print("インストールするには以下のコマンドを利用してください。\n    pip install requests_oauthlib\n")

	##
	# Constructor
	# @param self            The Object Pointer.
	# @param ConsumerKey     Consumer key of the application.
	# @param ConsumerSecret  Comsumer secret.
	# @param AuthToken       Authentication token of the user account.
	# @param AuthTokenSecret Authentication token secret.
	# @param AttachImage     If true, post screenshots.
	#
	def __init__(self, ConsumerKey = None, ConsumerSecret = None, AccessToken = None, AccessTokenSecret = None, attachImage = False, Footer = ''):
		self.enabled = not((ConsumerKey is None) or (ConsumerSecret is None) or (AccessToken is None) or (AccessTokenSecret is None))
		self.ConsumerKey = ConsumerKey
		self.ConsumerSecret = ConsumerSecret
		self.AccessToken = AccessToken
		self.AccessTokenSecret = AccessTokenSecret
		self.AttachImage = attachImage
		self.Footer = ''

		self.checkImport()

if __name__ == "__main__":
	import sys
	obj = IkaOutput_Twitter(
		ConsumerKey=sys.argv[1],
		ConsumerSecret=sys.argv[2],
		AccessToken=sys.argv[3],
		AccessTokenSecret=sys.argv[4]
	)
	print(obj.getTextGameIndividualResult( {
			"game": {
				"map": {"name": "map_name"},
				"rule": {"name": "rule_name"},
				"won": True, }}))
	obj.tweet('＜8ヨ 〜〜')
