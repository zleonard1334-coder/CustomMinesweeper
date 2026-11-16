class Tile(object):
	bomb = False
	value = 0
	state = 0
	percentage = 0.0

	def __init__(self, value, state, bomb):
		self.value = value
		self.state = state # 0 = hidden, 1 = flagged, 2 = questioned, 3 = revealed
		self.bomb = bomb
		self.percentage = -1
		self.percentageComplete = False
		self.percentageKnown = False
