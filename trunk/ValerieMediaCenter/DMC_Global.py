# -*- coding: utf-8 -*-

from   os import makedirs, environ, popen, system
import sys
import traceback

from Components.config import config

from DataElement import DataElement

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

def getAPILevel(parent):
	APILevel = 1
	try:
		APILevel = int(DataElement().getDataPreloading(parent, "API"))
	except Exception, ex:
		printl("Exception(" + str(type(ex)) + "): " + str(ex), __name__, "E")
		APILevel = 1
	return APILevel

#------------------------------------------------------------------------------------------

def getBoxtype():
	file = open("/proc/stb/info/model", "r")
	box = file.readline().strip()
	file.close()
	manu = "Unknown"
	model = box #"UNKNOWN" # Fallback to internal string
	arch = "sh4" # "unk" # Its better so set the arch by default to unkown so no wrong updateinformation will be displayed
	version = ""
	if box == "ufs910":
		manu = "Kathrein"
		model = "UFS-910"
		arch = "sh4"
	elif box == "ufs912":
		manu = "Kathrein"
		model = "UFS-912"
		arch = "sh4"
	elif box == "ufs922":
		manu = "Kathrein"
		model = "UFS-922"
		arch = "sh4"
	elif box == "tf7700hdpvr":
		manu = "Topfield"
		model = "HDPVR-7700"
		arch = "sh4"
	elif box == "dm800":
		manu = "Dreambox"
		model = "800"
		arch = "mipsel"
	elif box == "dm800se":
		manu = "Dreambox"
		model = "800se"
		arch = "mipsel"
	elif box == "dm8000":
		manu = "Dreambox"
		model = "8000"
		arch = "mipsel"
	elif box == "dm500hd":
		manu = "Dreambox"
		model = "500hd"
		arch = "mipsel"
	elif box == "elite":
		manu = "Azbox"
		model = "Elite"
		arch = "mipsel"
	elif box == "premium":
		manu = "Azbox"
		model = "Premium"
		arch = "mipsel"
	elif box == "premium+":
		manu = "Azbox"
		model = "Premium+"
		arch = "mipsel"
	elif box == "cuberevo-mini":
		manu = "Cubarevo"
		model = "Mini"
		arch = "sh4"
	elif box == "hdbox":
		manu = "Fortis"
		model = "HdBox"
		arch = "sh4"
	
	if arch == "mipsel":
		file = open(config.plugins.pvmc.pluginfolderpath.value + "oe.txt", "r")
		version = file.readline().strip()
		file.close()
	
	return (manu, model, arch, version)
	
#------------------------------------------------------------------------------------------

class Showiframe():
	def __init__(self):
		try:
			self.load()
		except Exception, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")

	def load(self):
		sys.path.append(config.plugins.pvmc.pluginfolderpath.value + "prebuild")
		#printl("SYS.PATH=" + str(sys.path), self, "D")
		try:
			self.ctypes = __import__("_ctypes")
		except Exception, ex:
			printl("self.ctypes import failed", self, "E")
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
			self.ctypes = None
			return False
		
		libname = "libshowiframe.so.0.0.0"
		if getBoxtype()[0] == "Azbox":
			libname = "libshowiframe.az.so.0.0.0"
		
		printl("LIB_PATH=" + str(config.plugins.pvmc.pluginfolderpath.value) + libname, self, "D")
		self.showiframe = self.ctypes.dlopen(config.plugins.pvmc.pluginfolderpath.value + libname)
		try:
			self.showSinglePic = self.ctypes.dlsym(self.showiframe, "showSinglePic")
			self.finishShowSinglePic = self.ctypes.dlsym(self.showiframe, "finishShowSinglePic")
		except Exception, ex: 
			printl("self.ctypes.dlsym - FAILED!!!", self, "W")
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
			try:
				self.showSinglePic = self.ctypes.dlsym(self.showiframe, "_Z13showSinglePicPKc")
				self.finishShowSinglePic = self.ctypes.dlsym(self.showiframe, "_Z19finishShowSinglePicv")
			except Exception, ex2: 
				printl("self.ctypes.dlsym - FAILED AGAIN !!!", self, "E")
				printl("Exception(" + str(type(ex2)) + "): " + str(ex2), self, "E")
				return False
		return True

	def  showStillpicture(self, pic):
		if self.ctypes is not None:
			self.ctypes.call_function(self.showSinglePic, (pic, ))

	def finishStillPicture(self):
		if self.ctypes is not None:
			self.ctypes.call_function(self.finishShowSinglePic, ())
			#dlclose(self.showiframe)

#------------------------------------------------------------------------------------------

class E2Control():
	def __init__(self):
		printl("->", self)
		
		try:
			makedirs("/hdd/valerie")
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		try:
			makedirs("/hdd/valerie/episodes")
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		try:
			makedirs("/hdd/valerie/media")
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		
		self.close()
		
		box = getBoxtype()
		environ['BOXSYSTEM'] = "MANUFACTOR="+box[0]+";MODEL="+box[1]+";"
		s = config.plugins.pvmc.pluginfolderpath.value + "e2control"
		printl(s, self, "D")
		try:
			system("chmod 777 " + s)
			popen(s)
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		
		printl("<-", self)

	def close(self):
		printl("->", self)
		s = config.plugins.pvmc.pluginfolderpath.value + "e2control stop"
		printl(s, self, "D")
		try:
			popen(s)
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		printl("<-", self)
