#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

class IkaOutput_Fluentd:

	def onGameStart(self, frame, map_name, mode_name):
		pass

	def onResultDetail(self, frame, map_name, mode_name, won):
		s_won = "win" if won else "lose"
		try:
			from fluent import sender
			from fluent import event
			if self.host is None:
				sender = sender.setup(self.tag)
			else:
				sender.setup(self.tag, host = self.host, port = self.port)

			event.Event('GameResult', {
					'username': self.username,
					'map': map_name,
					'mode': mode_name,
					'result': s_won
			} )
		finally:
			pass

	def __init__(self, tag = 'ikalog', username = 'ika', host = None, port = 24224):
		self.tag = tag
		self.username = username
		self.host = host
		self.port = port

if __name__ == "__main__":
	obj = IkaOutput_Fluentd()
	obj.onResultDetail(None, 'mapNap', 'modeName', True)
