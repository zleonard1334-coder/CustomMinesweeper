class Button(object):
	relative_x = 0
	relative_y = 0
	layer = 0
	x = 0
	y = 0
	name = ""
	width = 0
	height = 0
	orig_height = 0
	orig_width = 0
	action_name = ""
	parent = 0
	cir = False

	def __init__(self,layer,relative_x,relative_y,width,height,name,action_name,cir = False,parent = 0):
		self.relative_x = relative_x
		self.relative_y = relative_y
		self.orig_relative_x = relative_x
		self.orig_relative_y = relative_y
		self.width = width
		self.height = height
		self.orig_width = width
		self.orig_height = height
		self.name = name
		self.layer = layer
		self.action_name = action_name
		self.cir = cir
		self.parent = parent
		self.updateCoords()

	def updateCoords(self):
		if self.parent != 0:
			self.x = self.parent.x + self.relative_x
			self.y = self.parent.y + self.relative_y
		else:
			self.x = self.relative_x
			self.y = self.relative_y
