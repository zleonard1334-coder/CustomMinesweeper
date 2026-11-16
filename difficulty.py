class Difficulty(object):
	width = 0
	height = 0
	bombs = 0
	name = ""
	hotKey = ""
	hotKeyLabel = ""
	index = -1

	def __init__(self,w,h,b,n,hk,hkl,i):
		self.width = w
		self.height = h
		self.bombs = b
		self.name = n
		self.hotKey = hk
		self.hotKeyLabel = hkl
		self.index = i
