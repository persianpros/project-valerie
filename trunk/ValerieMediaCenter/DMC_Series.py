from enigma import eTimer, eWidget, eRect, eServiceReference, iServiceInformation, iPlayableService, ePicLoad
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.Button import Button

from Components.Sources.List import List
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen

from Components.ServicePosition import ServicePositionGauge
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
#from Screens.DMC_MoviePlayer import DMC_MoviePlayer
from Screens.InfoBar import MoviePlayer

from Plugins.Plugin import PluginDescriptor


from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap

import os
from os import path as os_path

from DMC_Global import Showiframe

#------------------------------------------------------------------------------------------

class DMC_Series(Screen, HelpableScreen, InfoBarBase):

	def __init__(self, session):
		Screen.__init__(self, session)
		InfoBarBase.__init__(self)
		HelpableScreen.__init__(self)
		self.showiframe = Showiframe()
		
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()	

		self.isVisible = True
		self.inSeries = True
		self.inSeasons = False
		self.inEpisode = False
		self.rememeberSeriesIndex = 0
		self.selectedSeries = 0
		self.serieslist = []
		self.moviedb = {}
		self.episodesdb = {}
		
		self["listview"] = MenuList(self.serieslist)
		self["poster"] 				= Pixmap()
		self["title"] 				= Label()
		self["otitle"] 				= Label()
		self["tag"] 				= Label()
		self["shortDesc"] 	        = Label()
		self["director"] 			= Label()
		self["writer"] 				= Label()
		self["genre"] 				= Label()
		self["year"] 				= Label()
		self["runtime"] 			= Label()
		#self["poster"] 				= Pixmap()
		
		for i in range(10):
			stars = "star" + str(i)
			print stars
			self[stars] = Pixmap()

		self["actions"] = HelpableActionMap(self, "MC_AudioPlayerActions", 
			{
				"ok": (self.KeyOk, "Play selected file"),
				"cancel": (self.KeyExit, "Exit Audio Player"),
				"left": (self.leftUp, "List Top"),
				"right": (self.rightDown, "List Bottom"),
				"up": (self.up, "List up"),
				"down": (self.down, "List down"),
			}, -2)
		
		self.loadSeriesDB()

		self.onFirstExecBegin.append(self.refresh)

	def loadSeriesDB(self):
		list =[]
		filter = []
		entrys =[]
		if self.inSeries or self.inEpisode:
			filter.append("Tag")
			filter.append("Plot")
			filter.append("LocalPlot")
			filter.append("Directors")
			filter.append("Writers")
			filter.append("Genres")
			filter.append("Year")
			filter.append("Runtime")
			filter.append("Popularity")
			filter.append("ImdbId")
			filter.append("Title")
			filter.append("LocalTitle")
			filter.append("TheTvDb")
			filter.append("Path")
		if self.inSeasons or self.inEpisode:
			filter.append("Season")
			filter.append("Episode")
				
		try:
			if self.inSeries:
				self.serieslist=[]
				db = open("/hdd/valerie/seriesdb.txt").read()[:-1]
			else:
				db = open("/hdd/valerie/episodes/" + self.selectedSeries + ".txt").read()[:-1]
					
			movies = db.split("\n----END----\n")
			

			for movie in movies:
				movie = movie.split("---BEGIN---\n")
				if len(movie) == 2: 
					d = {} 
					lines = movie[1].split('\n')
					for line in lines: 
						#print "Line: ", line
						if ":" in line: 
						    key, text = (s.strip() for s in line.split(":", 1)) 

						if key in filter: 
							d[key] = text

					#print d
					if self.inSeries:
						self.moviedb[d["TheTvDb"]] = d
						if not d["Title"] in entrys:
							entrys.append(d["Title"])
							if d["LocalTitle"] != "":
								self.serieslist.append((d["LocalTitle"], d["TheTvDb"], "menu_globalsettings", "50"))
							else:
								self.serieslist.append((d["Title"], d["TheTvDb"], "menu_globalsettings", "50"))
					elif self.inSeasons:
						if not d["Season"] in entrys:
							entrys.append(d["Season"])
							list.append(("Season " + d["Season"], d["Season"], "menu_globalsettings", "50"))			
					else:
						if d["Season"] == self.selectedSeason:
							if not d["Episode"] in entrys:
								entrys.append(d["Episode"])
								self.episodesdb[d["Season"]+"x"+ ("%02d" % int(d["Episode"]))] = d
								if d["LocalTitle"] != "":
									list.append((d["Season"]+"x"+("%02d" % int(d["Episode"])) + ": " + d["LocalTitle"], d["Season"]+"x"+("%02d" % int(d["Episode"])), "menu_globalsettings", "50"))
								else:
									list.append((d["Season"]+"x"+("%02d" % int(d["Episode"])) + ": " + d["Title"], d["Season"]+"x"+("%02d" % int(d["Episode"])), "menu_globalsettings", "50"))
								
						
		except OSError, e: 
			print "OSError: ", e
		
		if self.inSeries:
			self.serieslist.sort()
			self["listview"].setList(self.serieslist)	
		elif self.inSeasons:
			list.sort()
			self["listview"].setList(list)
		elif self.inEpisode:
			list.sort()
			self["listview"].setList(list)
			
		self["listview"].moveToIndex(0)
		self.refresh()
			

	def refresh(self):
		selection = self["listview"].getCurrent()
		if selection is not None:
			if self.inSeries is True:
				self.showiframe.showStillpicture("/hdd/valerie/media/" + selection[1] + "_backdrop.m1v")
				if self["poster"].instance is not None:
					self["poster"].instance.setPixmapFromFile("/hdd/valerie/media/" + selection[1] + "_poster.png")
				self["title"].setText(selection[0])
				self["otitle"].setText(self.moviedb[selection[1]]["Title"])
				self["tag"].setText(self.moviedb[selection[1]]["Tag"])
				self["shortDesc"].setText(self.moviedb[selection[1]]["Plot"])
				self["director"].setText(self.moviedb[selection[1]]["Directors"])
				self["writer"].setText(self.moviedb[selection[1]]["Writers"])
				self["genre"].setText(self.moviedb[selection[1]]["Genres"])
				self["year"].setText(self.moviedb[selection[1]]["Year"])
				self["runtime"].setText(self.moviedb[selection[1]]["Runtime"])
				for i in range(int(self.moviedb[selection[1]]["Popularity"])):
					if self["star" + str(i)].instance is not None:
						self["star" + str(i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/defaultHD/images/Valerie_Star.png")

				for i in range(10 - int(self.moviedb[selection[1]]["Popularity"])):
					if self["star" + str(9 - i)].instance is not None:
						self["star" + str(9 - i)].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/defaultHD/images/Valerie_NoStar.png")

			elif self.inEpisode is True:
				self["title"].setText(selection[0])
				if self.episodesdb[selection[1]]["LocalPlot"] and self.episodesdb[selection[1]]["LocalPlot"] !="":
					self["shortDesc"].setText(self.episodesdb[selection[1]]["LocalPlot"])
				else:
					self["shortDesc"].setText(self.episodesdb[selection[1]]["Plot"])
			
	def up(self):
		self["listview"].up()
		self.refresh()


	def down(self):
		self["listview"].down()
		self.refresh()
		
	def leftUp(self):
		self["listview"].pageUp()
		self.refresh()
		
	def rightDown(self):
		self["listview"].pageDown()
		self.refresh()



	def KeyOk(self):

		selection = self["listview"].getCurrent()
		if selection is not None:
			if self.inSeries is True:
				self.inSeries = False
				self.inSeasons = True
				self.inEpisode = False
				
				self.selectedSeries = selection[1]
				self.rememeberSeriesIndex = self["listview"].getSelectionIndex()
				
				seasonslist = []
				self.seasonsdb = {}
				
				self.loadSeriesDB()
				self.refresh()
				
			elif self.inSeasons is True:
				self.inSeries = False
				self.inSeasons = False
				self.inEpisode = True

				self.selectedSeason = selection[1]
				self.rememeberSeasonsIndex = self["listview"].getSelectionIndex()

				self.loadSeriesDB()
				self.refresh()

			elif self.inEpisode is True:
				if self.isVisible == False:
					self.visibility()
					return
		
				self.showiframe.finishStillPicture()
		
				selection = self["listview"].getCurrent()
				if selection is not None:
					self.session.openWithCallback(self.leaveMoviePlayer, MoviePlayer, eServiceReference("4097:0:1:0:0:0:0:0:0:0:" + self.episodesdb[selection[1]]["Path"] + ":" + selection[0]))


	def leaveMoviePlayer(self): 
		self.session.nav.playService(None) 
		self.showiframe.showStillpicture("/hdd/valerie/media/" + self.selectedSeries + "_backdrop.m1v")

	def KeyExit(self):
		if self.inSeries is True:
			if self.isVisible == False:
				self.visibility()
				return
		
			self.showiframe.finishStillPicture()

			self.close()
		elif self.inEpisode is True or self.inSeasons is True:
			self.inSeries = True
			self.inSeasons = False
			self.inEpisode = False
			self["listview"].setList(self.serieslist)
			self["listview"].moveToIndex(self.rememeberSeriesIndex)
			self.refresh()

#------------------------------------------------------------------------------------------

