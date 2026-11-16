# -*- coding: utf-8 -*-
import pygame
import math
import maps
import difficulty
import time
import copy
import button
import os.path

class FakeGui(object):
        dialogs = {}
        menubar = 0
        max_menu_width = 0
        orig_max_menu_width = 0

        def __init__(self,dialogs,menubar,menu_font,mmw):
                self.dialogs = dialogs
                self.menubar = menubar
                self.menu_font = menu_font
                self.max_menu_width = mmw
                self.orig_max_menu_width = mmw

class Dialog(object):
        layer = 0
        x = 0
        y = 0
        title = ""
        width = 0
        orig_width = 0
        height = 0
        orig_height = 0
        buttons = []
        visible = False

        def __init__(self,x,y,width,height,layer,buttons,visible,title,title_height,scale = 1.0):
                self.layer = layer
                self.x = x
                self.y = y
                self.width = width
                self.orig_width = width
                self.orig_height = height
                self.height = height
                self.buttons = buttons
                self.visible = visible
                self.scale = scale
                self.title = title
                self.title_height = title_height
                self.orig_title_height = title_height
                self.buttons.append(button.Button(self.layer+2,int(self.width - 22),3,int(18*scale),int(18*scale),"X","close_dialog",False,self))
                self.textboxes = []
                self.setTitleFont()

        def updateHeight(self):
                self.height = int(self.orig_height * self.scale)
                for i in self.buttons:
                        if i.relative_y + i.height > self.height:
                                self.height = i.relative_y + i.height + 5

                for i in self.textboxes:
                        if i.relative_y + i.height > self.height:
                                self.height = i.relative_y + i.height + 5

        def updatePosition(self,dx,dy):
                self.x += dx
                self.y += dy

                self.gui.menubar.updateCoords()

                for i in self.textboxes:
                        i.updateCoords()

                for i in self.buttons:
                        i.updateCoords()

        def setTitleFont(self):
                self.title_font = pygame.font.SysFont("tahoma", self.title_height-4)

class MenuBar(object):
        depth = 0
        items = []
        layer = 0
        relative_x = 0
        relative_y = 0
        x = 0
        y = 0
                
        width = 0
        orig_width = 0
        parent = 0

        def __init__(self,depth,relative_x,relative_y,items,width,layer,parent = 0):
                self.layer = layer
                self.depth = depth
                self.relative_x = relative_x
                self.relative_y = relative_y

                self.orig_relative_x = relative_x
                self.orig_relative_y = relative_y
                self.items = items
                self.width = width
                self.orig_width = width
                self.parent = parent

        def updateCoords(self):
                if self.parent != 0:
                        self.x = self.parent.x + self.relative_x
                        self.y = self.parent.y + self.relative_y
                else:
                        self.x = self.relative_x
                        self.y = self.relative_y

                for i in self.items:
                        i.updateCoords()

        def close(self):
                for i in self.items:
                        i.close()

        def expandUp(self):
                return True
        
        def closeUp(self):
                self.close()

        def closeExpanded(self):
                for i in self.items:
                        i.closeExpanded()

        def closeExpandedUp(self):
                self.closeExpanded()

        def isParent(self,menu):
                return False

class Menu(MenuBar):
        depth = 0
        text = ""
        help_text = ""
        expandable = False
        shortcut = ""
        selected = False
        layer = 0
        items = []
        parent = 0
        expanded = False
        hovered = False
        shortcut_cooldown = 0
        last_shortcut = 0
        temp_expanded = False
        
        def __init__(self,depth,text,help_text,items,shortcut,relative_x,relative_y,width,expanded,expandable,layer,parent = 0):
                MenuBar.__init__(self,depth,relative_x,relative_y,items,width,layer,parent = 0)
                self.text = text
                self.help_text = help_text
                self.shortcut = shortcut
                self.expanded = expanded
                self.expandable = expandable
                self.hovered = False
                self.shortcut_cooldown = 0.25
                self.layer = layer
                self.last_shortcut = 0
                self.parent = parent
                self.temp_expanded = False

        def updateCoords(self):
                if self.parent != 0:
                        self.x = self.parent.x + self.relative_x
                        self.y = self.parent.y + self.relative_y
                else:
                        self.x = self.relative_x
                        self.y = self.relative_y

                for i in self.items:
                        i.updateCoords()

        def close(self):
                self.expanded = False
                self.temp_expanded = False
                for i in self.items:
                        i.close()

        def expandUp(self):
                self.expanded = True
                if self.parent != 0:
                        self.parent.expandUp()

        def closeUp(self):
                self.close()
                if self.parent != 0:
                        self.parent.closeUp()

        def closeExpandedUp(self):
                self.closeExpanded()
                if self.parent != 0:
                        self.parent.closeExpandedUp()

        def closeExpanded(self):
                if self.temp_expanded == False:
                        self.expanded = False
                for i in self.items:
                        i.closeExpanded()

        def isParent(self,menu):
                if self.parent == menu:
                        return True
                elif self.parent != 0:
                        return self.parent.isParent(menu)
                else:
                        return False

class MenuItem(Menu):
        action_name = ""

        def __init__(self,depth,text,help_text,items,shortcut,x,y,width,expanded,expandable,layer,action_name,parent = 0):
                Menu.__init__(self,depth,text,help_text,items,shortcut,x,y,width,expanded,expandable,layer,parent = 0)
                self.action_name = action_name
                self.expandable = False

        def updateCoords(self):
                if self.parent != 0:
                        self.x = self.parent.x + self.relative_x
                        self.y = self.parent.y + self.relative_y
                else:
                        self.x = self.relative_x
                        self.y = self.relative_y

        def close(self):
                self.expanded = False
                self.temp_expanded = False

        def expandUp(self):
                self.expanded = True
                if self.parent != 0:
                        self.parent.expandUp()

        def closeUp(self):
                self.close()
                if self.parent != 0:
                        self.parent.closeUp()

        def closeExpanded(self):
                if self.temp_expanded == False:
                        self.expanded = False

        def closeExpandedUp(self):
                self.closeExpanded()
                if self.parent != 0:
                        self.parent.closeExpandedUp()

        def isParent(self,menu):
                if self.parent == menu:
                        return True
                elif self.parent != 0:
                        return self.parent.isParent(menu)
                else:
                        return False

class TextBox(object):
        name = ""
        x = 0
        y = 0
        relative_x = 0
        relative_y = 0
        text = ""
        layer = 0
        max_width = 0
        height = 0
        text_colour = (0,0,0)
        parent = 0
        
        def __init__(self,layer,name,relative_x,relative_y,text,font,max_width,text_colour = (0,0,0),parent = 0):
                self.name = name
                self.layer = layer
                self.relative_x = relative_x
                self.relative_y = relative_y
                self.orig_relative_x = relative_x
                self.orig_relative_y = relative_y
                self.text = text
                self.font = font
                self.orig_max_width = max_width
                self.max_width = max_width
                self.text_colour = text_colour
                self.parent = parent
                self.height = 0
                self.text_strings = []
                self.formatText()

        def formatText(self):
                self.text_strings = []
                lw = self.font.size('.')[0]
                t = self.text
                s = ""
                for i in t.split(' '):
                        if len(i) > 0:
                                if i.count(',.') > 0:
                                        temp_i = i
                                        nums = temp_i.count(',.')
                                        while nums >= 0:
                                                if nums == 0:
                                                        s = temp_i
                                                        nums -= 1
                                                elif len(s) > 0:
                                                        s += " " + str(temp_i[:temp_i.index(',.')])
                                                        temp_i = temp_i[temp_i.index(',.')+2:]
                                                        nums -= 1
                                                else:
                                                        s = str(temp_i[:temp_i.index(',.')])
                                                        temp_i = temp_i[temp_i.index(',.')+2:]
                                                        nums -= 1
                                                self.text_strings.append(s)

                                                s = ""
                                elif self.font.size(s+" "+str(i))[0] > self.max_width:
                                        self.text_strings.append(s)
                                        s = ""
                                        if self.font.size(str(i))[0] < self.max_width:
                                                s = i
                                        else:
                                                for j in str(i):
                                                        if self.font.size(s+str(j)+"-")[0] < self.max_width:
                                                                s += str(j)
                                                        else:
                                                                s += "-"
                                                                self.text_strings.append(s)
                
                                                                s = ""
                                elif i[len(i)-1] == ".":
                                        if len(s) > 0:
                                                s += " " + str(i)
                                        else:
                                                s = str(i)
                                        self.text_strings.append(s)

                                        s = ""
                                        self.text_strings.append("")

                                
                                        #self.text_strings.append("")
                                        #print self.text_strings

                                else:
                                        if len(s) > 0:
                                                s += " " + str(i)
                                        else:
                                                s = str(i)
                
                self.text_strings.append(s)                                     
                        
                self.height = len(self.text_strings)*(self.font.size('A')[1] + 3)
                if (type(self.parent) is Dialog):
                        self.parent.updateHeight()

        def updateCoords(self):
                if self.parent != 0:
                        self.x = self.parent.x + self.relative_x
                        self.y = self.parent.y + self.relative_y
                else:
                        self.x = self.relative_x
                        self.y = self.relative_y

