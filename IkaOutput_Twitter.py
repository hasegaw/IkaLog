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
import os

# Needed in GUI mode
try:
	import wx
except:
	pass

## IkaOutput_Twitter: IkaLog Output Plugin for Twitter
# 
# Tweet Splatton game events.
class IkaOutput_Twitter:

	## TODO
	_PresetCK = None
	_PresetCS = None

	## API Endpoint for Tweets
	url = "https://api.twitter.com/1.1/statuses/update.json"
	## API Endpoint for Medias (screenshots)
	url_media = "https://upload.twitter.com/1.1/media/upload.json"

	last_me = None

	def ApplyUI(self):

		if self.radioIkaLogKey.GetValue():
			self.ConsumerKeyType = 'ikalog'
		if self.radioOwnKey.GetValue():
			self.ConsumerKeyType = 'own'
		if self._PresetCK is None:
			self.ConsumerKeyType = 'own'

		self.enabled =           self.checkEnable.GetValue()
		self.AttachImage =       self.checkAttachImage.GetValue()
		self.TweetKd =           self.checkTweetKd.GetValue()
		self.ConsumerKey =       self.editConsumerKey.GetValue()
		self.ConsumerSecret =    self.editConsumerSecret.GetValue()
		self.AccessToken =       self.editAccessToken.GetValue()
		self.AccessTokenSecret = self.editAccessTokenSecret.GetValue()
		self.Footer =            self.editFooter.GetValue()

	def OnConsumerKeyModeSwitch(self, event = None):
		if self._PresetCK is None:
			self.radioIkaLogKey.Disable()
			self.radioOwnKey.SetValue(True)
		else:
			self.radioIkaLogKey.Enable()

		if self.radioOwnKey.GetValue():
			self.editConsumerKey.Enable()
			self.editConsumerSecret.Enable()
			self.buttonIkaLogAuth.Disable()
		else:
			self.editConsumerKey.Disable()
			self.editConsumerSecret.Disable()
			self.buttonIkaLogAuth.Enable()

	def RefreshUI(self):
		self._internal_update = True
		self.checkEnable.SetValue(self.enabled)
		self.checkAttachImage.SetValue(self.AttachImage)
		self.checkTweetKd.SetValue(self.TweetKd)

		try:
			{
				'ikalog': self.radioIkaLogKey,
				'own': self.radioOwnKey,
			}[self.ConsumerKeyType].SetValue(True)
		except:
			pass

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
		self.OnConsumerKeyModeSwitch()
		self._internal_update = False

	def onConfigReset(self, context = None):
		self.enabled = False
		self.AttachImage = False
		self.TweetKd = False
		self.ConsumerKeyType = 'ikalog'
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

		if 'TweetKd' in conf:
			self.TweetKd = conf['TweetKd']

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
			'TweetKd': self.TweetKd,
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
			self.editFooter.SetValue(self.Footer)
		else:
			self.editFooter.SetValue('')

		self._internal_update = False

	def OnTestButtonClick(self, event):
		dlg = wx.TextEntryDialog(None, '投稿内容を入力してください', caption='投稿テスト', value='マンメンミ')
		r = dlg.ShowModal()
		s = dlg.GetValue()
		dlg.Destroy()

		if r != wx.ID_OK:
			return

		failure = False
		try:
			# FixMe: tweet() doesn't return result code
			self.tweet(s)
		except:
			failure = True

		# FixMe

	def OnIkaLogAuthButtonClick(self, event):
		from requests_oauthlib import OAuth1Session

		request_token_url = 'https://api.twitter.com/oauth/request_token'
		authorization_url = 'https://api.twitter.com/oauth/authorize'
		access_token_url = 'https://api.twitter.com/oauth/access_token'

		oauth_session = OAuth1Session(self._PresetCK, client_secret = self._PresetCS, callback_uri = 'oob')
		step1 = oauth_session.fetch_request_token(request_token_url)
		auth_web_url = oauth_session.authorization_url(authorization_url)

		msg = "Twitter の利用認証を行います。\n下記のURLをブラウザにペーストし、Twitterサイトで認証ページを開いてください。"

		dlg = wx.TextEntryDialog(None, msg, caption='OAuth認証', value=auth_web_url)
		r = dlg.ShowModal()
		dlg.Destroy()

		if r != wx.ID_OK:
			return

		msg = "Twitter サイトにて認証に成功すると PIN コードが表示されます。\n表示された PIN コードを下記に入力してください。"

		dlg = wx.TextEntryDialog(None, msg, caption='OAuth認証', value='')
		dlg.ShowModal()
		pin = dlg.GetValue()
		dlg.Destroy()

		if r != wx.ID_OK:
			return

		oauth_session.params['oauth_verifier'] = pin
		r = oauth_session.get('%s?oauth_token=%s' % (access_token_url, step1['oauth_token']))

		d = oauth_session.parse_authorization_response('?' + r.text)
		AT = d['oauth_token']
		ATS = d['oauth_token_secret']

		self.radioIkaLogKey.SetValue(True)
		self.ConsumerKeyType = 'ikalog'
		self.AccessToken = AT
		self.AccessTokenSecret = ATS
		self.ScreenName = d['screen_name']

		self.RefreshUI()

	def onOptionTabCreate(self, notebook):
		self.panel = wx.Panel(notebook, wx.ID_ANY)
		self.page = notebook.InsertPage(0, self.panel, 'Twitter')
		self.layout = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.layout)
		self.checkEnable = wx.CheckBox(self.panel, wx.ID_ANY, u'Twitter へ戦績を通知する')
		self.checkAttachImage = wx.CheckBox(self.panel, wx.ID_ANY, u'戦績画面を画像添付する')
		self.checkTweetKd = wx.CheckBox(self.panel, wx.ID_ANY, u'K/D を投稿する')
		self.editFooter = wx.TextCtrl(self.panel, wx.ID_ANY, u'hoge')

		self.radioIkaLogKey = wx.RadioButton(self.panel, wx.ID_ANY, u'IkaLog内部キー')
		self.radioOwnKey = wx.RadioButton(self.panel, wx.ID_ANY, u'自分のキー')

		self.buttonIkaLogAuth = wx.Button(self.panel, wx.ID_ANY, u'Twitter 連携認証')
		self.buttonTest = wx.Button(self.panel, wx.ID_ANY, u'投稿テスト(反映済みの設定を使用します)')
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
		self.layout.Add(self.checkTweetKd)
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
		self.layout.Add(self.buttonTest)

		self.panel.SetSizer(self.layout)

		self.radioIkaLogKey.Bind(wx.EVT_RADIOBUTTON, self.OnConsumerKeyModeSwitch)
		self.radioOwnKey.Bind(wx.EVT_RADIOBUTTON, self.OnConsumerKeyModeSwitch)
		self.buttonIkaLogAuth.Bind(wx.EVT_BUTTON, self.OnIkaLogAuthButtonClick)
		self.buttonTest.Bind(wx.EVT_BUTTON, self.OnTestButtonClick)

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

		from requests_oauthlib import OAuth1Session

		CK = self._PresetCK if self.ConsumerKeyType == 'ikalog' else self.ConsumerKey
		CS = self._PresetCS if self.ConsumerKeyType == 'ikalog' else self.ConsumerSecret

		twitter = OAuth1Session(CK, CS, self.AccessToken, self.AccessTokenSecret)
		twitter.post(self.url, params = params)

	##
	# Post a screenshot to Twitter
	# @param  self    The object pointer.
	# @param  frame   The image to be posted.
	# @return media   The media ID
	#
	def postMedia(self, frame):

		if IkaUtils.isWindows():
			temp_file = os.path.join(os.environ['TMP'], '_image_for_twitter.jpg')
		else:
			temp_file = '_image_for_twitter.jpg'

		IkaUtils.writeScreenshot(temp_file, cv2.resize(frame, (640, 360)))

		files = { "media" : open(temp_file, "rb") }

		CK = self._PresetCK if self.ConsumerKeyType == 'ikalog' else self.ConsumerKey
		CS = self._PresetCS if self.ConsumerKeyType == 'ikalog' else self.ConsumerSecret

		from requests_oauthlib import OAuth1Session
		twitter = OAuth1Session(CK, CS, self.AccessToken, self.AccessTokenSecret)
		req = twitter.post(self.url_media, files = files)

		if req.status_code == 200:
			return json.loads(req.text)['media_id']

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

		s = '%sで%sに%sました' % (map, rule, won)

		me = IkaUtils.getMyEntryFromContext(context)
		if ('kills' in me) and ('deaths' in me) and self.TweetKd:
			s = '%s %dk/%dd' % (s, me['kills'], me['deaths'])

		fes_title = IkaUtils.playerTitle(me)
		if fes_title:
			s = '%s %s' % (s, fes_title)

		s = '%s (%s) %s #IkaLog' % (s, t, self.Footer)
		return s

	##
	# onGameIndividualResult Hook
	# @param self      The Object Pointer
	# @param context   IkaLog context
	#
	def onGameIndividualResult(self, context):
		IkaUtils.dprint('%s (enabled = %s)' % (self, self.enabled))

		if not self.enabled:
			return False

		s = self.getTextGameIndividualResult(context)
		IkaUtils.dprint('投稿内容 %s' % s)

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
	def __init__(self, ConsumerKey = None, ConsumerSecret = None, AccessToken = None, AccessTokenSecret = None, attachImage = False, Footer = '', TweetKd = False):
		self.enabled = not((ConsumerKey is None) or (ConsumerSecret is None) or (AccessToken is None) or (AccessTokenSecret is None))
		self.ConsumerKeyType = 'own'
		self.ConsumerKey = ConsumerKey
		self.ConsumerSecret = ConsumerSecret
		self.AccessToken = AccessToken
		self.AccessTokenSecret = AccessTokenSecret
		self.AttachImage = attachImage
		self.TweetKd = TweetKd
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
