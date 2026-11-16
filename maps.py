import tile
import tilegrouping
import copy
import random

class Maps(object):
	width = 0
	height = 0
	numBombs = 0
	tiles = []
	tileGroupings = []
	tilesChangedSinceLastGrouping = True
	
	def __init__(self, width, height, numBombs):
		self.width = width
		self.height = height
		self.numBombs = numBombs
		self.tiles = []
		self.lastCounts = 0
		self.tileGroupings = []
		self.tilesChangedSinceLastGrouping = True
		for i in range(self.width):
			
			temp = []
			for j in range(self.height):
				temp_t = 0
				temp_t = tile.Tile(0,0,False)
				temp.append(temp_t)		
			self.tiles.append(temp)

	def numFlags(self,x,y):
		flags = 0
		for i in range(x-1,x+2):
			for j in range(y-1,y+2):
				if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and self.tiles[i][j].state == 1:
					flags += 1
		return flags

	def numTiles(self,x,y):
		tiles = 0
		for i in range(x-1,x+2):
			for j in range(y-1,y+2):
				if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and self.tiles[i][j].state == 0:
					tiles += 1
		return tiles

	def cheatAll(self, fl, cts):		
		hasChanged = True
		while(hasChanged):
			self.processTileGroupings(fl,cts)
			hasChanged = False
			for x in range(self.width):
				for y in range(self.height):
					if self.tiles[x][y].state == 0 and self.tiles[x][y].percentage == 100:
						self.tiles[x][y].state = 1
						hasChanged = True
					elif self.tiles[x][y].state == 0 and self.tiles[x][y].percentage == 0:
						self.reveal(x,y)
						hasChanged = True
			self.revealAll()


	def genTileGroupings(self, remainingBombs):
		
		rb = remainingBombs
		newTileGroupings = []
		groupedTiles = []
		groupedBombs = 0
		groupedBombTiles = []
		for x in range(self.width):
			for y in range(self.height):
				flags = 0
				tempGroupList = []
				if not(self.tiles[x][y].percentageComplete):
					self.tiles[x][y].percentage = -1
					self.tiles[x][y].percentageKnown = False
				if self.tiles[x][y].state == 3 and self.tiles[x][y].value > 0:
					for i in range(x-1,x+2):
						for j in range(y-1,y+2):
							if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and ((self.tiles[i][j].state == 1) or (self.tiles[i][j].percentageComplete and self.tiles[i][j].percentage == 100)):
								flags += 1
								if self.tiles[i][j].state != 1 and (i,j) not in groupedBombTiles:
									groupedBombTiles.append((i,j))
									groupedBombs += 1
								

					
					if self.tiles[x][y].value - flags > 0:
						for i in range(x-1,x+2):
							for j in range(y-1,y+2):
								if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and (self.tiles[i][j].state == 0 or self.tiles[i][j].state == 2) and not(self.tiles[i][j].percentageComplete):
									tempGroupList.append((i,j))
									groupedTiles.append((i,j))

						if len(tempGroupList) > 0:
							tempTemp = tilegrouping.TileGrouping(tempGroupList, self.tiles[x][y].value - flags, -1, -1, [], "gen")
							newTileGroupings.append(tempTemp)
				elif self.tiles[x][y].state == 1:
					tempGroupList.append((x,y))
					groupedTiles.append((x,y))
					tempTemp = tilegrouping.TileGrouping(tempGroupList, 1, 1, 1, [], "gen")
					newTileGroupings.append(tempTemp)
				elif self.tiles[x][y].percentageComplete and self.tiles[x][y].percentage == 100 and self.tiles[x][y].state == 0:
					tempGroupList.append((x,y))
					groupedTiles.append((x,y))
					tempTemp = tilegrouping.TileGrouping(tempGroupList, 1, 1, 1, [], "gen")
					newTileGroupings.append(tempTemp)
				elif self.tiles[x][y].percentageComplete and self.tiles[x][y].percentage == 0 and self.tiles[x][y].state == 0:
					tempGroupList.append((x,y))
					groupedTiles.append((x,y))
					tempTemp = tilegrouping.TileGrouping(tempGroupList, 0, 0, 0, [], "gen")
					newTileGroupings.append(tempTemp)
		groupedTileSet = set(groupedTiles)
		ungroupedTiles = []
		ungroupedBombs = 0
		for x in range(self.width):
			for y in range(self.height):
				if self.tiles[x][y].state == 0 and (x,y) not in groupedTileSet:
					ungroupedTiles.append((x,y))
		ungroupedBombs = remainingBombs - groupedBombs
		for i in ungroupedTiles:
			if ungroupedBombs == 0:
				self.tiles[i[0]][i[1]].percentage = 0
				self.tiles[i[0]][i[1]].percentageComplete = True
			elif not (self.tiles[i[0]][i[1]].percentageComplete):
				self.tiles[i[0]][i[1]].percentage = int((100*ungroupedBombs)/len(ungroupedTiles))
		return newTileGroupings


	def processTileGroupings(self, remainingBombs, counts):
		# The algorithm works as follows:
		# "Tile Groupings" are formed by revealed numbers on the map. A grouping has a set number of remaining bombs in it based on the number displayed and flags placed.
		# Groupings can intersect each other to narrow down possible bomb locations.
		# A group is "Complete" when the number of remaining bombs is 0, when the number of bombs matches the number of available tiles, or when it intersects with another group allowing bomb subtraction.
		
		if self.tilesChangedSinceLastGrouping or counts != self.lastCounts:
			self.lastCounts = counts
			primaryGroupings = self.genTileGroupings(remainingBombs) # get the list of groupings from the tiles, pre processing
			self.tileGroupings = [copy.deepcopy(i) for i in primaryGroupings] # at the start, the grouping is just the primary grouping
			existingGroupSets = [copy.deepcopy(i.tileSet) for i in self.tileGroupings]
			groupingHasChanged = True
			c = 0
			while(c < counts):
				groupingHasChanged = False
				newGroupSets = []
				if c % 2 == 1:					
					self.tileGroupings.reverse()
				#else:
					#random.shuffle(self.tileGroupings)
				tGL = len(self.tileGroupings)
				tGL0 = len(self.tileGroupings)
				#print tGL
				i = 0
				
				while(i < tGL0):
					j = 0
					while(j < tGL0):
						modded = False
						#inclusive groupings
						
						if c > 1 or (self.tileGroupings[i].sourceType == 'gen' or self.tileGroupings[j].sourceType == 'gen'):
							if self.tileGroupings[i].ID != self.tileGroupings[j].ID and len(self.tileGroupings[i].tileList) != len(self.tileGroupings[j].tileList) and (not(self.tileGroupings[j].isComplete()) or not(self.tileGroupings[i].isComplete())):
								if (len(self.tileGroupings[i].tileList) > len(self.tileGroupings[j].tileList)):
									b = i #big
									s = j #small
								else:
									b = j
									s = i
								# The smaller group is a subset of the larger group, the number of bombs isn't unknown, and we're at the start of our search or the smaller grouping is complete
								if (self.tileGroupings[s].tileSet & self.tileGroupings[b].tileSet) == self.tileGroupings[s].tileSet and (self.tileGroupings[s].numBombs != -1) and (c < 3 or self.tileGroupings[s].isComplete()):
									#print 'inclusion', self.tileGroupings[b].tileSet, self.tileGroupings[s].tileSet, self.tileGroupings[b].maxBombs, self.tileGroupings[b].minBombs, self.tileGroupings[s].maxBombs, self.tileGroupings[s].minBombs
									modded = True
									groupingHasChanged = True
									self.tileGroupings[b].parentGrouping = [copy.deepcopy(self.tileGroupings[b])]
									self.tileGroupings[b].sourceType = 'inclusion'
									if self.tileGroupings[b].tileSet in newGroupSets:
										newGroupSets.remove(self.tileGroupings[b].tileSet)
									self.tileGroupings[b].tileSet -= self.tileGroupings[s].tileSet
									self.tileGroupings[b].getTileList()
									self.tileGroupings[b].minBombs -= min(self.tileGroupings[s].maxBombs,self.tileGroupings[b].minBombs)
									self.tileGroupings[b].maxBombs = min(self.tileGroupings[b].maxBombs - self.tileGroupings[s].minBombs, len(self.tileGroupings[b].tileList)) 
									if self.tileGroupings[b].numBombs >= 0 and self.tileGroupings[s].numBombs >= 0:
										self.tileGroupings[b].numBombs -= self.tileGroupings[s].numBombs
									elif self.tileGroupings[s].numBombs < 0:
										self.tileGroupings[b].numBombs = -1 #unkown actual bombs									
										
									if self.tileGroupings[b].minBombs == self.tileGroupings[b].maxBombs:
										self.tileGroupings[b].numBombs = self.tileGroupings[b].maxBombs
									
										
							if not(modded) and self.tileGroupings[i].ID != self.tileGroupings[j].ID and (not(self.tileGroupings[j].isComplete()) or not(self.tileGroupings[i].isComplete())):
								intersect = self.tileGroupings[i].tileSet & self.tileGroupings[j].tileSet
								if intersect == self.tileGroupings[i].tileSet or intersect == self.tileGroupings[j].tileSet:
									intersect = set([])
								# If the 2 groupings intersect but not completely
								elif len(intersect) > 0:
									# Create new sets from the tiles outside the i & j intersection
									iMjSet = self.tileGroupings[i].tileSet - self.tileGroupings[j].tileSet

									jMiSet = self.tileGroupings[j].tileSet - self.tileGroupings[i].tileSet
									# If the number of bombs in both groupings is known
									if self.tileGroupings[i].numBombs != -1 and self.tileGroupings[j].numBombs != -1:
										# if the remaining set of tiles is smaller than the number of bombs in either set, the intersecton must contain some number of bombs
										if len(iMjSet) <= self.tileGroupings[i].numBombs or len(jMiSet) <= self.tileGroupings[j].numBombs:
											#print 'exclusion 1', intersect,self.tileGroupings[i].tileSet,self.tileGroupings[i].numBombs,self.tileGroupings[i].maxBombs,self.tileGroupings[i].minBombs ,self.tileGroupings[j].tileSet,self.tileGroupings[j].numBombs,self.tileGroupings[j].maxBombs,self.tileGroupings[j].minBombs ,  iMjSet, jMiSet, self.tileGroupings[i].isComplete(), self.tileGroupings[j].isComplete()

											# Create a new grouping from the intersection of the two groupings, i and j, the minimum number of bombs is the greater of the number of bombs in i or j minus the respective tiles outside the intersection.
											# The maximum number of bombs is the lowest of: the size of the intersection (all bombs), the smaller of the number of bombs in i or j.
											tempNewGroup = tilegrouping.TileGrouping(list(intersect),-1,max(self.tileGroupings[i].numBombs - len(iMjSet),self.tileGroupings[j].numBombs - len(jMiSet)),min(len(intersect),self.tileGroupings[i].numBombs,self.tileGroupings[j].numBombs),[copy.deepcopy(self.tileGroupings[i]),copy.deepcopy(self.tileGroupings[j])],'exclusion child')
											#if (tempNewGroup.maxBombs == 0 or tempNewGroup.minBombs > 0) and len(tempNewGroup.tileSet) > 1 :
											if True:

												modded = True
												tempOldGroup = copy.deepcopy(self.tileGroupings[i])
												tempOldGroup2 = copy.deepcopy(self.tileGroupings[j])
												groupingHasChanged = True
												# If grouping i is not complete and there still is at least 1 bomb left in the portion of i outside of the intersection with j.
												if not(self.tileGroupings[i].isComplete()) and self.tileGroupings[i].minBombs - min(self.tileGroupings[i].minBombs,tempNewGroup.maxBombs) > 0:
													# Remove the intersection of i and j from the grouping i
													self.tileGroupings[i].parentGrouping = [copy.deepcopy(self.tileGroupings[i])]
													self.tileGroupings[i].sourceType = 'exclusion parent'
													self.tileGroupings[i].tileList = list(iMjSet)
													self.tileGroupings[i].tileSet = copy.deepcopy(iMjSet)
													self.tileGroupings[i].maxBombs = min(self.tileGroupings[i].maxBombs-tempNewGroup.minBombs,len(iMjSet))
													self.tileGroupings[i].minBombs -= min(self.tileGroupings[i].minBombs,tempNewGroup.maxBombs)
													self.tileGroupings[i].numBombs = -1
													if tempOldGroup.tileSet not in newGroupSets:
														self.tileGroupings.append(copy.deepcopy(tempOldGroup))
														newGroupSets.append(copy.deepcopy(tempOldGroup.tileSet))
														tGL += 1
													#elif tempOldGroup.sourceType == 'gen':
														#print '1    1    ',tempOldGroup.tileSet,newGroupSets
												if not(self.tileGroupings[j].isComplete()) and self.tileGroupings[j].minBombs - min(self.tileGroupings[j].minBombs,tempNewGroup.maxBombs) > 0:
													self.tileGroupings[j].parentGrouping = [copy.deepcopy(self.tileGroupings[j])]
													self.tileGroupings[j].sourceType = 'exclusion parent'
													self.tileGroupings[j].tileList = list(jMiSet)
													self.tileGroupings[j].tileSet = copy.deepcopy(jMiSet)
													self.tileGroupings[j].maxBombs = min(self.tileGroupings[j].maxBombs - tempNewGroup.minBombs, len(jMiSet))
													self.tileGroupings[j].minBombs -= min(self.tileGroupings[j].minBombs,tempNewGroup.maxBombs)
													self.tileGroupings[j].numBombs = -1
													if tempOldGroup2.tileSet not in newGroupSets:
														self.tileGroupings.append(copy.deepcopy(tempOldGroup2))
														newGroupSets.append(copy.deepcopy(tempOldGroup2.tileSet))
														tGL += 1
													#elif tempOldGroup2.sourceType == 'gen':
														#print '1    2    ',tempOldGroup2.tileSet,newGroupSets
												if self.tileGroupings[i].minBombs == self.tileGroupings[i].maxBombs:
													self.tileGroupings[i].numBombs = self.tileGroupings[i].maxBombs
												if self.tileGroupings[j].minBombs == self.tileGroupings[j].maxBombs:
													self.tileGroupings[j].numBombs = self.tileGroupings[j].maxBombs
												#print 'POST exclusion 1', intersect,self.tileGroupings[i].tileSet,self.tileGroupings[i].numBombs,self.tileGroupings[i].maxBombs,self.tileGroupings[i].minBombs ,self.tileGroupings[j].tileSet,self.tileGroupings[j].numBombs,self.tileGroupings[j].maxBombs,self.tileGroupings[j].minBombs ,  iMjSet, jMiSet, self.tileGroupings[i].isComplete(), self.tileGroupings[j].isComplete()
												if (not(self.tileGroupings[j].isComplete()) or self.tileGroupings[j].tileSet == jMiSet) and (not(self.tileGroupings[i].isComplete()) or self.tileGroupings[i].tileSet == iMjSet):
													
													if tempNewGroup.tileSet not in newGroupSets and  tempNewGroup.tileSet not in existingGroupSets:
														self.tileGroupings.append(copy.deepcopy(tempNewGroup))
														newGroupSets.append(copy.deepcopy(tempNewGroup.tileSet))
														tGL += 1
													#else:
														#print 'did not add', intersect
														
												#else:
													#print 'outer did not add', intersect,self.tileGroupings[i].isComplete(),self.tileGroupings[j].isComplete()
												
											
				
									else:
										# If we don't know how many bombs are in i and j but we do know that there is at least 1 bomb in the intersection
										if len(iMjSet) <= self.tileGroupings[i].minBombs or len(jMiSet) <= self.tileGroupings[j].minBombs:
											#print 'exclusion 2', intersect,self.tileGroupings[i].tileSet,self.tileGroupings[i].numBombs,self.tileGroupings[i].maxBombs,self.tileGroupings[i].minBombs ,self.tileGroupings[j].tileSet,self.tileGroupings[j].numBombs,self.tileGroupings[j].maxBombs,self.tileGroupings[j].minBombs ,  iMjSet, jMiSet, self.tileGroupings[i].isComplete(), self.tileGroupings[j].isComplete()
											
											tempNewGroup = tilegrouping.TileGrouping(list(intersect),-1,max(self.tileGroupings[i].minBombs - len(iMjSet),self.tileGroupings[j].minBombs - len(jMiSet)),min(len(intersect),self.tileGroupings[i].maxBombs,self.tileGroupings[j].maxBombs),[copy.deepcopy(self.tileGroupings[i]),copy.deepcopy(self.tileGroupings[j])],'exclusion child')
											#if (tempNewGroup.maxBombs == 0 or tempNewGroup.minBombs > 0) and len(tempNewGroup.tileSet) > 1 :
											if True:
												modded = True
												tempOldGroup = copy.deepcopy(self.tileGroupings[i])
												tempOldGroup2 = copy.deepcopy(self.tileGroupings[j])
												groupingHasChanged = True	
												if not(self.tileGroupings[i].isComplete()) and self.tileGroupings[i].minBombs - min(self.tileGroupings[i].minBombs,tempNewGroup.maxBombs) > 0:
													self.tileGroupings[i].parentGrouping = [copy.deepcopy(self.tileGroupings[i])]
													self.tileGroupings[i].sourceType = 'exclusion parent'
													self.tileGroupings[i].tileList = list(iMjSet)
													self.tileGroupings[i].tileSet = iMjSet
													self.tileGroupings[i].maxBombs = min(self.tileGroupings[i].maxBombs-tempNewGroup.minBombs,len(iMjSet))
													self.tileGroupings[i].minBombs -= min(self.tileGroupings[i].minBombs,tempNewGroup.maxBombs)
													self.tileGroupings[i].numBombs = -1
													self.tileGroupings[i].complete = self.tileGroupings[i].isComplete()
													if tempOldGroup.tileSet not in newGroupSets :
														self.tileGroupings.append(copy.deepcopy(tempOldGroup))
														newGroupSets.append(copy.deepcopy(tempOldGroup.tileSet))
														tGL += 1
													#elif tempOldGroup.sourceType == 'gen':
														#print '2    2    ',tempOldGroup.tileSet,newGroupSets
												if not(self.tileGroupings[j].isComplete()) and self.tileGroupings[j].minBombs - min(self.tileGroupings[j].minBombs,tempNewGroup.maxBombs) > 0:
													self.tileGroupings[j].parentGrouping = [copy.deepcopy(self.tileGroupings[j])]
													self.tileGroupings[j].sourceType = 'exclusion parent'
													self.tileGroupings[j].tileList = list(jMiSet)
													self.tileGroupings[j].tileSet = jMiSet
													self.tileGroupings[j].maxBombs = min(self.tileGroupings[j].maxBombs - tempNewGroup.minBombs, len(jMiSet))
													self.tileGroupings[j].minBombs -= min(self.tileGroupings[j].minBombs,tempNewGroup.maxBombs)
													self.tileGroupings[j].numBombs = -1
													self.tileGroupings[j].complete = self.tileGroupings[j].isComplete()
													if tempOldGroup2.tileSet not in newGroupSets:
														self.tileGroupings.append(copy.deepcopy(tempOldGroup2))
														newGroupSets.append(copy.deepcopy(tempOldGroup2.tileSet))
														tGL += 1
													#elif tempOldGroup2.sourceType == 'gen':
														#print '2    2    ',tempOldGroup2.tileSet,newGroupSets
												if self.tileGroupings[i].minBombs == self.tileGroupings[i].maxBombs:
													self.tileGroupings[i].numBombs = self.tileGroupings[i].maxBombs
												if self.tileGroupings[j].minBombs == self.tileGroupings[j].maxBombs:
													self.tileGroupings[j].numBombs = self.tileGroupings[j].maxBombs
												#print 'POST exclusion 2', intersect,self.tileGroupings[i].tileSet,self.tileGroupings[i].numBombs,self.tileGroupings[i].maxBombs,self.tileGroupings[i].minBombs ,self.tileGroupings[j].tileSet,self.tileGroupings[j].numBombs,self.tileGroupings[j].maxBombs,self.tileGroupings[j].minBombs ,  iMjSet, jMiSet, self.tileGroupings[i].isComplete(), self.tileGroupings[j].isComplete()	
												if (not(self.tileGroupings[j].isComplete()) or self.tileGroupings[j].tileSet == jMiSet) and (not(self.tileGroupings[i].isComplete()) or self.tileGroupings[i].tileSet == iMjSet):
													
													if tempNewGroup.tileSet not in newGroupSets and  tempNewGroup.tileSet not in existingGroupSets:
														self.tileGroupings.append(copy.deepcopy(tempNewGroup))
														newGroupSets.append(copy.deepcopy(tempNewGroup.tileSet))
														tGL += 1
													#else: #print 'did not add', intersect
												#else: #print 'outer did not add', intersect,self.tileGroupings[i].isComplete(),self.tileGroupings[j].isComplete()
											
											
						if self.tileGroupings[j].maxBombs == self.tileGroupings[j].minBombs and self.tileGroupings[j].numBombs != self.tileGroupings[j].maxBombs:
							self.tileGroupings[j].numBombs = self.tileGroupings[j].maxBombs
							groupingHasChanged = True
						tGL = len(self.tileGroupings)
						j += 1
					if self.tileGroupings[i].maxBombs == self.tileGroupings[i].minBombs and self.tileGroupings[i].numBombs != self.tileGroupings[i].maxBombs:
						self.tileGroupings[i].numBombs = self.tileGroupings[i].maxBombs
						groupingHasChanged = True
					tGL = len(self.tileGroupings)
					i += 1
				
				c += 1
					
				secondaryGroupingSets = [i.tileSet for i in self.tileGroupings]
				
				tempList = []
				for i in primaryGroupings:
					if i.tileSet not in secondaryGroupingSets and c == 1:
						tempList.append(copy.deepcopy(i))

				if len(tempList) > 0:
					self.tileGroupings.extend(tempList) 
			
				completeSet100 = set([])
				completeSet0 = set([])
				
				for i in self.tileGroupings:
					
					if (i.isComplete()):
						if i.numBombs == 0:
							completeSet0 = completeSet0 | i.tileSet
						else:
							completeSet100 = completeSet100 | i.tileSet


				ii = 0
				iC = len(self.tileGroupings)

				setList = []
				for i in self.tileGroupings:
					setList.append(i.tileSet)

				# consolidate grouping 100s and 0s
				while (ii < iC):
					i = self.tileGroupings[ii]
					i2 = copy.deepcopy(i)
					inter = i.tileSet & completeSet100
					i.tileSet -= inter
					
					i.numBombs = max(-1,i.numBombs - len(inter))
					i.minBombs = i.minBombs - len(inter)
					i.maxBombs = i.maxBombs - len(inter)

					
					
					

					inter0 = i.tileSet & completeSet0
					i.tileSet -= inter0

					i.tileList = list(i.tileSet)
					if len(i2.tileSet) != len(i.tileSet):
						i.parentGrouping = [copy.deepcopy(i2)]
						i.sourceType = 'consolidate'

					if len(inter) > 0 and inter not in setList:
						if len(i.tileList) == 0:
							tempTemp = tilegrouping.TileGrouping(list(inter),len(inter),len(inter),len(inter),copy.deepcopy(i2.parentGrouping), 'intersect 100')						
						else:
							tempTemp = tilegrouping.TileGrouping(list(inter),len(inter),len(inter),len(inter),[copy.deepcopy(i2)], 'intersect 100')
						#print inter,tempTemp.isComplete()
						self.tileGroupings.append(copy.deepcopy(tempTemp))
						setList.append(copy.deepcopy(inter))
						
					if len(inter0) > 0 and inter0 not in setList:
						if len(i.tileList) == 0:
							tempTemp = tilegrouping.TileGrouping(list(inter0),0,0,0,copy.deepcopy(i2.parentGrouping), 'intersect 0')
						else:
							tempTemp = tilegrouping.TileGrouping(list(inter0),0,0,0,[copy.deepcopy(i2)], 'intersect 0')
						#print inter0,tempTemp.isComplete()
						self.tileGroupings.append(copy.deepcopy(tempTemp))
						setList.append(copy.deepcopy(inter0))
						
					if len(i.tileList) == 0:
						self.tileGroupings.pop(ii)
						iC -= 1
					else:
						ii += 1
			
			for tr in range(2):						
				for i in self.tileGroupings:				

					tempP = (0.5*(i.maxBombs+i.minBombs))/(len(i.tileList))
					tempC = i.isComplete()
						
					
					
					
					if i.maxBombs == i.numBombs and i.numBombs == i.minBombs:
						tempKnown = True
					else:
						tempKnown = False
					
					for j in i.tileList:
						
						if not(self.tiles[j[0]][j[1]].percentageComplete) and (i.isComplete() or (not(self.tiles[j[0]][j[1]].percentageComplete) and (self.tiles[j[0]][j[1]].percentage < int(100*tempP)))):
							temp_per = 1.0 - (self.tiles[j[0]][j[1]].percentage/100.0)
							if tempP != 0 and tempP != 1.0 and 1 == 2:
								temp_per *= (1-tempP)
							else:
								temp_per = tempP
							self.tiles[j[0]][j[1]].percentage = temp_per * 100
							self.tiles[j[0]][j[1]].percentageKnown = tempKnown
							self.tiles[j[0]][j[1]].percentageComplete = tempC

			tGC = len(self.tileGroupings)
			ii = 0
			# remove 100% and 0% from groupings?
			while(ii < tGC):
				j = 0
				i = self.tileGroupings[ii]
				i2 = copy.deepcopy(i)
				
				while(j < len(i.tileList) and len(i.tileList) > 1):
					
					if self.tiles[i.tileList[j][0]][i.tileList[j][1]].percentageComplete and not(i.isComplete()):
						#for x in i.tileList: #print x,self.tiles[x[0]][x[1]].percentage,self.tiles[x[0]][x[1]].percentageComplete
						#print ''
						if int(self.tiles[i.tileList[j][0]][i.tileList[j][1]].percentage) == 100:
							#print '0    ',i.tileSet,i.numBombs,i.maxBombs,i.minBombs
							tempTempGroup = tilegrouping.TileGrouping([i.tileList[j]],1,1,1,[copy.deepcopy(i2)], 'remove 100 child')
							self.tileGroupings.append(copy.deepcopy(tempTempGroup))
							i.parentGrouping = [copy.deepcopy(i2)]
							i.sourceType = 'remove 100'
							i.tileSet -= set([i.tileList[j]])
							i.tileList = list(i.tileSet)
							i.numBombs -= 1
							i.maxBombs -= 1
							i.minBombs -= 1
							i.complete = i.isComplete()
							
							#self.tiles[i.tileList[j][0]][i.tileList[j][1]].percentageComplete = i.isComplete()
							#print '1    ',i.tileSet,i.numBombs,i.maxBombs,i.minBombs
							ii -= 1
							break
						elif int(self.tiles[i.tileList[j][0]][i.tileList[j][1]].percentage) == 0:
							#print '0    ',i.tileSet,i.numBombs,i.maxBombs,i.minBombs
							tempTempGroup = tilegrouping.TileGrouping([i.tileList[j]],0,0,0,[copy.deepcopy(i2)], 'remove 0 child')
							
							self.tileGroupings.append(copy.deepcopy(tempTempGroup))
							i.parentGrouping = [copy.deepcopy(i2)]
							i.sourceType = 'remove 0'
							i.tileSet -= set([i.tileList[j]])
							i.tileList = list(i.tileSet)
							i.complete = i.isComplete()
							
							#self.tiles[i.tileList[j][0]][i.tileList[j][1]].percentageComplete = i.isComplete()
							#print '2    ',i.tileSet,i.numBombs,i.maxBombs,i.minBombs
							ii -= 1
							break
						else:
							j += 1
					else:
						j += 1
				ii += 1
				for jj in i.tileList:
					if not(self.tiles[jj[0]][jj[1]].percentageComplete):
						self.tiles[jj[0]][jj[1]].percentageComplete = i.isComplete()
				tGC = len(self.tileGroupings)

			for i in self.tileGroupings:
				
				
				#print i.tileList,i.maxBombs,i.minBombs,i.numBombs,i.isComplete(),i.ID
				self.printGrouping(i, 0, True)
				
				tempP = (0.5*(i.maxBombs+i.minBombs))/len(i.tileList)
				tempC = i.isComplete()

				
				
				if i.maxBombs == i.numBombs and i.numBombs == i.minBombs:
					tempKnown = True
				else:
					tempKnown = False
				for j in i.tileList:
					
					if not(self.tiles[j[0]][j[1]].percentageComplete) and tempKnown and (i.isComplete() or ( (self.tiles[j[0]][j[1]].percentage < int(100*tempP))) or (not(self.tiles[j[0]][j[1]].percentageComplete) and tempKnown)):
						self.tiles[j[0]][j[1]].percentage = int(100*tempP)
						self.tiles[j[0]][j[1]].percentageKnown = tempKnown
						self.tiles[j[0]][j[1]].percentageComplete = tempC

			for i in primaryGroupings:
				
				tempP = (0.5*(i.maxBombs+i.minBombs))/len(i.tileList)
				tempC = i.isComplete()				
				
				for j in i.tileList:
					
					if not(self.tiles[j[0]][j[1]].percentageComplete): # and not(self.tiles[j[0]][j[1]].percentageKnown):# and i.sourceType == 'gen':
						self.tiles[j[0]][j[1]].percentage = int(100*tempP)
						self.tiles[j[0]][j[1]].percentageKnown = True
						self.tiles[j[0]][j[1]].percentageComplete = tempC
					
					
			#print 'done'
		self.tilesChangedSinceLastGrouping = False
		

	def printGrouping(self, i, depth, displayParents):
		
		#print '  '*depth,i.tileList,i.maxBombs,i.minBombs,i.numBombs,i.isComplete(),i.sourceType
		if len(i.parentGrouping) > 0 and displayParents:
			for j in i.parentGrouping:
				self.printGrouping(j, depth + 1, True)

	def reveal(self,x,y):
		self.tiles[x][y].state = 3		
		self.tilesChangedSinceLastGrouping = True
		if self.tiles[x][y].bomb:
			return False


		flags = 0
		for i in range(x-1,x+2):
			for j in range(y-1,y+2):
				if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and self.tiles[i][j].state == 1:
					flags += 1


		if self.tiles[x][y].value - flags == 0:
			for i in range(x-1,x+2):
				for j in range(y-1,y+2):
					if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and (self.tiles[i][j].state == 0 or self.tiles[i][j].state == 2):
						self.reveal(i,j)
		return True

	def revealAll(self):
		for x in range(self.width):
			for y in range(self.height):
				flags = 0
				if self.tiles[x][y].state == 3:
					for i in range(x-1,x+2):
						for j in range(y-1,y+2):
							if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and self.tiles[i][j].state == 1:
								flags += 1


					if self.tiles[x][y].value - flags == 0:
						for i in range(x-1,x+2):
							for j in range(y-1,y+2):
								if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != x or j != y) and (self.tiles[i][j].state == 0 or self.tiles[i][j].state == 2):
									self.reveal(i,j)
		return True

	
	def generate(self, x, y):
		#self.tiles[x][y].state = 3
		self.tilesChangedSinceLastGrouping = True
		temp = 0
		for i in range(x-1,x+2):
			for j in range(y-1,y+2):
				if i >= 0 and i < self.width and j >= 0 and j < self.height:
					self.tiles[i][j].state = 3
					temp += 1

		rem_b = self.numBombs
		rem_t = self.width * self.height - temp
		w = 0
		h = 0
		while w < self.width and rem_b > 0:
			h = 0
			while h < self.height and rem_b > 0:
				rr = random.randrange(rem_t)
				if rem_b == rem_t:
					rr = rem_b - 1
				if rem_b > rr and self.tiles[w][h].state == 0:
					rem_b -= 1
					self.tiles[w][h].bomb = True
					for i in range(w-1,w+2):
						for j in range(h-1,h+2):
							if i >= 0 and i < self.width and j >= 0 and j < self.height and (i != w or j != h) and self.tiles[i][j].bomb == False:
								self.tiles[i][j].value += 1								
				rem_t -= 1
				h += 1
			w += 1
		for i in range(len(self.tiles)):
			for j in range(len(self.tiles[i])):
				if self.tiles[i][j].state == 3:
					self.reveal(i,j)