class App(object):
        def __init__(self):
                pygame.init()
                self.clock = pygame.time.Clock()

                self.difs = []

                self.window_width = 0
                self.window_height = 0

                self.counts = 3

                self.has_gui = False

                self.loadDifficultySettings()

                #self.difs.append(difficulty.Difficulty(10,10,10,"Easy"))
                #self.difs.append(difficulty.Difficulty(16,16,40,"Intermediate"))
                #self.difs.append(difficulty.Difficulty(40,16,99,"Hard"))
                #self.difs.append(difficulty.Difficulty(40,24,192,"Extreme"))

                self.score_updated = True

                self.colour = {}

                self.cheater = False

                self.settingsSplit = ['|','~',';']
                
                self.num_layers = 500

                self.moving_dialog = False
                self.cur_moving_x = 0
                self.cur_moving_y = 0

                self.menu_gen = False

                self.m_tile_x = -1
                self.m_tile_y = -1

                self.lastGroupTileLocation = (-1,-1)

                self.displayed_groups = []

                self.groupDisplayLength = 3 # Number of seconds to display a group for.

                self.colour["background"] = (182,182,182)
                self.colour["divider"] = (33,33,33)
                self.colour["tile"] = (192,192,192)
                self.colour["menu"] = (229,229,229)
                self.colour["revealed"] = (170,170,170)
                self.colour["border_top"] = (230,230,230)
                self.colour["border_left"] = (215,215,215)
                self.colour["border_right"] = (150,150,150)
                self.colour["border_down"] = (110,110,110)
                self.colour["menu_selected"] = (177,192,204)
                self.colour["menu_border"] = (0,0,0)
                self.colour["dead"] = (180,1,1)
                self.colour["score_default"] = (0,0,0)
                self.colour["score_top"] = (0,100,0)
                self.colour["group_outline"] = (255,0,0)
                self.colour["score_this"] = (0,0,100)
                self.colour["dialog_title_bar"] = self.colour["menu"]

                self.keys = [pygame.K_z,pygame.K_x,pygame.K_c,pygame.K_v,pygame.K_b,pygame.K_n,pygame.K_m,
                      pygame.K_a,pygame.K_s,pygame.K_d,pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_j,
                      pygame.K_k,pygame.K_l,pygame.K_q,pygame.K_w,pygame.K_e,pygame.K_r,pygame.K_t,
                      pygame.K_y,pygame.K_u,pygame.K_i,pygame.K_o,pygame.K_p]

                self.key_map = {}
                self.key_map["a"] = pygame.K_a
                self.key_map["b"] = pygame.K_b
                self.key_map["c"] = pygame.K_c
                self.key_map["d"] = pygame.K_d
                self.key_map["e"] = pygame.K_e
                self.key_map["f"] = pygame.K_f
                self.key_map["g"] = pygame.K_g
                self.key_map["h"] = pygame.K_h
                self.key_map["i"] = pygame.K_i
                self.key_map["j"] = pygame.K_j
                self.key_map["k"] = pygame.K_k
                self.key_map["l"] = pygame.K_l
                self.key_map["m"] = pygame.K_m
                self.key_map["n"] = pygame.K_n
                self.key_map["o"] = pygame.K_o
                self.key_map["p"] = pygame.K_p
                self.key_map["q"] = pygame.K_q
                self.key_map["r"] = pygame.K_r
                self.key_map["s"] = pygame.K_s
                self.key_map["t"] = pygame.K_t
                self.key_map["u"] = pygame.K_u
                self.key_map["v"] = pygame.K_v
                self.key_map["w"] = pygame.K_w
                self.key_map["x"] = pygame.K_x
                self.key_map["y"] = pygame.K_y
                self.key_map["z"] = pygame.K_z
                self.key_map["lCtrl"] = pygame.K_LCTRL

                self.number_colours = [(255,255,255),(1,0,254),(1,127,1),(254,0,0),(1,0,128),(129,1,2),(0,128,129),(0,0,0),(128,128,128)]

                self.settings = {}

                self.buttons = []

                self.pressed = []               

                self.setSetting("current_difficulty",2)

                #### To be options in a menu later?

                self.updateScaling(1.0,False)           

                self.dialog_fade = 120

                ####

                self.fps = 60

                self.reveal = False

                self.percentage = False

                self.subtract = False

        def updateScaling(self,scale,update = True):

                if update:
                        self.setSetting("app_scaling",scale)
                
                self.tile_size = int(30 * scale)

                self.top_height = int(self.tile_size*4/3.0)

                self.menu_height = int(self.tile_size*2/3.0)

                self.border = int(self.tile_size / 6.0)

                self.tile_shade = max(1,int(self.tile_size / 10))

                self.divider_width = max(int(self.tile_size / 20),1)

                self.font = pygame.font.SysFont("tahoma", int((self.tile_size * 2) / 3.0))

                self.fontP = pygame.font.SysFont("tahoma", int((self.tile_size * 1) / 3.5))

                self.fontPC = pygame.font.SysFont("tahoma", int((self.tile_size * 1) / 4.5))

                self.fontN = pygame.font.SysFont("tahoma", 1)

                self.font2 = pygame.font.SysFont("tahoma", self.tile_size)

                self.font3 = self.font

                self.menu_font = pygame.font.SysFont("courier", self.menu_height-4)

                for b in self.buttons:
                        b.height = int(b.orig_height * scale)
                        if b.name != "Restart":
                                b.relative_x = int(b.orig_relative_x * scale)
                        else:
                                b.orig_relative_x = int((2 * self.border + self.game_map_width)/(2))
                                b.relative_x = int((2 * self.border + self.game_map_width)/(2))
                        b.relative_y = int(b.orig_relative_y * scale)
                        b.width = int(b.orig_width * scale)
                        b.updateCoords()                                

                if self.has_gui:
                        self.updateDialogScaling(self)
                        self.updateGUIScaling(self)
                        self.updateMenuScaling(self.gui.menubar)
                        self.updateDisplaySize()

                
        def updateGUIScaling(self,obj):
                s = self.getSetting("app_scaling",1.0)
                obj.gui.max_menu_width = int(obj.gui.orig_max_menu_width * s)
                obj.gui.menu_font = self.menu_font

        def updateDialogScaling(self,obj):              
                s = self.getSetting("app_scaling",1.0)
                self.updateGUIScaling(self)
                for d2 in obj.gui.dialogs.keys():
                        d = obj.gui.dialogs[d2]
                        d.height = int(d.orig_height * s)
                        d.width = int(d.orig_width * s)
                        d.title_height = int(d.orig_title_height * s)
                        d.setTitleFont()
                        self.updateMenuScaling(d.gui.menubar)                   
                        if len(d.gui.dialogs.keys()) > 0:
                                self.updateDialogScaling(d)
                        for b in d.buttons:
                                b.height = int(b.orig_height * s)
                                b.relative_x = int(b.orig_relative_x * s)
                                b.relative_y = int(b.orig_relative_y * s)
                                b.width = int(b.orig_width * s)
                                b.updateCoords()
                        for t in d.textboxes:
                                t.max_width = int(t.orig_max_width * s)
                                t.relative_x = int(t.orig_relative_x * s)
                                t.relative_y = int(t.orig_relative_y * s)
                                t.formatText()
                        d.updatePosition(0,0)
                        

        def updateMenuScaling(self,obj):
                s = self.getSetting("app_scaling",1.0)

                obj.relative_x = int(obj.orig_relative_x * s)
                obj.relative_y = int(obj.orig_relative_y * s)

                obj.width = int(obj.orig_width * s)
                for m in obj.items:
                        self.updateMenuScaling(m)
                obj.updateCoords()

        def create_map(self,d):
                #print d.width,d.height,d.bombs
                return maps.Maps(d.width,d.height,d.bombs)


        def display_groups(self):               
                # TODO: Display the current groups for the currently hovered tile.
                nothing = 1
                # Outline hovered group in red lines.
                # Display number of bombs and numeber of tiles at the top of the map.
                x = self.m_tile_x
                y = self.m_tile_y

                if self.lastGroupTileLocation != (x, y):
                        self.lastGroupTileLocation = (x, y)
                        self.displayed_groups = []
                        for i in self.main_map.tileGroupings:
                                if (x,y) in i.tileList:
                                        self.tryAddGroup(i)
                                        for k in i.parentGrouping:
                                                
                                                if (x,y) in k.tileList:
                                                        self.tryAddGroup(k)
                                                
                if len(self.displayed_groups) > 0:
                        groupToDisplayIndex = int(round((self.tp + self.tc - self.t1)/self.groupDisplayLength,0)) % len(self.displayed_groups)

                        self.display_group(groupToDisplayIndex)

        def tryAddGroup(self, g):
                shouldAdd = True
                                                        
                for l in self.displayed_groups:
                        if l.tileSet == g.tileSet:
                                shouldAdd = False
                                break

                        
                if shouldAdd:
                        self.displayed_groups.append(g) 

        def display_group(self, index):

                #print len(self.displayed_groups), index

                for i in self.displayed_groups[index].tileList:
                        x = i[0]
                        y = i[1]
                        # TOP
                        if ((x,y-1) not in self.displayed_groups[index].tileList):
                                pygame.draw.line(self.gameDisplay,self.colour["group_outline"],(self.border  + self.tile_size * x, self.menu_height + self.border  + self.top_height + self.tile_size * y),
                                                 (self.border  + self.tile_size * (x+1),self.menu_height + self.border  + self.top_height + self.tile_size * y),self.tile_shade)
                        # LEFT
                        if ((x-1,y) not in self.displayed_groups[index].tileList):
                                pygame.draw.line(self.gameDisplay,self.colour["group_outline"],(self.border + self.tile_size * x,self.menu_height + self.border  + self.top_height + self.tile_size * y),
                                                 (self.border + self.tile_size * x,self.menu_height + self.border  + self.top_height + self.tile_size * (1+y)),self.tile_shade)
                        # RIGHT
                        if ((x+1,y) not in self.displayed_groups[index].tileList):
                                pygame.draw.line(self.gameDisplay,self.colour["group_outline"],(self.border  + self.tile_size * (1+x),self.menu_height + self.border  + self.top_height + self.tile_size * y),
                                                 (self.border  + self.tile_size * (1+x),self.menu_height + self.border  + self.top_height + self.tile_size * (1+y)),self.tile_shade)
                        # BOTTOM
                        if ((x,y+1) not in self.displayed_groups[index].tileList):
                                pygame.draw.line(self.gameDisplay,self.colour["group_outline"],(self.border  + self.tile_size * x,self.menu_height + self.border + self.top_height + self.tile_size * (y+1)),
                                                 (self.border + self.tile_size * (x+1),self.menu_height + self.border + self.top_height + self.tile_size * (1+y)),self.tile_shade)


                if self.displayed_groups[index].minBombs >= 0 and self.displayed_groups[index].maxBombs >= 0:
                        if self.displayed_groups[index].numBombs >= 0:
                                n = self.font2.render(str(self.displayed_groups[index].numBombs) + ' / ' + str(len(self.displayed_groups[index].tileList)),True,(0,100,0))
                        else:
                                n = self.font2.render(str(self.displayed_groups[index].minBombs)+'-'+str(self.displayed_groups[index].maxBombs) + ' / ' + str(len(self.displayed_groups[index].tileList)),True,(230,0,0))
                else:
                        n = self.font2.render('? / ' + str(len(self.displayed_groups[index].tileList)),True,(155,55,0))
                self.gameDisplay.blit(n,(int(6.0*self.game_map_width/8.0),self.menu_height ))

                n2 = self.font2.render(str(index + 1)+' / ' + str(len(self.displayed_groups)),True,(0,0,0))

                self.gameDisplay.blit(n2,(int(5.0*self.game_map_width/8.0),self.menu_height ))  
                        
                
                

        def display_map(self):
                #global reveal
                self.gameDisplay.fill(self.colour["background"])
                pygame.draw.line(self.gameDisplay,self.colour["divider"],(self.border,self.menu_height+self.top_height+self.border),(self.game_map_width+self.border,self.menu_height+self.top_height+self.border),self.divider_width)
                pygame.draw.line(self.gameDisplay,self.colour["divider"],(self.border,self.menu_height+self.top_height+self.border),(self.border,self.game_map_height+self.border),self.divider_width)
                r = 1
                # divider lines
                for row in self.main_map.tiles[0]:
                        pygame.draw.line(self.gameDisplay,self.colour["divider"],(self.border,self.menu_height+self.top_height + r * self.tile_size + self.border),
                                         (self.game_map_width+self.border,self.menu_height+self.top_height + r*self.tile_size + self.border),self.divider_width)
                        r += 1
                r = 1
                for row in self.main_map.tiles:
                        
                        pygame.draw.line(self.gameDisplay,self.colour["divider"],(self.border  + r * self.tile_size,self.menu_height+self.top_height + self.border),
                                         (self.border  + r * self.tile_size,self.game_map_height+ self.border),self.divider_width)
                        c = 1
                        for t in row:                   
                                self.display_tile(t,r-1,c-1)                    
                                c += 1
                        r += 1

        def display_paused(self):
                if self.paused == True:
                        self.gameDisplay.fill(self.colour["background"])
                        s = pygame.Surface((self.main_map.width, self.main_map.height))
                        n = self.font.render('PAUSED',True,(0,0,0))
                                                
                        s.blit(n, (0, 0))
                        self.gameDisplay.blit(s,(0,0))          

        def checkSettings(self):
                if os.path.isfile('settings.txt'):
                        self.loadSettings()
                else:
                        self.saveSettings(0)

        def loadDifficultySettings(self):
                f= open('difficulties.txt','r+')
                diffs = f.read()                
                f.close()
                self.loadDifficultySettingsFromString(0,diffs)

        def loadDifficultySettingsFromString(self,index,difsString):
                for i in difsString.split(';'):
                        #print i
                        dfs = i.split(',')
                        tempDif = difficulty.Difficulty(int(dfs[1]),int(dfs[2]),int(dfs[3]),dfs[0],dfs[5],dfs[4],int(dfs[6]))
                        self.difs.append(copy.deepcopy(tempDif))
                sorted(self.difs, key=lambda x: x.index)

        def loadSettings(self):
                f= open('settings.txt','r+')
                setting = f.read()              
                f.close()
                self.loadSettingsFromString(0,setting)

        def loadSettingsFromString(self,index,settingsString):
                dfs = []
                delim = self.settingsSplit[index]
                next_delim = self.settingsSplit[index+1]

                if len(settingsString)>0:
                        for i in settingsString.split(delim):
                                if i.count(next_delim) > 0:
                                        self.loadSettingsFromString(index+1,i)
                                elif i.count(':') > 0:
                                        temp_set = i.split(':')
                                        if temp_set[1].count(',') > 0 or temp_set[0].count('list') > 0:
                                                temp_list = []
                                                for t in temp_set[1].split(','):
                                                        if len(t)>0 and temp_set[0].count('score') > 0:
                                                                temp_list.append(float(t))
                                                        elif len(t)>0 :
                                                                temp_list.append(t)
                                                self.settings[temp_set[0]] = temp_list
                                        else:
                                                self.settings[temp_set[0]] = temp_set[1]
                                else:
                                        print ('Error reading settings: '+ i)


        def saveSettings(self,index):
                f= open('settings.txt','w')
                temp_set = ""
                for i in self.settings.keys():
                        temp_set += i+':'
                        if type(self.settings[i]) is list or i.count('_list') > 0:
                                temp_list = ""
                                for j in self.settings[i]:
                                        temp_list += str(j)+','
                                temp_list = temp_list[:len(temp_list)-1]

                                temp_set += temp_list
                        else:
                                temp_set += str(self.settings[i])
                        temp_set += str(self.settingsSplit[index])
                temp_set = temp_set[:len(temp_set)-1]
                f.write(temp_set)
                f.close()
                
        def display_tile(self,t,x,y):

                displayPercentageCoords = True
                
                if self.subtract:
                        temp_val = max(t.value - self.main_map.numFlags(x,y),0)
                else:
                        temp_val = t.value
                
                if t.state < 3:
                        pygame.draw.line(self.gameDisplay,self.colour["border_top"],(self.border + self.tile_shade + self.tile_size * x, self.menu_height + self.border + self.tile_shade + self.top_height + self.tile_size * y),
                                         (self.border - self.tile_shade + self.tile_size * (x+1),self.menu_height + self.border + self.tile_shade + self.top_height + self.tile_size * y),self.tile_shade)
                        pygame.draw.line(self.gameDisplay,self.colour["border_left"],(self.border + self.tile_shade + self.tile_size * x,self.menu_height + self.border + self.tile_shade + self.top_height + self.tile_size * y),
                                         (self.border + self.tile_shade + self.tile_size * x,self.menu_height + self.border - self.tile_shade + self.top_height + self.tile_size * (1+y)),self.tile_shade)
                        pygame.draw.line(self.gameDisplay,self.colour["border_right"],(self.border - self.tile_shade + self.tile_size * (1+x),self.menu_height + self.border + self.tile_shade + self.top_height + self.tile_size * y),
                                         (self.border - self.tile_shade + self.tile_size * (1+x),self.menu_height + self.border - self.tile_shade + self.top_height + self.tile_size * (1+y)),self.tile_shade)
                        pygame.draw.line(self.gameDisplay,self.colour["border_down"],(self.border + self.tile_shade + self.tile_size * x,self.menu_height + self.border - self.tile_shade + self.top_height + self.tile_size * (y+1)),
                                         (self.border - self.tile_shade + self.tile_size * (x+1),self.menu_height + self.border - self.tile_shade + self.top_height + self.tile_size * (1+y)),self.tile_shade)
                        
                if (t.state > 0 or self.reveal or self.percentage) and self.gen:
                        s = pygame.Surface((self.tile_size - 2 * self.tile_shade, self.tile_size - 2 * self.tile_shade))
                        n2 = self.fontN.render('',True,(0,0,0))
                        if t.state == 3:
                                s.fill(self.colour["revealed"])
                        elif t.state < 3:
                                s.fill(self.colour["tile"])
                        if temp_val > 0 or (t.bomb) or (self.percentage and (t.state == 0 or t.state == 2)):
                                if t.bomb and (self.reveal or t.state == 3):
                                        s.fill(self.colour["dead"])
                                        n = self.font.render('*',True,(0,0,0))
                                        self.running = self.reveal
                                        self.lose = not(self.reveal)
                                elif t.state == 3 or t.state == 0:
                                        if self.percentage and t.state == 0:
                                                if t.percentageKnown and t.percentage == 100:
                                                        tempC = (255,0,0)
                                                elif t.percentageKnown and t.percentage == 0:
                                                        tempC = (0,100,0)
                                                elif t.percentageKnown:
                                                        tempC = (155,55,0)
                                                else:
                                                        tempC = (0,0,0)
                                                n = self.fontP.render(str(int(t.percentage))+'%',True,tempC)
                                                if (displayPercentageCoords):
                                                        n2 = self.fontPC.render('('+str(x)+','+str(y)+')',True,(0,0,0))
                                        else:
                                                n = self.font.render(str(temp_val),True,self.number_colours[temp_val])
                                elif t.state == 1:
                                        n = self.font.render('^',True,(220,0,0))
                                        
                                elif t.state == 2:
                                        if self.percentage:
                                                if t.percentageKnown and t.percentage == 100:
                                                        tempC = (255,0,0)
                                                elif t.percentageKnown:
                                                        tempC = (155,55,0)
                                                else:
                                                        tempC = (0,0,0)
                                                n = self.fontP.render(str(int(t.percentage))+'%',True,tempC)
                                                if (displayPercentageCoords):
                                                        n2 = self.fontPC.render('('+str(x)+','+str(y)+')',True,(0,0,0))

                                        else:
                                                n = self.font.render('?',True,(100,0,150))
                                if self.percentage and (t.state == 2 or t.state == 0) and not ((t.bomb) and self.reveal):
                                        s.blit(n, ((self.tile_size - 2 * self.tile_shade)/4 - len(str(int(t.percentage))), self.tile_size / 5.0))
                                        if (displayPercentageCoords and (t.state == 0 or t.state == 2 or t.state == 3)) and not ((t.bomb) and self.reveal):
                                                s.blit(n2, ((self.tile_size - 2 * self.tile_shade)/4.0 - (len('('+str(x)+','+str(y)+')')*0.75), (2.75*self.tile_size) / 5.0))
                                else:
                                        s.blit(n, ((self.tile_size - 2 * self.tile_shade)/4, 0))
                        self.gameDisplay.blit(s,(self.border+ self.tile_size * x + self.tile_shade,self.menu_height + self.top_height + self.border + self.tile_size * y + self.tile_shade))

        def getRestartColour(self):
                if self.running:
                        return (230,230,0)
                elif self.win:
                        return (0,230,0)
                else:
                        return (230,0,0)

        def display_score(self):

                
                
                s = pygame.Surface((self.game_map_width  + 2 * self.border, self.top_height))
                s.fill(self.colour["background"])
                n = self.font2.render(str(self.flags_left),True,(230,0,0))
                n2 = self.font2.render(str(round(self.tp + self.tc - self.t1,1)),True,(230,0,0))
                n3 = self.font.render(str(self.counts),True,(230,0,0))
                s.blit(n,(self.border,4))
                s.blit(n2,(int(7.0*self.game_map_width/8.0)-(len(str(round(self.tp + self.tc - self.t1,1)))-3)*15,4))
                #s.blit(n3,(int(1.9*self.game_map_width/8.0)-(len(str(self.counts))-3)*15,4))

                self.gameDisplay.blit(s,(0,self.menu_height))

                if self.percentage and self.running and not(self.paused) and self.gen:
                        self.display_groups()


        def display_buttons(self,b,layer):
                for i in b:
                        if layer == -1 or i.layer == layer:
                                if i.name == "Restart":
                                        pygame.draw.circle(self.gameDisplay,self.getRestartColour(),(i.x,i.y),int(i.height / 2),0)
                                        #pygame.draw.circle(self.gameDisplay,(0,0,0),(i.x,i.y),int(i.height / 2)+1,1)
                                else:
                                        temp_r = pygame.Rect(i.x,i.y,i.width,i.height)
                                        temp_s = pygame.Surface((i.width,i.height))
                                        temp_s.fill(self.colour["tile"])
                                        temp_f = pygame.font.SysFont("tahoma", int(i.height/2.0 ))
                                        temp_n = temp_f.render(i.name, True, (0,0,0))
                                        temp_s.blit(temp_n,(int((i.width -  temp_f.size(i.name)[0])/2.0),self.tile_shade+1))
                                        self.gameDisplay.blit(temp_s,(i.x,i.y))
                                        pygame.draw.rect(self.gameDisplay,(0,0,0),temp_r,1)
                                        #border
                                        pygame.draw.line(self.gameDisplay,self.colour["border_top"],(i.x+ self.tile_shade, i.y + self.tile_shade),(i.x + i.width - self.tile_shade,i.y + self.tile_shade),self.tile_shade)
                                        pygame.draw.line(self.gameDisplay,self.colour["border_left"],(i.x+ self.tile_shade, i.y + self.tile_shade),(i.x + self.tile_shade, i.y + i.height - self.tile_shade),self.tile_shade)
                                        pygame.draw.line(self.gameDisplay,self.colour["border_right"],(i.x + i.width - self.tile_shade,i.y + self.tile_shade),(i.x + i.width - self.tile_shade, i.y + i.height - self.tile_shade),self.tile_shade)
                                        pygame.draw.line(self.gameDisplay,self.colour["border_down"],(i.x + self.tile_shade, i.y + i.height - self.tile_shade),(i.x + i.width - self.tile_shade, i.y + i.height - self.tile_shade),self.tile_shade)


        def getActiveDialogList(self,obj):
                ds = []
                for d in obj.gui.dialogs.keys():
                        if obj.gui.dialogs[d].visible:
                                ds.append(obj.gui.dialogs[d])
                        if len(obj.gui.dialogs[d].gui.dialogs.keys()) > 0:
                                ds.extend(self.getActiveDialogList(obj.gui.dialogs[d]))
                sorted(ds, key=lambda dialog: dialog.layer, reverse=True)
                ds.reverse()
                return ds               

        def display_dialog(self,obj,layer):
                # find top dialog
                ds = self.getActiveDialogList(obj)
                # check top dialog
                if len(ds) > 0:                         
                        for i in ds[1::-1]:
                                if layer == -1 or i.layer == layer:
                                        temp_d = pygame.Surface((i.width,i.height))
                                        temp_r = pygame.Rect(i.x,i.y,i.width,i.height)
                                        temp_d.fill(self.colour["background"])
                                        self.gameDisplay.blit(temp_d,(i.x,i.y))
                                        

                                        temp_t = pygame.Surface((i.width,i.title_height))
                                                                
                                        temp_t.fill(self.colour["dialog_title_bar"])

                                        temp_title = i.title_font.render(i.title,True,(0,0,0))
                                        temp_t.blit(temp_title,(5,-2))
                                        self.gameDisplay.blit(temp_t,(i.x,i.y+2))
                                        for lay in range(self.num_layers):
                                                self.display_buttons(i.buttons,lay)
                                                self.display_textboxes(i.textboxes,lay)
                                                self.displayGUI(i,i.visible,lay)
                                        pygame.draw.rect(self.gameDisplay,(0,0,0),temp_r,2)

                        if layer == -1 or ds[0].layer == layer:
                                temp_s = pygame.Surface((self.window_width,self.window_height))
                                temp_s.set_alpha(self.dialog_fade)

                                temp_d = pygame.Surface((ds[0].width,ds[0].height))
                                temp_r = pygame.Rect(ds[0].x,ds[0].y,ds[0].width,ds[0].height)
                                temp_d.fill(self.colour["background"])
                                self.gameDisplay.blit(temp_s,(0,0))
                                self.gameDisplay.blit(temp_d,(ds[0].x,ds[0].y))
                                
                                temp_t = pygame.Surface((ds[0].width,ds[0].title_height))
                                                                
                                temp_t.fill(self.colour["dialog_title_bar"])

                                temp_title = ds[0].title_font.render(ds[0].title,True,(0,0,0))
                                temp_t.blit(temp_title,(5,-2))

                                self.gameDisplay.blit(temp_t,(ds[0].x,ds[0].y+2))

                                
                                #pygame.draw.rect(self.gameDisplay,(0,0,0),temp_tr,2)
                                for lay in range(layer,self.num_layers):
                                        self.display_buttons(i.buttons,lay)
                                        self.display_textboxes(i.textboxes,lay)
                                        self.displayGUI(i,i.visible,lay)
                                pygame.draw.rect(self.gameDisplay,(0,0,0),temp_r,2)

        def display_textboxes(self,tbs,layer):
                for tb in tbs:
                        if layer == -1 or tb.layer == layer:
                                c = 0
                                for ts in tb.text_strings:
                                        texts = tb.font.render(str(ts),True,tb.text_colour)
                                        self.gameDisplay.blit(texts,(tb.x,tb.y + int(c*(tb.font.size(str(texts))[1] + 3 ))))
                                        c += 1  
                        
                        
        def checkWin(self):

                self.flags_left = self.main_map.numBombs
                
                hidden = 0
                for i in self.main_map.tiles:
                        for j in i:
                                if j.state < 3:
                                        hidden += 1
                                if j.state == 1:
                                        self.flags_left -= 1

                                if j.state == 3 and j.bomb:
                                        lose = True
                                        return False

                if hidden == self.main_map.numBombs:
                        self.win = True
                        self.running = False
                        self.score_updated = False

        def getDialog(self,obj,dialog_code):
                for i in obj.gui.dialogs.keys():
                        if i == dialog_code:
                                return obj.gui.dialogs[i]
                        elif len(obj.gui.dialogs[i].gui.dialogs.keys())>0:
                                temp = self.getDialog(obj.gui.dialogs[i],dialog_code)
                                if not(type(temp) is bool):
                                        return temp
                return False

        def action(self,caller):
                #print caller.action_name
                if caller.action_name == "test":
                        print ("test complete")
                for i in self.difs:
                        if caller.action_name == "dif_switch_"+i.name.lower() and self.getSetting("current_difficulty",2) != -1:
                                self.running = False
                                self.win = False
                                self.lose = False
                                self.playing = True
                                self.setSetting("current_difficulty",i.index)
                        elif caller.action_name == "reset_score_"+i.name.lower():
                                self.updateScore(i.name,"")
                if caller.action_name.count("help_info_dialog_") > 0:
                        d = self.getDialog(self,caller.action_name)
                        if d != False:
                                d.visible = not(d.visible)
                elif caller.action_name == "game_restart":
                        self.running = False
                        self.win = False
                        self.lose = False
                        self.playing = True
                elif caller.action_name == "add_counts":                        
                        self.counts += 1
                        #print self.counts
                elif caller.action_name == "subtract_counts" and self.counts > 1:
                        self.counts -= 1
                        #print self.counts
                elif caller.action_name == "open_help_dialog":
                        d = self.getDialog(self,"help")
                        if d != False:
                                d.visible = not(d.visible)
                elif caller.action_name == "open_controls_dialog":
                        d = self.getDialog(self,"controls")
                        if d != False:
                                d.visible = not(d.visible)
                elif caller.action_name == "open_scaling_dialog":
                        d = self.getDialog(self,"scaling")
                        if d != False:
                                d.visible = not(d.visible)
                elif caller.action_name == "close_dialog":
                        ds = self.getActiveDialogList(self)
                        ds[0].visible = False
                elif caller.action_name == "app_set_scale_70":
                        self.updateScaling(0.7)
                elif caller.action_name == "app_set_scale_85":
                        self.updateScaling(0.85)
                elif caller.action_name == "app_set_scale_100":
                        self.updateScaling(1.0)
                elif caller.action_name == "app_set_scale_115":
                        self.updateScaling(1.15)
                elif caller.action_name == "app_set_scale_130":
                        self.updateScaling(1.3)
                        
        def updateScore(self,dif2,newScore,update = True):
                dif = dif2.lower()
                cd = self.difs[0]
                for i in self.difs:
                        if i.name == dif2:
                                cd = i
                                break
                if newScore == "" or len(str(newScore))<2:
                        self.setSetting("high_score_list_"+dif+str(cd.width)+'x'+str(cd.height)+'b'+str(cd.bombs),[])
                        d = self.getDialog(self,"help_info_dialog_"+dif)
                        tb = 0
                        for i in d.textboxes:
                                if i.name == "score_"+dif:
                                        tb = i
                                        break
                        tb.text = "Best Time: Not yet completed"
                        tb.formatText()
                        #print 'rekt'
                        self.saveSettings(0)
                else:                           

                        temp = self.getSetting("high_score_list_"+dif+str(cd.width)+'x'+str(cd.height)+'b'+str(cd.bombs),[])
                        if update:
                                temp.append(float(newScore))
                        temp.sort()
                        d = self.getDialog(self,"help_info_dialog_"+dif)
                        tb = 0
                        for i in d.textboxes:
                                if i.name == "score_"+dif:
                                        tb = i
                                        break
                        
                        
                        temp_l = []                     

                        for i in range(min(len(temp),self.getSetting("scores_to_save",10))):
                                temp_l.append(float(temp[i]))
                        
                        self.setSetting("high_score_list_"+dif+str(cd.width)+'x'+str(cd.height)+'b'+str(cd.bombs),temp_l)

                        tb.text = "Best Times:"
                        for i in self.getSetting("high_score_list_"+dif+str(cd.width)+'x'+str(cd.height)+'b'+str(cd.bombs),[]):
                                if update and float(newScore) == i:
                                        tb.text += ',.' + str(i)+'**'
                                else:
                                        tb.text += ',.' + str(i)
                        tb.formatText()

                        if update and float(newScore) in self.getSetting("high_score_list_"+dif+str(cd.width)+'x'+str(cd.height)+'b'+str(cd.bombs),[]):
                                d.visible = True
                        
                        #print 'rekt'
                        self.saveSettings(0)


        def getSetting(self,settingName,default):
                if settingName in self.settings.keys():
                        if type(default) is int and not(type(self.settings[settingName]) is int):
                                try:
                                        self.settings[settingName] = int(self.settings[settingName])
                                except Exception as e:
                                        print ("Could not convert setting: "+settingName+" to type int", e.errno, e.strerror)
                        elif type(default) is str and not(type(self.settings[settingName]) is str):
                                try:
                                        self.settings[settingName] = str(self.settings[settingName])
                                except Exception as e:
                                        print ("Could not convert setting: "+settingName+" to type str", e.errno, e.strerror)
                        elif type(default) is float and not(type(self.settings[settingName]) is float):
                                try:
                                        self.settings[settingName] = float(self.settings[settingName])
                                except Exception as e:
                                        print ("Could not convert setting: "+settingName+" to type float", e.errno, e.strerror)
                        elif type(default) is list and not(type(self.settings[settingName]) is list):
                                try:
                                        self.settings[settingName] = list(self.settings[settingName])
                                except Exception as e:
                                        print ("Could not convert setting: "+settingName+" to type list", e.errno, e.strerror)
                        return copy.deepcopy(self.settings[settingName])
                else:
                        self.settings[settingName] = default
                        return copy.deepcopy(default)

        def setSetting(self,settingName,value):
                self.settings[settingName] = value

        def checkDialogTitle(self,d,mx,my):
                if (mx > d.x and mx < (d.x + d.width) and my > d.y and my < (d.y + d.title_height)):
                        self.moving_dialog = True
                        self.cur_moving_x = mx
                        self.cur_moving_y = my
                        return True
                else:
                        return False

        def mouseEvent(self,e):
                mx = e.pos[0]
                my = e.pos[1]   

                x = int(math.floor((mx - self.border) / self.tile_size))
                y = int(math.floor((my - self.border - self.top_height - self.menu_height) / self.tile_size))
                # find top dialog
                ds = self.getActiveDialogList(self)
                

                if len(ds) > 0:
                        ad = ds[0]

                        for i in ad.buttons:
                                cx = i.x + (i.width/2)
                                cy = i.y + (i.height/2)
                                if (abs(mx-cx) < i.width/2 and abs(my-cy) < i.height/2):                                        
                                        self.action(i)
                                        return True
                                
                        if not(self.moving_dialog):
                                self.checkDialogTitle(ad,mx,my)                 
                        
                        
                        if not(self.checkMenu(ad.gui.menubar,mx,my)):
                                ad.gui.menubar.close()
                        else:
                                return True
                else:
                        # check menus
                        if not(self.checkMenu(self.gui.menubar,mx,my)):
                                self.gui.menubar.close()
                        else:
                                return True

                if x >= 0 and y >= 0 and x < self.main_map.width and y < self.main_map.height and my >= self.top_height and self.running and len(ds) == 0 and self.paused == False:
                        if not(self.gen) and self.main_map.tiles[x][y].state == 0 and e.button == 1:
                                self.main_map.generate(x,y)
                                self.t1 = time.perf_counter()
                                self.tp = 0
                                self.gen = True
                        elif (self.main_map.tiles[x][y].state == 0 or (self.main_map.tiles[x][y].state == 3 and not self.gen))and e.button == 1:
                                self.main_map.reveal(x,y)
                        elif self.main_map.tiles[x][y].state < 3 and e.button == 3 and self.gen and (self.flags_left > 0 or self.main_map.tiles[x][y].state == 1):
                                self.main_map.tiles[x][y].state = (self.main_map.tiles[x][y].state + 1) % 3
                                self.main_map.tilesChangedSinceLastGrouping = True
                        elif (self.main_map.tiles[x][y].state == 3)and e.button == 2:
                                self.main_map.revealAll()

                        
                if len(ds) == 0:
                        for i in self.buttons:
                                cx = i.x + (i.width/2)
                                cy = i.y + (i.height/2)

                                if math.hypot(abs(i.x-mx),abs(i.y-my)) < (i.height/2.0) and i.cir:
                                        self.action(i)
                                
                                elif (abs(mx-cx) < i.width/2 and abs(my-cy) < i.height/2.0)and not (i.cir):
                                        self.action(i)


        def mouseMotion(self,event,obj):                
                ds = self.getActiveDialogList(obj)                      

                mx = event.pos[0]
                my = event.pos[1]   

                self.m_tile_x = int(math.floor((mx - self.border) / self.tile_size))
                self.m_tile_y = int(math.floor((my - self.border - self.top_height - self.menu_height) / self.tile_size))
               
                if len(ds) > 0:
                        ad = ds[0]
                        
                        if self.moving_dialog:
                                ad.updatePosition(mx-self.cur_moving_x,my-self.cur_moving_y)

                                self.cur_moving_x = mx
                                self.cur_moving_y = my                  
                        
                        self.checkMenuHover(ad.gui.menubar,event)
                else:
                        self.checkMenuHover(obj.gui.menubar,event)              
        
        def checkMenuHover(self,menu,e):
                mx = e.pos[0]
                my = e.pos[1]
                hover_expand_found = False
                # returns true if a menu is hovered, otherwise false
                # check open menus
                if not(type(menu) is MenuItem):                 
                        for m in menu.items:
                                m.hovered = False
                        for m in menu.items:
                                if not(type(m) is MenuItem):
                                        cx = m.x + (m.width/2)
                                        cy = m.y + (self.menu_height/2)

                                        if (abs(mx-cx) <= m.width/2.0 and abs(my-cy) <= self.menu_height/2.0):
                                                m.hovered = True
                                                m.temp_expanded = True
                                                hover_expand_found = m
                                                #return True
                                        elif (m.expanded or m.temp_expanded) and self.checkMenuHover(m,e):
                                                hover_expand_found = m
                                                m.hovered = True
                                        else:
                                                m.temp_expanded = False

                                else:
                                        cx = m.x + (m.width/2)
                                        cy = m.y + (self.menu_height/2)
                                        
                                        if (abs(mx-cx) <= m.width/2.0 and abs(my-cy) <= self.menu_height/2.0):
                                                m.hovered = True
                                                m.temp_expanded = True
                                                hover_expand_found = m
                        for m in menu.items:
                                if hover_expand_found != False and m != hover_expand_found:
                                        m.temp_expanded = False
                                        m.hovered = False
                                        if not(hover_expand_found.isParent(m)):
                                                m.closeExpanded()
        
                #print not(type(hover_expand_found) is bool)
                return not(type(hover_expand_found) is bool)

        def displayGUI(self,obj,perform,layer):
                if perform:
                        self.display_menu(obj.gui.menubar,layer)
                        self.display_dialog(obj,layer)                          

        def createMenu(self,menu_list,orig_relative_x,orig_relative_y,l,parent_menu):
                ret_list = []
                c = 0
                inc = 0
                for i in menu_list:
                        if len(i[3]) > 0:
                                temp_menu = Menu(l,i[0],i[1],[],i[2],orig_relative_x,orig_relative_y,0,False,True,i[4])

                                if l == 1:
                                        temp_menu.orig_width = max(60,self.gui.menu_font.size(i[0])[0]+10)
                                        temp_menu.orig_relative_x += c * temp_menu.orig_width                                   
                                elif l == 2:
                                        temp_menu.orig_relative_x += (l-2)*self.gui.orig_max_menu_width
                                        temp_menu.orig_relative_y += (self.menu_height + 0 )
                                        temp_menu.orig_width = self.gui.orig_max_menu_width
                                else:
                                        temp_menu.orig_relative_x += (l-2)*self.gui.orig_max_menu_width
                                        temp_menu.orig_width = self.gui.max_menu_width
                                temp_temp_menu = copy.deepcopy(temp_menu)
                                temp_temp_menu.items = self.createMenu(i[3],0,0,temp_menu.depth + 1,temp_temp_menu)                             
                                temp_temp_menu.parent = parent_menu

                                temp_temp_menu.relative_x = temp_temp_menu.orig_relative_x
                                temp_temp_menu.relative_y = temp_temp_menu.orig_relative_y
                                temp_temp_menu.width = temp_temp_menu.orig_width
                                temp_temp_menu.updateCoords()
                                ret_list.append(temp_temp_menu)
                        else:
                                temp_item = MenuItem(l,i[0],i[1],[],i[2],0,0,0,False,False,i[4],i[5])
                                if l == 1:
                                        temp_item.orig_relative_x += c * 60
                                        temp_item.orig_width = 60
                                elif l == 2:
                                        temp_item.orig_relative_y += (self.menu_height + 0 )
                                        temp_item.orig_width = self.gui.orig_max_menu_width
                                else:
                                        temp_item.orig_relative_x += (l-2)*self.gui.orig_max_menu_width
                                        temp_item.orig_width = self.gui.orig_max_menu_width
                                temp_item.orig_relative_y += (c) * (self.menu_height)
                                temp_temp_item = copy.deepcopy(temp_item)
                                temp_temp_item.parent = parent_menu

                                temp_temp_item.relative_x = temp_temp_item.orig_relative_x
                                temp_temp_item.relative_y = temp_temp_item.orig_relative_y
                                temp_temp_item.width = temp_temp_item.orig_width
                                
                                temp_temp_item.updateCoords()
                                ret_list.append(temp_temp_item)
                        c += 1
                return ret_list

        def display_menu(self,mm,layer):
                
                if mm.depth == 0 and (layer == -1 or mm.layer == layer):
                        #menu bar (lol)
                        s2 = pygame.Surface((mm.width, self.menu_height))
                        s2.fill(self.colour["menu"])
                        self.gameDisplay.blit(s2,(mm.x,mm.y))
                if mm.depth > 0 and mm.expanded and len(mm.items) > 0 and (layer == -1 or mm.layer == layer):
                        temp_r = pygame.Rect(mm.items[0].x,mm.items[0].y,mm.items[0].width,self.menu_height * len(mm.items))
                        pygame.draw.rect(self.gameDisplay,self.colour["menu_border"],temp_r,3)
                for m in mm.items:
                        
                        if layer == -1 or m.layer == layer:
                                temp_m = pygame.Surface((m.width,self.menu_height))
                                ###
                                if m.expanded or m.hovered:
                                        temp_m.fill(self.colour["menu_selected"])

                                else:
                                        temp_m.fill(self.colour["menu"])
                                if m.text.lower().find(m.shortcut.lower()) > -1:
                                        f_ind = m.text.lower().find(m.shortcut.lower())
  
                                        n0 = self.gui.menu_font.render(m.text[:f_ind],True,(0,0,0))
                                        self.gui.menu_font.set_underline(True)
                                        n = self.gui.menu_font.render(m.text[f_ind],True,(0,0,0))
                                        self.gui.menu_font.set_underline(False)
                                        n1 = self.gui.menu_font.render(m.text[f_ind+1:],True,(0,0,0))
                                        temp_m.blit(n0,(5,0))
                                        temp_m.blit(n,(5 + self.gui.menu_font.size(m.text[:f_ind])[0] ,0))
                                        temp_m.blit(n1,(5 + self.gui.menu_font.size(m.text[:f_ind])[0] + self.gui.menu_font.size(m.text[f_ind])[0] ,0))
                      
                                else:
                                        n = self.gui.menu_font.render(m.text,True,(0,0,0))
                                        temp_m.blit(n,(5,0))
                                
                                #n = self.gui.menu_font.render(m.text,True,(0,0,0))
                                n2 = self.gui.menu_font.render(m.shortcut.upper(),True,(0,0,0))
                                n3 = self.gui.menu_font.render(">",True,(0,0,0))
                                
                                if m.depth > 1:
                                        temp_m.blit(n2,(int(150*self.getSetting("app_scaling",1.0)),0))
                                        if len(m.items) > 0:
                                                temp_m.blit(n3,(int(180*self.getSetting("app_scaling",1.0)),0))

                                self.gameDisplay.blit(temp_m,(m.x,m.y))
                        ###
                        
                        if m.expanded or m.temp_expanded:
                                self.display_menu(m,layer)
                                
        def checkMenuShortcut(self,menu):
                if not(type(menu) is MenuItem):
                        for m in menu.items:
                                if m.expanded == True or m.temp_expanded == True:
                                        if not(type(m) is MenuItem):
                                                match_list = m.shortcut.split('+')
                                                matches = 0
                                                for i in match_list:
                                                        if self.key_map[i] in self.pressed:
                                                                matches += 1

                                                if (matches == len(match_list) and m.last_shortcut  < time.perf_counter() - m.shortcut_cooldown):
                                                        m.last_shortcut = time.perf_counter()
                                                        m.close()
                                                        return True
                                                if self.checkMenuShortcut(m):
                                                        return True
                                        else:
                                                match_list = m.shortcut.split('+')
                                                matches = 0
                                                for i in match_list:
                                                        if self.key_map[i] in self.pressed:
                                                                matches += 1
                                                if (matches == len(match_list) and m.last_shortcut  < time.perf_counter() - m.shortcut_cooldown):
                                                        m.last_shortcut = time.perf_counter()
                                                        self.action(m)
                                                        m.closeUp()
                                                        return True

                        # check closed menus second
                        for m in menu.items:
                                if m.expanded == False and m.temp_expanded == False:
                                        if not(type(m) is MenuItem):
                                                match_list = m.shortcut.split('+')
                                                matches = 0
                                                for i in match_list:
                                                        if self.key_map[i] in self.pressed:
                                                                matches += 1
                                                if (matches == len(match_list) and m.last_shortcut  < time.perf_counter() - m.shortcut_cooldown):
                                                        m.last_shortcut = time.perf_counter()
                                                        m.close()
                                                        m.expanded = True
                                                        return True
                                        else:
                                                match_list = m.shortcut.split('+')
                                                matches = 0
                                                for i in match_list:
                                                        if self.key_map[i] in self.pressed:
                                                                matches += 1
                                                if (matches == len(match_list) and m.last_shortcut  < time.perf_counter() - m.shortcut_cooldown):
                                                        m.last_shortcut = time.perf_counter()
                                                        self.action(m)
                                                        m.closeUp()
                                                        return True

                return False
                
        def checkMenu(self,menu,mx,my):
                # returns true if a menu was clicked, otherwise false
                # check open menus
                if not(type(menu) is MenuItem):
                        for m in menu.items:
                                if m.expanded == True or m.temp_expanded == True:
                                        if not(type(m) is MenuItem):
                                                cx = m.x + (m.width/2)
                                                cy = m.y + (self.menu_height/2)
                                                
                                                if (abs(mx-cx) < m.width/2 and abs(my-cy) < self.menu_height/2):
                                                        if m.expanded == False:
                                                                m.expandUp()
                                                        else:
                                                                m.close()
                                                        return True
                                                if self.checkMenu(m,mx,my):
                                                        return True
                                                else:
                                                        m.close()
                                        else:
                                                cx = m.x + (m.width/2)
                                                cy = m.y + (self.menu_height/2)
                                                if (abs(mx-cx) < m.width/2 and abs(my-cy) < self.menu_height/2):
                                                        self.action(m)
                                                        m.closeUp()
                                                        return True

                        # check closed menus second
                        for m in menu.items:
                                if m.expanded == False and m.temp_expanded == False:
                                        if not(type(m) is MenuItem):
                                                cx = m.x + (m.width/2)
                                                cy = m.y + (self.menu_height/2)
                                                if (abs(mx-cx) < m.width/2 and abs(my-cy) < self.menu_height/2):
                                                        if m.expanded == False:
                                                                m.expandUp()
                                                        else:
                                                                m.close()
                                                        m.expanded = True
                                                        return True
                                        else:
                                                cx = m.x + (m.width/2)
                                                cy = m.y + (self.menu_height/2)
                                                if (abs(mx-cx) < m.width/2 and abs(my-cy) < self.menu_height/2):
                                                        self.action(m)
                                                        m.closeUp()
                                                        return True

                return False

        def processKeyPress(self):
                for event in self.events:
                        if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                        ds = self.getActiveDialogList(self)
                                        if len(ds) > 0:
                                                self.action(ds[0].buttons[0])
                                                break
                                        self.running = False
                                        self.playing = False
                                        break
                                if event.key in self.keys:
                                        self.cur_key = event.key
                                        self.pressed.append(self.cur_key)
                        if event.type == pygame.KEYUP:
                                if event.key in self.pressed:
                                        self.pressed.remove(event.key)
                                if event.key == pygame.K_p and self.running:
                                        self.paused = not(self.paused)
                                        if self.paused == True:
                                                self.tp += self.tc - self.t1
                                                #print self.tp,self.tc,self.t1

                        if event.type == pygame.MOUSEBUTTONDOWN:
                                self.mouseEvent(event)
                        if event.type == pygame.MOUSEBUTTONUP:
                                self.moving_dialog = False
                        if event.type == pygame.MOUSEMOTION:
                                self.mouseMotion(event,self)
                        if event.type == pygame.QUIT:
                                self.running = False
                                self.playing = False
                                self.lose = False
                                self.win = False
                for i in self.pressed:
                        if i == pygame.K_r and self.running and self.gen:
                                self.reveal = True
                        elif i == pygame.K_t and self.running and self.gen:
                                self.subtract = True
                        elif i == pygame.K_o and self.gen and self.running and self.paused == False:
                                self.main_map.cheatAll(self.flags_left,self.counts)
                        elif i == pygame.K_g and self.running and self.gen:
                                self.percentage = True
                                                        
                        ds = self.getActiveDialogList(self)
                        if len(ds) > 0:
                                if self.checkMenuShortcut(ds[0].gui.menubar):
                                        return  True
                        elif self.checkMenuShortcut(self.gui.menubar):
                                return True

        def getExpandedMenuWidth(self,menu):
                w = 0

                for m in menu.items:
                        w = max(w,m.x + m.width)
                        if not(type(m) is MenuItem):
                                if m.expanded == True or m.temp_expanded == True:
                                        w = max(w, self.getExpandedMenuWidth(m))

                return w

        def getExpandedMenuHeight(self,menu):
                h = 0

                for m in menu.items:
                        h = max(h,m.y + self.menu_height)
                        if not(type(m) is MenuItem):
                                if m.expanded == True or m.temp_expanded == True:
                                        h = max(h, self.getExpandedMenuHeight(m))

                return h
                        
        def updateDisplaySize(self):
                cur_width = self.window_width
                cur_height = self.window_height
                
                map_width = self.main_map.width * self.tile_size
                map_height = self.menu_height + self.main_map.height * self.tile_size + self.top_height

                self.game_map_width = map_width
                self.game_map_height = map_height

                self.window_width = self.game_map_width + 2 * self.border
                self.window_height = self.game_map_height  + 2 * self.border

                needed_width = self.window_width

                needed_height = self.window_height              
                        
                if self.has_gui:
                        ds = self.getActiveDialogList(self)
                        
                        if len(ds) > 0:
                                for d in ds:
                                        needed_width = max(needed_width,self.getExpandedMenuWidth(d.gui.menubar))
                                        needed_width = max(needed_width, d.x + d.width + 2)

                                        needed_height = max(needed_height,self.getExpandedMenuHeight(d.gui.menubar))
                                        needed_height = max(needed_height, d.y + d.height + 2)
                                        
                        needed_width = max(needed_width,self.getExpandedMenuWidth(self.gui.menubar))
                        needed_height = max(needed_height,self.getExpandedMenuHeight(self.gui.menubar))
                        
                self.window_width = needed_width
                self.window_height = needed_height

                if self.has_gui:
                        self.gui.menubar.width = self.window_width

                if cur_width != self.window_width or cur_height != self.window_height:
                        self.gameDisplay = pygame.display.set_mode((self.window_width ,self.window_height))


        def play(self):
                self.playing = True
                self.has_gui = False
                self.checkSettings()
                while(self.playing):
                        self.running = True
                        self.paused = False
                        self.mouseE = []

                        #self.buttons = []

                        self.t1 = 0
                        self.tc = 0
                        self.tp = 0
                        
                        self.checkSettings()

                        self.main_map = self.create_map(self.difs[self.getSetting("current_difficulty",2)])

                        #print self.difs[self.getSetting("current_difficulty",2)].name

                        self.gen = False

                        self.bombs_left = self.main_map.numBombs

                        self.win = False

                        self.lose = False

                        self.flags_left = self.main_map.numBombs
                                
                        self.updateDisplaySize()

                        self.timer = 0.0

                        self.top = pygame.Rect(0,self.menu_height,self.game_map_width,self.top_height)

                        # MENUS

                        
                        

                        # Menu Items (File > Difficulty > Esay, Intermediate, Hard)
                        if not(self.menu_gen):
                                difsMenu = []
                                for di in self.difs:
                                        difsMenu.append([di.name,di.hotKeyLabel,di.hotKey,[],5,"dif_switch_"+di.name.lower()])
                                                        
                                self.menu_gen = True
                                menu_list = [
                                        ["File","","f",
                                         [
                                                ["Difficulty","D","d",
                                                 difsMenu,4
                                                 ],
                                                ["Scaling","S","s",[],4,"open_scaling_dialog"]
                                                ],3
                                         ],
                                        ["Help","","h",
                                         [
                                                ["Instructions","I","i",[],4,"open_help_dialog"],
                                                ["Controls","C","c",[],4,"open_controls_dialog"]
                                         ],3
                                        ]
                                        ]

                                temp_menu_bar = MenuBar(0,0,0,[],self.window_width,1)
                                self.gui = FakeGui({},temp_menu_bar,self.menu_font,200)
                                self.has_gui = True
                                self.gui.menubar.items = self.createMenu(menu_list,0,0,1,self.gui.menubar)

                                ## Dialogs

                                ## Scaling Dialog
                                scaling_dialog = Dialog(0,0,300,200,10,[],False,"Scaling",20)
                                self.gui.dialogs["scaling"] = scaling_dialog
                                d = self.gui.dialogs["scaling"]
                                scale_menubar = MenuBar(0,2,scaling_dialog.title_height+2,[],d.width-4,d.layer+1)
                                d.gui = FakeGui({},scale_menubar,self.menu_font,120)
                                d.gui.menubar.parent = d
                                
                                scale_text = TextBox(d.layer,"scale",self.menu_height,60,"Change the size of the game: ",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d.width-50,(0,0,0),d)
                                
                                d.textboxes.append(scale_text)

                                d.updatePosition(0,0)

                                ds1 = button.Button(d.layer+2,scale_text.relative_x + int(50),scale_text.relative_y+30,100,24,"70%","app_set_scale_70",False,d)
                                ds2 = button.Button(d.layer+2,scale_text.relative_x + int(50),ds1.relative_y+30,100,24,"85%","app_set_scale_85",False,d)
                                ds3 = button.Button(d.layer+2,scale_text.relative_x + int(50),ds2.relative_y+30,100,24,"Default","app_set_scale_100",False,d)
                                ds4 = button.Button(d.layer+2,scale_text.relative_x + int(50),ds3.relative_y+30,100,24,"115%","app_set_scale_115",False,d)
                                ds5 = button.Button(d.layer+2,scale_text.relative_x + int(50),ds4.relative_y+30,100,24,"130%","app_set_scale_130",False,d)

                                d.buttons.append(ds1)
                                d.buttons.append(ds2)
                                d.buttons.append(ds3)
                                d.buttons.append(ds4)
                                d.buttons.append(ds5)

                                d.updateHeight()

                                ## Help dialog
                                help_dialog = Dialog(0,0,600,350,10,[],False,"Instructions",20,self.getSetting("app_scaling",1.0))
                                self.gui.dialogs["help"] = help_dialog
                                help_menubar = MenuBar(0,2,help_dialog.title_height+2,[],self.gui.dialogs["help"].width-4,self.gui.dialogs["help"].layer+1)
                                self.gui.dialogs["help"].gui = FakeGui({},help_menubar,self.menu_font,120)

                                difsHelpMenu = []
                                for di in self.difs:
                                        difsHelpMenu.append([di.name,di.hotKeyLabel,di.hotKey,[],help_menubar.layer + 3,"help_info_dialog_"+di.name.lower()])

                                help_menu_list = [
                                        ["Difficulty Info","","d",
                                         difsHelpMenu
                                         ,help_menubar.layer + 2
                                        ]
                                        ]
                                d = self.gui.dialogs["help"]
                                d.gui.menubar.items = self.createMenu(help_menu_list,0,0,1,d.gui.menubar)
                                d.gui.menubar.parent = d
                        

                                ## Help Text

                                help_text = TextBox(d.layer,"instr",self.menu_height,60,"Left click a tile to reveal it, the first tile clicked will always be safe. The number on the revealed tile will indicate how many adjacent bombs there are to that tile, the game ends if you click on a bomb. Tiles without a number are not adjacent to any bombs and will reveal all tiles that are adjacent to them as well. Right click a hidden tile to 'flag' it, right click again to mark the tile 'unknown'. Flagging a tile indicates that you think that tile is a bomb. Marking 'unkown' indicates that there is not yet enough information to determine whether the tile is a bomb or not, marked tiles cannot be left clicked, right click on a marked tile to remove the mark. Left click a revealed number tile once all adjacent bombs have been flagged to reveal the any adjacent tiles that also have their bombs flagged. The number at the top right of the screen indicates how many flags you have left to use, this number is equal to the total number of bombs. The number at the top right is the time, once you reveal a tile it will count up until the game ends. You will win once all safe tiles have been revealed even if not all bombs are flagged. Click the circle at the top in the middle to restart the game.",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d.width-50,(0,0,0),d)

                                d.textboxes.append(help_text)

                                d.updatePosition(0,0)
                                dc = 0
                                help_temp_text = []
                                score_temp_text = []
                                temp_dialog = []

                                for hdi in self.difs:
                                        # Dif Information
                                        temp_dialog.append(Dialog(0,0,400,100,d.layer + 10,[],False,hdi.name,20,self.getSetting("app_scaling",1.0)))
                                        d.gui.dialogs["help_info_dialog_"+hdi.name.lower()] = temp_dialog[dc]
                                        temp_menubar = MenuBar(0,2,temp_dialog[dc].title_height+2,[],d.gui.dialogs["help_info_dialog_"+hdi.name.lower()].width-4,d.gui.dialogs["help_info_dialog_"+hdi.name.lower()].layer+1)
                                        d.gui.dialogs["help_info_dialog_"+hdi.name.lower()].gui = FakeGui({},copy.deepcopy(temp_menubar),self.menu_font,120)
                                        d2 = d.gui.dialogs["help_info_dialog_"+hdi.name.lower()]
                                        d2.gui.menubar.parent = d2

                                        # Dif Help Text

                                        help_temp_text.append(TextBox(d2.layer,"info_"+hdi.name.lower(),self.menu_height,75,"The {0} game mode uses a {1}x{2} board. There are {3} bombs to find.".format(hdi.name,str(hdi.width),str(hdi.height),str(hdi.bombs)), pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2))
                                        
                                        d2.textboxes.append(help_temp_text[dc])                                 

                                        d2.updatePosition(0,0)

                                        score_temp_text.append(TextBox(d2.layer,"score_"+hdi.name.lower(),self.menu_height,help_temp_text[dc].y + help_temp_text[dc].height + 10,"Best Time:", pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2))
                                        
                                        d2.textboxes.append(score_temp_text[dc])

                                        d2.updatePosition(0,0)

                                        d2.buttons.append(button.Button(d2.layer+2,score_temp_text[dc].relative_x + 260,score_temp_text[dc].relative_y-10,100,24,"Reset","reset_score_"+hdi.name.lower(),False,d2))
        
                                        dc += 1

                                ## Controls Dialog
                                controls_dialog = Dialog(0,0,600,350,10,[],False,"Controls",25,self.getSetting("app_scaling",1.0))
                                self.gui.dialogs["controls"] = controls_dialog
                                controls_menubar = MenuBar(0,2,controls_dialog.title_height+2,[],self.gui.dialogs["controls"].width-4,self.gui.dialogs["controls"].layer+1)
                                self.gui.dialogs["controls"].gui = FakeGui({},controls_menubar,self.menu_font,120)

                                controls_menu_list = []
                                d = self.gui.dialogs["controls"]
                                d.gui.menubar.items = self.createMenu(controls_menu_list,0,0,1,d.gui.menubar)
                                d.gui.menubar.parent = d

                                

                                ## Controls Text

                                controls_text_0 = TextBox(d.layer,"contrl0",self.menu_height,60,"These are the controls used for hints or to cheat. o: Completely cheat the game, reveal all tiles and flag all bombs; This ends the current game; Highscores will not apply. t: Subtracts flagged tiles from displayed numbers; a learning tool for visualization. r: reveals all bombs, a cheat; Highscores will not apply. g: Shows possibility of a bomb on each tile using known information; 0% is accurate, other percentages may be inaccurate; Used to learn the game. Middle click: Reveal all tiles around completely flagged numbers; if flags are wrong you will lose the game.",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d.width-50,(0,0,0),d)
                                #controls_text_1 = TextBox(d.layer,"contrl1",self.menu_height,controls_text_0.relative_y + + controls_text_0.height - 30,"o: Completely cheat the game, reveal all tiles and flag all bombs; This ends the current game; Highscores will not apply.",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d.width-50,(0,0,0),d)





                                d.textboxes.append(controls_text_0)
                                #d.textboxes.append(controls_text_1)

                                d.updatePosition(0,0)
                                
                        
