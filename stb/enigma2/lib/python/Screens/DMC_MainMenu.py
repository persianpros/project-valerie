from enigma import eTimer, eDVBDB
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText

from Components.ConfigList import ConfigList
from Components.config import *

from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch

import os

# Plugins
from MC_AudioPlayer import MC_AudioPlayer
from DMC_Movies import DMC_Movies
from DMC_Series import DMC_Series
from MC_Settings import MC_Settings, MCS_Update


currentmcversion = "092"
currentmcplatform = "sh4"

config.plugins.mc_favorites = ConfigSubsection()
config.plugins.mc_favorites.foldercount = ConfigInteger(0)
config.plugins.mc_favorites.folders = ConfigSubList()

config.plugins.mc_globalsettings = ConfigSubsection()
config.plugins.mc_globalsettings.language = ConfigSelection(default="EN", choices = [("EN", _("English"))])
config.plugins.mc_globalsettings.showinmainmenu = ConfigYesNo(default=True)
config.plugins.mc_globalsettings.showinextmenu = ConfigYesNo(default=True)
config.plugins.mc_globalsettings.checkforupdate = ConfigYesNo(default=True)
config.plugins.mc_globalsettings.currentversion = ConfigInteger(0, (0, 999))
config.plugins.mc_globalsettings.currentplatform = ConfigText(default = currentmcplatform)

config.plugins.mc_globalsettings.dst_top = ConfigInteger(0, (0, 999))
config.plugins.mc_globalsettings.dst_left = ConfigInteger(0, (0, 999))
config.plugins.mc_globalsettings.dst_width = ConfigInteger(720, (1, 720))
config.plugins.mc_globalsettings.dst_height = ConfigInteger(576, (1, 576))

config.plugins.mc_globalsettings.currentskin = ConfigSubsection()
config.plugins.mc_globalsettings.currentskin.path = ConfigText(default = "default/skin.xml")

config.plugins.mc_globalsettings.currentversion.value = currentmcversion
config.plugins.mc_globalsettings.currentplatform.value = currentmcplatform

from Components.MenuList import MenuList

# Load Skin
from skin import loadSkin
loadSkin("/usr/lib/enigma2/python/Screens/MediaCenter/skins/defaultHD/skin.xml")

import keymapparser
keymapparser.readKeymap("/usr/lib/enigma2/python/Screens/MediaCenter/keymap.xml")

#------------------------------------------------------------------------------------------
def getAspect():
	val = AVSwitch().getAspectRatioSetting()
	return val/2
	
class DMC_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()

	
		list = []
		list.append(("Movies", "DMC_Movies", "menu_movies", "50"))
		list.append(("TV", "InfoBar", "menu_tv", "50"))
		list.append(("Settings", "MC_Settings", "menu_settings", "50"))
		list.append(("Pictures", "MC_PictureViewer", "menu_pictures", "50"))
		list.append(("Music", "MC_AudioPlayer", "menu_music", "50"))
		#list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list, True)

		listWatch = []
		listWatch.append((" ", "dummy", "menu_dummy", "50"))
		listWatch.append(("Movies", "DMC_Movies", "menu_movies", "50"))
		listWatch.append(("Series", "DMC_Series", "menu_series", "50"))
		self["menuWatch"] = List(listWatch, True)
		self.Watch = False

		self["title"] = StaticText("")
		self["welcomemessage"] = StaticText("")

		#self["moveWatchMovies"] = MovingPixmap()
		#self["moveWatchSeries"] = MovingPixmap()

		self.inter = 0

		self["actions"] = HelpableActionMap(self, "DMC_MainMenuActions", 
			{
				"ok": self.okbuttonClick,
				"cancel": self.cancel,
				"left": self.left,
				"right": self.right,
				"up": self.up,
				"down": self.down,
			}, -1)

		
	def okbuttonClick(self):
		print "okbuttonClick"

		if self.Watch == True:
			selection = self["menuWatch"].getCurrent()
			if selection is not None:
				if selection[1] == "DMC_Movies":
					self.session.open(DMC_PosterDemo)
				elif selection[1] == "DMC_Series":
					self.session.open(DMC_Series)
		else:
			selection = self["menu"].getCurrent()
			if selection is not None:
				if selection[1] == "DMC_Movies":
					self["menuWatch"].setIndex(1)
					self.Watch = True;
				elif selection[1] == "MC_AudioPlayer":
					self.session.open(MC_AudioPlayer)
				elif selection[1] == "MC_Settings":
					from Menu import MainMenu, mdom
					menu = mdom.getroot()
					assert menu.tag == "menu", "root element in menu must be 'menu'!"


					self.session.open(MainMenu, menu)
				elif selection[1] == "InfoBar":
					eDVBDB.getInstance().reloadBouquets()
					from Screens.InfoBar import InfoBar
					self.session.open(InfoBar)
				elif selection[1] == "Exit":
					self.Exit()

	def up(self):
		self.cancel()
		return

	def down(self):
		self.okbuttonClick()
		return

	def right(self):
		if self.Watch == True:
			self["menuWatch"].selectNext()
			if self["menuWatch"].getIndex() == 0:
				self["menuWatch"].selectNext()
		else:
			self["menu"].selectNext()

	def left(self):
		if self.Watch == True:
			self["menuWatch"].selectPrevious()
			if self["menuWatch"].getIndex() == 0:
				self["menuWatch"].selectPrevious()
		else:
			self["menu"].selectPrevious()

	def cancel(self):
		if self.Watch == True:
			self["menuWatch"].setIndex(0)
			self.Watch = False;

		return

	def error(self, error):
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)

	def Ok(self):
		self.session.open(MPD_PictureViewer)
		
	def Exit(self):
		self.session.nav.stopService()
		self.session.nav.playService(self.oldService)
		
		self.close()

