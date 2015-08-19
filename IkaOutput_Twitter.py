#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## @package IkaOutput_Twitter

from IkaUtils import *

from datetime import datetime
import json
import cv2

## IkaOutput_Twitter: IkaLog Output Plugin for Twitter
# 
# Tweet Splatton game events.
class IkaOutput_Twitter:
	## API Endpoint for Tweets
	url = "https://api.twitter.com/1.1/statuses/update.json"
	## API Endpoint for Medias (screenshots)
	url_media = "https://upload.twitter.com/1.1/media/upload.json"

	## Post a tweet
	#
	# @param self    The object pointer.
	# @param s       Text to tweet
	# @param media   Media ID
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
		finally:
			pass

	## Post a screenshot to Twitter
	#
	# @param  self    The object pointer.
	# @param  frame   The image to be posted.
	# @return media   The media ID
	def postMedia(self, frame):
		try:
			from requests_oauthlib import OAuth1Session
			twitter = OAuth1Session(self.ConsumerKey, self.ConsumerSecret, self.AccessToken, self.AccessTokenSecret)

			IkaUtils.writeScreenshot('_image_for_twitter.jpg', cv2.resize(frame, (640,360)))
			files = { "media" : open("_image_for_twitter.jpg", "rb") }
			req = twitter.post(self.url_media, files = files)

			if req.status_code == 200:
				return json.loads(req.text)['media_id']
		finally:
			pass

		return None

	## GameStart Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name.
	# @param mode_name Mode name.
	def onGameStart(self, frame, map_name, mode_name):
		pass

	## getRecordResultDetail
	#
	# Generate a message for ResultDetail.
	# @param self      The Object Pointer.
	# @param map_name  Map name.
	# @param mode_name Mode name.
	# @param won       True is player's team won. Otherwise False.
	def getRecordResultDetail(self, map_name, mode_name, won):
		t = datetime.now().strftime("%Y/%m/%d %H:%M")
		s_won = IkaUtils.getWinLoseText(won, win_text ="勝ち", lose_text = "負け", unknown_text = "不明")
		return "%sで%sに%sました (%s) #IkaLog" % (map_name, mode_name, s_won, t)

	## onResultDetail
	#
	# ResultDetail Hook
	#
	# @param self      The Object Pointer
	# @param frame     Screenshot image
	# @param map_name  Map name
	# @param mode_name Mode name
	# @param won       True if the player's team won. Otherwise False
	def onResultDetail(self, frame, map_name, mode_name, won):
		s = self.getRecordResultDetail(map_name, mode_name, won)
		media = self.postMedia(frame) if self.attachImage else None
		self.tweet(s, media = media)

	## checkImport
	#
	# Check availability of modules this plugin depends on.
	# @param self      The Object Pointer.
	def checkImport(self):
		try:
			from requests_oauthlib import OAuth1Session
		except:
			print("モジュール requests_oauthlib がロードできませんでした。 Twitter 投稿ができません。")
			print("インストールするには以下のコマンドを利用してください。\n    pip install requests_oauthlib\n")
		finally:
			pass

	## Constructor
	#
	# @param self            The Object Pointer.
	# @param ConsumerKey     Consumer key of the application.
	# @param ConsumerSecret  Comsumer secret.
	# @param AuthToken       Authentication token of the user account.
	# @param AuthTokenSecret Authentication token secret.
	# @param attachImage     If true, post screenshots.
	def __init__(self, ConsumerKey = None, ConsumerSecret = None, AccessToken = None, AccessTokenSecret = None, attachImage = False):
		self.ConsumerKey = ConsumerKey
		self.ConsumerSecret = ConsumerSecret
		self.AccessToken = AccessToken
		self.AccessTokenSecret = AccessTokenSecret
		self.attachImage = attachImage

		self.checkImport()

if __name__ == "__main__":
	import sys
	obj = IkaOutput_Twitter(
		ConsumerKey=sys.argv[1],
		ConsumerSecret=sys.argv[2],
		AccessToken=sys.argv[3],
		AccessTokenSecret=sys.argv[4]
	)
	print(obj.getRecordResultDetail('map', 'mode', True))
	obj.tweet('＜8ヨ 〜〜')