##                              #Intermediate Information
##                              
##                              help_intermediate_dialog = Dialog(0,0,400,100,d.layer + 10,[],False,"Intermediate",20,self.getSetting("app_scaling",1.0))
##                              d.gui.dialogs["help_info_dialog_intermediate"] = help_intermediate_dialog
##                              help_intermediate_menubar = MenuBar(0,2,help_intermediate_dialog.title_height+2,[],d.gui.dialogs["help_info_dialog_intermediate"].width-4,d.gui.dialogs["help_info_dialog_intermediate"].layer+1)
##                              d.gui.dialogs["help_info_dialog_intermediate"].gui = FakeGui({},help_intermediate_menubar,self.menu_font,120)
##
##                              d2 = d.gui.dialogs["help_info_dialog_intermediate"]
##                              d2.gui.menubar.parent = d2              
##
##                              ## Help Text Intermediate
##
##                              help_intermediate_text = TextBox(d2.layer,"info_intermediate",self.menu_height,75,"The intermediate game mode uses a 16x16 board. There are 40 bombs to find.",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2)
##
##                              d2.textboxes.append(help_intermediate_text)
##
##                              d2.updatePosition(0,0)
##
##                              score_intermediate_text = TextBox(d2.layer,"score_intermediate",self.menu_height,help_intermediate_text.y + help_intermediate_text.height + 10,"Best Time:",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2)
##                              score_intermediate_text.formatText()
##                              d2.textboxes.append(score_intermediate_text)
##
##                              d2.updatePosition(0,0)
##
##                              d2.buttons.append(button.Button(d2.layer+2,score_intermediate_text.relative_x + 260,score_intermediate_text.relative_y-10,100,24,"Reset","reset_score_intermediate",False,d2))
##
##                              #Hard Information
##                              
##                              help_hard_dialog = Dialog(0,0,400,100,d.layer + 10,[],False,"Hard",20,self.getSetting("app_scaling",1.0))
##                              d.gui.dialogs["help_info_dialog_hard"] = help_hard_dialog
##                              help_hard_menubar = MenuBar(0,2,help_hard_dialog.title_height+2,[],d.gui.dialogs["help_info_dialog_hard"].width-4,d.gui.dialogs["help_info_dialog_hard"].layer+1)
##                              d.gui.dialogs["help_info_dialog_hard"].gui = FakeGui({},help_hard_menubar,self.menu_font,120)
##
##                              d2 = d.gui.dialogs["help_info_dialog_hard"]
##                              d2.gui.menubar.parent = d2              
##
##                              ## Help Text Hard
##
##                              help_hard_text = TextBox(d2.layer,"info_hard",self.menu_height,75,"The hard game mode uses a 40x16 board. There are 99 bombs to find.",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2)
##
##                              d2.textboxes.append(help_hard_text)
##
##                              d2.updatePosition(0,0)
##
##                              score_hard_text = TextBox(d2.layer,"score_hard",self.menu_height,help_hard_text.y + help_hard_text.height + 10,"Best Time:",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2)
##                              score_hard_text.formatText()
##                              d2.textboxes.append(score_hard_text)
##
##                              d2.updatePosition(0,0)
##
##                              d2.buttons.append(button.Button(d2.layer+2,score_hard_text.relative_x + 260,score_hard_text.relative_y-10,100,24,"Reset","reset_score_hard",False,d2))
##
##                              #Extreme Information
##                              
##                              help_extreme_dialog = Dialog(0,0,400,100,d.layer + 10,[],False,"Extreme",20,self.getSetting("app_scaling",1.0))
##                              d.gui.dialogs["help_info_dialog_extreme"] = help_extreme_dialog
##                              help_extreme_menubar = MenuBar(0,2,help_extreme_dialog.title_height+2,[],d.gui.dialogs["help_info_dialog_extreme"].width-4,d.gui.dialogs["help_info_dialog_extreme"].layer+1)
##                              d.gui.dialogs["help_info_dialog_extreme"].gui = FakeGui({},help_extreme_menubar,self.menu_font,120)
##
##                              d2 = d.gui.dialogs["help_info_dialog_extreme"]
##                              d2.gui.menubar.parent = d2              
##
##                              ## Help Text Extreme
##
##                              help_extreme_text = TextBox(d2.layer,"info_extreme",self.menu_height,75,"The extreme game mode uses a 40x24 board. There are 192 bombs to find.",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2)
##
##                              d2.textboxes.append(help_extreme_text)
##
##                              d2.updatePosition(0,0)
##
##                              score_extreme_text = TextBox(d2.layer,"score_extreme",self.menu_height,help_extreme_text.y + help_extreme_text.height + 10,"Best Time:",pygame.font.SysFont("courier", int(self.tile_size / 2.5)),d2.width-50,(0,0,0),d2)
##                              score_extreme_text.formatText()
##                              d2.textboxes.append(score_extreme_text)
##
##                              d2.updatePosition(0,0)

                                for i in self.difs:
                                        n = i.name
                                        hs = self.getSetting("high_score_list_"+n.lower()+str(i.width)+'x'+str(i.height)+'b'+str(i.bombs),[])
                                        #print "high_score_list_"+n.lower(),hs
                                        if len(hs) == 0:
                                                self.updateScore(n,"")
                                        else:
                                                self.updateScore(n,hs[0],False)
                                

                                #d2.buttons.append(button.Button(d2.layer+2,score_extreme_text.relative_x + 260,score_extreme_text.relative_y-10,100,24,"Reset","reset_score_extreme",False,d2))


                                #self.buttons.append(button.Button(0,int((2 * self.border + self.game_map_width)/2.5), int((self.border + self.top_height)/2.0)  + self.menu_height/3,self.tile_size,self.tile_size,"C+","add_counts",False))
                                #self.buttons.append(button.Button(0,int((2 * self.border + self.game_map_width)/2.3), int((self.border + self.top_height)/2.0)  + self.menu_height/3,self.tile_size,self.tile_size,"C-","subtract_counts",False))
                        
                                ## Restart button
                                self.buttons.append(button.Button(0,int((2 * self.border + self.game_map_width)/2), int((self.border + self.top_height)/2.0)  + self.menu_height,self.tile_size,self.tile_size,"Restart","game_restart",True))

                        self.checkSettings()
                        temp_s = self.getSetting("app_scaling",1.0)
                        #
                        self.updateScaling(temp_s)
                        self.updateScaling(temp_s)

                        while(self.running):
                                self.events = pygame.event.get()
                                self.reveal = False
                                self.subtract = False
                                self.percentage = False

                                if self.gen:
                                        self.tc = time.perf_counter()
                                else:
                                        self.tc = time.perf_counter()
                                        self.t1 = self.tc
                                        self.tp = 0
                                        self.cheater = False

                                if self.paused == True:
                                        self.t1 = self.tc
                                #else:
                                        

                                self.processKeyPress()
                                for i in self.pressed:
                                        if i == pygame.K_r and self.gen:
                                                self.reveal = True
                                                self.cheater = True
                                        elif i == pygame.K_t and self.gen:
                                                self.subtract = True
                                        elif i == pygame.K_o and self.gen:
                                                self.main_map.cheatAll(self.flags_left,self.counts)
                                                self.cheater = True
                                        elif i == pygame.K_g and self.gen:
                                                self.percentage = True
                                                #self.cheater = True

                                if self.percentage:
                                        self.main_map.processTileGroupings(self.flags_left,self.counts)
                                
                                if not(self.moving_dialog):
                                        self.updateDisplaySize()
                                self.display_map()
                                self.display_score()
                                
                                self.display_paused()
                                
                                for lay in range(self.num_layers):
                                        self.display_buttons(self.buttons,lay)
                                        self.displayGUI(self,True,lay)
                                
                                self.checkWin()
                                pygame.display.update()
                                self.clock.tick(self.fps)
                                
                        if(self.win and not(self.lose) and not(self.score_updated)):
                                #print 'win'
                                if(not(self.cheater)):
                                        self.updateScore(self.difs[self.getSetting("current_difficulty",2)].name,round(self.tp + self.tc - self.t1,3))

                                self.score_updated = True
                                
                                
                        while(self.win or self.lose):
                                if not(self.moving_dialog):
                                        self.updateDisplaySize()
                                self.display_map()
                                self.display_score()
                                for lay in range(self.num_layers):
                                        self.display_buttons(self.buttons,lay)
                                        self.displayGUI(self,True,lay)
                                pygame.display.update()
                                self.clock.tick(self.fps)

                                self.events = pygame.event.get()
                                self.reveal = False
                                self.pecentage = False
                                self.subtract = False
                                self.processKeyPress()

                        self.saveSettings(0)    
                
                pygame.quit()

app = App()
app.play()
