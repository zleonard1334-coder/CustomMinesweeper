import pygame
import button

class FakeGui(object):
	dialogs = {}
	



class Dialog(object):
	layer = 0
	x = 0
	y = 0
	width = 0
	height = 0

	def __init__(self,x,y,width,height,layer):
		self.layer = layer
		self.x = x
		self.y = y
		self.width = width
		self.height = height
