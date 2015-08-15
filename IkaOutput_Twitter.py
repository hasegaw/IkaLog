#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
#
# Tweet the game result
#
from datetime import datetime
import json
import cv2

class IkaOutput_Twitter:
	url_media = "https://upload.twitter.com/1.1/media/upload.json"
	url = "https://api.twitter.com/1.1/statuses/update.json"
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

	def postMedia(self, frame):
		try:
			from requests_oauthlib import OAuth1Session
			twitter = OAuth1Session(self.ConsumerKey, self.ConsumerSecret, self.AccessToken, self.AccessTokenSecret)

			cv2.imwrite('_image_for_twitter.jpg', cv2.resize(frame, (640,360)))
			files = { "media" : open("_image_for_twitter.jpg", "rb") }
			req = twitter.post(self.url_media, files = files)

			if req.status_code == 200:
				return json.loads(req.text)['media_id']
		finally:
			pass

		return None

	def onGameStart(self, frame, map_name, mode_name):
		pass

	def onResultDetail(self, frame, map_name, mode_name, won):
		t = datetime.now().strftime("%Y/%m/%d %H:%M")
		s_won = "勝ち" if won else "負け"
		s = "%sで%sに%sました (%s) #IkaLog" % (map_name, mode_name, s_won, t)
		media = self.postMedia(frame) if self.attachImage else None

		self.tweet(s, media = media)

	def __init__(self, ConsumerKey = None, ConsumerSecret = None, AccessToken = None, AccessTokenSecret = None, attachImage = False):
		self.ConsumerKey = ConsumerKey
		self.ConsumerSecret = ConsumerSecret
		self.AccessToken = AccessToken
		self.AccessTokenSecret = AccessTokenSecret
		self.attachImage = attachImage

if __name__ == "__main__":
	import sys
	obj = IkaOutput_Twitter(
		ConsumerKey=sys.argv[1],
		ConsumerSecret=sys.argv[2],
		AccessToken=sys.argv[3],
		AccessTokenSecret=sys.argv[4]
	)
	obj.tweet('＜8ヨ 〜〜')
