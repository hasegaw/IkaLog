#!python
# -*- coding: utf-8 -*-

class Rect:
	def top(self):
		return self.y

	def right(self):
		return self.x + self.width

	def bottom(self):
		return self.y + self.height

	def left(self):
		return self.x

	def leftTop(self):
		return (self.left(), self.top())

	def rightTop(self):
		return (self.right(), self.top())

	def rightBottom(self):
		return (self.right(), self.bottom())

	def leftBottom(self):
		return (self.left(), self.bottom())

	def size(self):
		return (self.width(), self.height())

	def __init__(self, x, y, width, height):
		self.x = float(x)
		self.y = float(y)
		self.width = float(width)
		self.height = float(height)

class IkaPositionPlayerGeneratior:
	def getPlayerNativeArea(self):
		# 各プレイヤー情報のスタート左位置
		left = 610
		# 各プレイヤー情報の横幅
		width = 610
		# 各プレイヤー情報の高さ
		height = 46

		xoffset = left
		if self.is_me:
			xoffset -= self.me_offset

		return Rect(xoffset, self.start_y, width, height)

	def getPlayerRankNativeArea(self):
		# ランク情報の横オフセット
		rank_xoffset = 0
		# ランク情報の縦オフセット
		rank_yoffset = 20
		# ランク情報の横幅
		rank_width = 43
		# ランク情報の高さ
		rank_height = 25

		pos = self.getPlayerNativeArea()
		pos.x += rank_xoffset
		pos.y += rank_yoffset
		pos.width = rank_width
		pos.height = rank_height
		return pos

	def getPlayerWeaponNativeArea(self):
		# ブキ情報の横オフセット
		weapon_xoffset = 149
		# ブキ情報の横幅
		weapon_width = 46

		pos = self.getPlayerNativeArea()
		pos.x += weapon_xoffset
		pos.width = weapon_width
		return pos
	
	def getPlayerNameNativeArea(self):
		# ナマエ情報の横オフセット
		name_xoffset = 199
		# ナマエ情報の横幅
		name_width = 180

		pos = self.getPlayerNativeArea()
		pos.x += name_xoffset
		pos.width = name_width
		return pos
	
	def getPlayerScoreNativeArea(self):
		# スコア情報の横オフセット
		score_xoffset = 385
		# スコア情報の横幅
		score_width = 115

		pos = self.getPlayerNativeArea()
		pos.x += score_xoffset
		if self.is_me:
			pos.x += self.me_offset
		pos.width = score_width
		return pos
	
	def getPlayerKillCountNativeArea(self):
		# キル情報の横オフセット
		kill_xoffset = 577
		# キル情報の縦オフセット
		kill_yoffset = 0
		# キル情報の横幅
		kill_width = 30
		# キル情報の高さ
		kill_height = 21

		pos = self.getPlayerNativeArea()
		pos.x += kill_xoffset
		if self.is_me:
			pos.x += self.me_offset
		pos.y += kill_yoffset
		pos.width = kill_width
		pos.height = kill_height
		return pos
	
	def getPlayerDeathCountNativeArea(self):
		# デス情報の横オフセット
		death_xoffset = 577
		# デス情報の縦オフセット
		death_yoffset = 21
		# デス情報の横幅
		death_width = 30
		# デス情報の高さ
		death_height = 21

		pos = self.getPlayerNativeArea()
		pos.x += death_xoffset
		if self.is_me:
			pos.x += self.me_offset
		pos.y += death_yoffset
		pos.width = death_width
		pos.height = death_height
		return pos

	def getPlayerArea(self):
		return self.getNativeToReal(self.getPlayerNativeArea())
	
	def getPlayerRankArea(self):
		return self.getNativeToReal(self.getPlayerRankNativeArea())

	def getPlayerWeaponArea(self):
		return self.getNativeToReal(self.getPlayerWeaponNativeArea())

	def getPlayerNameArea(self):
		return self.getNativeToReal(self.getPlayerNameNativeArea())

	def getPlayerScoreArea(self):
		return self.getNativeToReal(self.getPlayerScoreNativeArea())

	def getPlayerKillCountArea(self):
		return self.getNativeToReal(self.getPlayerKillCountNativeArea())

	def getPlayerDeathCountArea(self):
		return self.getNativeToReal(self.getPlayerDeathCountNativeArea())

	def getNativeToReal(self, target):
		fw = float(self.parent.width)
		fh = float(self.parent.height)
		target.x *= fw / 1280.
		target.y *= fh / 720.
		target.width *= fw / 1280.
		target.height *= fh / 720.
		return target

	def __init__(self, parent, start_y, is_me):
		self.parent = parent
		self.start_y = start_y
		self.is_me = is_me

		# 自信のスコア表示オフセット
		self.me_offset = 39

class IkaPositionGenerator:
	def getPlayerPositionGenerator(self, player_index, is_me = False):
		# 各プレイヤー情報の開始位置
		top = [99, 165, 229, 294, 430, 494, 560, 625]

		return IkaPositionPlayerGeneratior(self, top[player_index], is_me)

	def __init__(self, width, height):
		self.width = width
		self.height = height