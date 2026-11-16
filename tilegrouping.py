global ID
ID = 0
class TileGrouping(object):
	tileSet = set([]) # set of the tileList
	tileList = [] # list of [x,y] coords of tiles
	numBombs = 0 # the number of bombs in the grouping
	minBombs = 0 # the minimum number of bombs that the group must contain
		     # this is used for intersections when the actual number of
		     # bombs is unknown.
	maxBombs = 0
	parentGrouping = []
	sourceType = ""
	complete = False # when there are 0 bombs in the group or the number of
			 # bombs equals the number of tiles.

	def __init__(self, tileList, numBombs, minBombs = -1, maxBombs = - 1, pGrouping = [], sType = ""):
		global ID
		self.tileList = tileList
		self.tileSet = set(tileList)
		self.numBombs = numBombs
		self.minBombs = minBombs
		self.maxBombs = maxBombs
		self.ID = ID
		self.parentGrouping = pGrouping
		self.sourceType = sType
		ID += 1

		if self.minBombs == -1:
			self.minBombs = self.numBombs
		if self.maxBombs == -1:
			self.maxBombs = self.numBombs
			
		self.complete = self.isComplete()

	def getTileList(self):
		self.tileList = list(self.tileSet)

	def isComplete(self):
		if (self.maxBombs == self.minBombs):
			self.numBombs = self.maxBombs

		
		if self.complete or (self.numBombs == 0 or self.numBombs == len(self.tileList)):
			self.complete = True
		else:
			self.complete = False
		#print 'P ',self.numBombs, len(self.tileList), self.complete
		return self.complete
	
