# #!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
"""
===============================================================================
 Config - Helper for Enigma2

 This module collects free CCcam lines from various websites and automatically
 converts them into [reader] blocks for use in oscam.server.
 Send emm tu tvsat card

 Features:
 - Fetches data from multiple sources using regular expressions
 - Validates hostnames and ports
 - Automatically generates OSCam reader blocks
 - Backs up the original file if it exists
 - Avoids writing duplicate readers
 - Uses threading to avoid blocking the GUI

 Requirements:
 - Internet access on the device

 Credits: by Lululla
 Date: May 2025
===============================================================================
"""

import base64
import codecs
import re
import ssl
import subprocess
import sys
from os import X_OK, access, chmod, listdir, popen, stat, system
from os.path import dirname, exists, join
from random import choice
from threading import Thread

from enigma import eTimer, getDesktop

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.config import (
	ConfigNumber,
	ConfigPassword,
	ConfigSelection,
	ConfigSubsection,
	ConfigText,
	ConfigYesNo,
	NoSave,
	config,
	getConfigListEntry,
)

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard

from Tools.Directories import SCOPE_PLUGINS, fileExists, resolveFilename

from .. import _, paypal
from ..plugin import currversion, runningcam

global skin_path

sss = "aHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3L0I5N0hDOGll"
PY3 = sys.version_info.major >= 3

if PY3:
	unicode = str
	unichr = chr
	long = int


def b64decoder(s):
	"""Add missing padding to string and return the decoded base64 string."""
	s = str(s).strip()
	try:
		outp = base64.b64decode(s)
		print("outp1 ", outp)
		if PY3:
			outp = outp.decode("utf-8")
			print("outp2 ", outp)
	except TypeError:
		padding = len(s) % 4
		if padding == 1:
			print("Invalid base64 string: {}".format(s))
			return ""
		elif padding == 2:
			s += b"=="
		elif padding == 3:
			s += b"="
		outp = base64.b64decode(s)
		print("outp1 ", outp)
		if PY3:
			outp = outp.decode("utf-8")
			print("outp3 ", outp)
	return outp


# currversion = "2.3"
name_plug = "TiVuStream Softcam Manager"
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager")
data_path = plugin_path + "/data/"
skin_path = plugin_path

try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	pass
else:
	ssl._create_default_https_context = _create_unverified_https_context


def checkStr(txt):
	if PY3:
		if isinstance(type(txt), type(bytes())):
			txt = txt.decode("utf-8")
	else:
		if isinstance(type(txt), type(unicode())):
			txt = txt.encode("utf-8")
	return txt


ListAgent = [
	"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15",
	"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14",
	"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13",
	"Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13",
	"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8",
	"Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1",
	"Mozilla/5.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1",
	"Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.16) Gecko/20120427 Firefox/15.0a1",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1",
	"Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2",
	"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0a2) Gecko/20111101 Firefox/9.0a2",
]


def RequestAgent():
	RandomAgent = choice(ListAgent)
	return RandomAgent


def getUrl(url):
	if sys.version_info.major == 3:
		import urllib.request as urllib2
	elif sys.version_info.major == 2:
		import urllib2
	req = urllib2.Request(url)
	req.add_header(
		"User-Agent",
		"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14")
	r = urllib2.urlopen(req, None, 15)
	link = r.read()
	r.close()
	content = link
	if str(type(content)).find("bytes") != -1:
		try:
			content = content.decode("utf-8")
		except Exception as e:
			print("Error: %s." % str(e))
	return content


# =============== SCREEN PATH SETTING
screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
	skin_path = plugin_path + "/res/skins/uhd/"
elif screenwidth.width() == 1920:
	skin_path = plugin_path + "/res/skins/fhd/"
else:
	skin_path = plugin_path + "/res/skins/hd/"
if exists("/usr/bin/apt-get"):
	skin_path = skin_path + "dreamOs/"


if not exists("/etc/tuxbox/config"):
	system("mkdir /etc/tuxbox/config")


def cccamPath():
	cmd = "find /usr -name CCcam.cfg"
	res = popen(cmd).read()
	if res == "":
		cmd = "find /var -name CCcam.cfg"
		res = popen(cmd).read()
		if res == "":
			cmd = "find /etc -name CCcam.cfg"
			res = popen(cmd).read()
			if res == "":
				try:
					folders = listdir("/etc/tuxbox/")
					for folder in folders:
						if folder.startswith("oscam"):
							cmd = "find /etc/tuxbox/config/" + folder + " -name CCcam.cfg"
							res = popen(cmd).read()
							return "/etc/tuxbox/config/" + folder + "CCcam.cfg"
						if res == "":
							return "/etc/CCcam.cfg"
				except BaseException:
					return "/etc/CCcam.cfg"
			else:
				return "/etc/CCcam.cfg"
		else:
			return "/var/CCcam.cfg"


def findOscam():
	"""Trova tutti i percorsi di oscam.server sul sistema."""
	paths = [
		"/etc/tuxbox/config/oscam/oscam.server",
		"/etc/tuxbox/config/oscam-emu/oscam.server",
		"/etc/tuxbox/config/oscam_atv_free/oscam.server",
		"/etc/tuxbox/config/oscam.server",
		"/etc/tuxbox/config/oscam-stable/oscam.server",
		"/var/tuxbox/config/oscam.server",
		"/etc/tuxbox/config/gcam.server",
		"/etc/tuxbox/config/ncam.server",
		"/etc/tuxbox/config/ncam/ncam.server",
		"/etc/tuxbox/config/supcam-emu/oscam.server",
		"/etc/tuxbox/config/oscamicam/oscam.server",
		"/etc/tuxbox/config/oscamicamnew/oscam.server"
	]
	return paths


def saveFileContent(file_pathx):
	"""Returns the contents of the file if it exists."""
	if exists(file_pathx):
		with open(file_pathx, "r") as f:
			return f.read()
	return ""


def prependToFile(file_pathx):
	"""
	Reads (and creates if necessary) the original backup of the file,
	adding markers to avoid duplication.
	Returns the original content (with markers).
	"""
	directory = dirname(file_pathx)
	if not exists(directory):
		print("DEBUG: Directory non esistente per", file_pathx)
		return ""

	backup_path = file_pathx + "Orig"
	original_content = ""

	if not exists(backup_path) and exists(file_pathx):
		with open(file_pathx, "r") as f:
			original_content = f.read()
		with open(backup_path, "w") as f:
			f.write(original_content)
		print("DEBUG: Creato backup per", file_pathx)
	elif exists(backup_path):
		with open(backup_path, "r") as f:
			original_content = f.read()
		print("DEBUG: Lettura backup esistente per", file_pathx)

	marker_start = "### ORIGINAL START ###"
	marker_end = "### ORIGINAL END ###"
	if marker_start not in original_content:
		original_content = marker_start + "\n" + original_content.strip() + "\n" + \
			marker_end + "\n"
		print("DEBUG: Aggiunti marker al backup per", file_pathx)
	else:
		print("DEBUG: Marker già presenti nel backup per", file_pathx)

	return original_content


def remove_backup_block(content):
	"""
	If the content starts with the backup block (marker),
	removes it and returns only the new content.
	"""
	marker_start = "### ORIGINAL START ###"
	marker_end = "### ORIGINAL END ###"
	if content.startswith(marker_start):
		end_index = content.find(marker_end)
		if end_index != -1:
			# Salta il blocco del backup
			return content[end_index + len(marker_end):].strip()
	return content


def ensure_directory_exists(file_path):
	"""Ensures that the file directory exists; otherwise, creates it."""
	directory = dirname(file_path)
	if not exists(directory):
		return


Serverlive = [
	("aHR0cHM6Ly9ib3NzY2NjYW0uY28vVGVzdC5waHA=", "Server01"),
	("aHR0cHM6Ly9pcHR2LTE1ZGF5cy5ibG9nc3BvdC5jb20=", "Server02"),
	("aHR0cHM6Ly9jY2NhbWlhLmNvbS9mcmVlLWNjY2FtLw==", "Server03"),
	("aHR0cHM6Ly9jY2NhbS5uZXQvZnJlZWNjY2Ft", "Server04"),
	("aHR0cHM6Ly9jY2NhbXNhdGUuY29tL2ZyZWU=", "Server05"),
	("aHR0cHM6Ly9jY2NhbXguY29tL2ZyZWUtY2NjYW0=", "Server06"),
	("aHR0cHM6Ly9jY2NhbS1wcmVtaXVtLmNvL2ZyZWUtY2NjYW0v", "Server07"),
	("aHR0cHM6Ly9jY2NhbWZyZWUuY28vZnJlZS9nZXQucGhw", "Server8"),
	("aHR0cHM6Ly9jY2NhbWlwdHYucHJvL2NjY2FtLWZyZWUvI3BhZ2UtY29udGVudA==", "Server9"),
]


cfgcam = [
	("/etc/CCcam.cfg", "CCcam"),
	("/etc/tuxbox/config/oscam.server", "Oscam"),
	("/etc/tuxbox/config/oscam-emu/oscam.server", "oscam-emu"),
	("/etc/tuxbox/config/ncam.server", "Ncam"),
	("/etc/tuxbox/config/gcam.server", "Gcam"),
	("/etc/tuxbox/config/Oscamicam/oscam.server", "Oscamicam")
]


config.plugins.tvmanager = ConfigSubsection()
config.plugins.tvmanager.active = ConfigYesNo(default=False)
config.plugins.tvmanager.Server = NoSave(
	ConfigSelection(choices=Serverlive))  # , default=Server1))
config.plugins.tvmanager.cfgfile = NoSave(ConfigSelection(choices=cfgcam))
config.plugins.tvmanager.hostaddress = NoSave(ConfigText(default="127.0.0.1"))
config.plugins.tvmanager.port = NoSave(ConfigNumber(default=16000))
config.plugins.tvmanager.user = NoSave(
	ConfigText(
		default="Enter Username",
		visible_width=50,
		fixed_size=False))
config.plugins.tvmanager.passw = NoSave(
	ConfigPassword(
		default="******",
		fixed_size=False,
		censor="*"))

# ===================================================
host = str(config.plugins.tvmanager.hostaddress.value)
port = str(config.plugins.tvmanager.port.value)
user = str(config.plugins.tvmanager.user.value)
password = str(config.plugins.tvmanager.passw.value)


def putlblcfg():
	global rstcfg
	global buttn
	global putlbl
	putlbl = config.plugins.tvmanager.cfgfile.getValue()
	buttn = ""
	if not putlbl:
		print("Error: Invalid file path")
		return None

	path_map = {
		"/etc/CCcam.cfg": ("CCcam", "CCcam.cfg"),
		"/etc/tuxbox/config/oscam.server": ("Oscam", "oscam.server"),
		# "/etc/tuxbox/config/gcam.server": ("Gcam", "gcam.server"),  # eventualmente da riabilitare
		"/etc/tuxbox/config/oscam-emu/oscam.server": ("OscamEmu", "oscam.server"),
		"/etc/tuxbox/config/Oscamicam/oscam.server": ("Oscamicam", "oscam.server"),
		"/etc/tuxbox/config/ncam.server": ("Ncam", "ncam.server"),
	}

	if putlbl in path_map:
		buttn = _("Write") + " " + path_map[putlbl][0]
		rstcfg = path_map[putlbl][1]
	else:
		buttn = _("Write") + " NONE"
		rstcfg = "unknow.server"
		return None

	return putlbl


putlblcfg()
print("putlblcfg start")
print("putlbl ==========", putlbl)
print("rstcfg ==========", rstcfg)
print("rstcfg ==========", buttn)
print("putlblcfg end")


class tv_config(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		skin = join(skin_path, "tv_config.xml")
		with codecs.open(skin, "r", encoding="utf-8") as f:
			self.skin = f.read()
		self.setup_title = (name_plug)
		self["title"] = Label(_(name_plug))
		self["key_red"] = Label("")
		self["key_green"] = Label("")
		self["key_yellow"] = Label("")
		self["key_blue"] = Label("")
		self["description"] = Label("")
		self["info"] = Label(_("Wait please..."))
		self.onChangedEntry = []
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
		self["paypal"] = Label()
		self["actions"] = ActionMap(
			[
				"InfobarEPGActions",
				"OkCancelActions",
				"HotkeyActions",
				"VirtualKeyboardActions",
				"ColorActions",
				"MenuActions"
			],
			{
				"left": self.keyLeft,
				"right": self.keyRight,
				"ok": self.closex,
				"showVirtualKeyboard": self.KeyText,
				"green": self.green,
				"yellow": self.sendemm,
				"blue": self.resetcfg,
				"red": self.oscamAu,  # closex,
				"cancel": self.closex,
				"info": self.infomsg,
				"back": self.closex
			},
			-1
		)
		self.createSetup()
		if self.selectionChanged not in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)
		payp = paypal()
		self["paypal"].setText(payp)
		self["info"].setText(_("Select Your Choice"))
		self["description"].setText(_("MENU EMM / SERVER CLINE"))

	def infomsg(self):
		self.session.open(MessageBox, _("Softcam Manager by Lululla\nV.%s\nInstall Cam Software\nForum Support www.corvoboys.org\n") % currversion,	 MessageBox.TYPE_INFO, timeout=4)

	def oscamAu(self, answer=False):

		if answer:
			def status_callback(msg):
				print("[CCcamCollector] {}".format(msg))

			def run_collector_thread():
				try:
					from .MyCCcamCollector import MyCCcamCollector
					collector = MyCCcamCollector(putlbl)
					collector.run(status_callback=status_callback)
				except Exception as e:
					print("error:{}".format(e))

					def show_error(err=e):
						self.session.open(MessageBox, "Error downloading CCcam data:\n{}".format(err), MessageBox.TYPE_ERROR)

					self.timer = eTimer()
					if exists("/usr/bin/apt-get"):
						self.timer_conn = self.timer.timeout.connect(show_error)
					else:
						self.timer.callback.append(show_error)
					self.timer.start(0, True)
					return

				def show_success():
					name = "Oscam" if "oscam" in putlbl.lower() else "CCcam"
					message = "{} config saved to:\n{}".format(name, putlbl)
					self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

				self.timer = eTimer()
				if exists("/usr/bin/apt-get"):
					self.timer_conn = self.timer.timeout.connect(show_success)
				else:
					self.timer.callback.append(show_success)
				self.timer.start(0, True)

			Thread(target=run_collector_thread).start()

		else:
			self.session.openWithCallback(
				self.oscamAu,
				MessageBox,
				"Do you want to automatically download CCcam readers?\nThey will be saved to:\n{}".format(putlbl),
				MessageBox.TYPE_YESNO
			)

	def sendemm(self):
		if config.plugins.tvmanager.active.value:
			self.getcl()
		else:
			try:
				print("datas runningcam=", runningcam)

				def execute_command(choice):
					if choice:
						if "oscam" in runningcam.lower():
							# cmd = "ps aux | grep -i '[o]scam'"
							# res = subprocess.getoutput(cmd)
							res = ""
							msg = []
							cmd = ["ps"]
							output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
							stdout, stderr = output.communicate()

							if output.returncode == 0:
								res = "\n".join(line for line in stdout.decode("utf-8").split("\n") if "oscam" in line.lower())
								print("execute_command res ps:", res)
							else:
								print("Error:", stderr.decode("utf-8"))

							if any(cam in res.lower() for cam in ["oscam", "icam", "ncam", "gcam"]):
								print("oscam exist")
								msg.append(_("\n....\n.....\n"))
								self.cmd1 = "/usr/lib/enigma2/python/Plugins/Extensions/tvManager/data/emm_sender.sh"
								if not access(self.cmd1, X_OK):
									chmod(self.cmd1, 493)

								def run_command():
									subprocess.run(self.cmd1, shell=True)

								thread = Thread(target=run_command)
								thread.start()

							if exists("/tmp/emm.txt"):
								print("EMM file exists!")
								with open("/tmp/emm.txt") as f:
									file_content = f.read().strip()
									msg.append("CURRENT EMM IS:\n")
									msg.append(file_content)
									msg.append("\nCurrent Emm saved to /tmp/emm.txt")
									msg = (" %s " % _("\n")).join(msg)
									print("DEBUG: msg_output =", msg)
								self.session.open(MessageBox, _("Please wait, %s.") % msg, MessageBox.TYPE_INFO, timeout=10)

				self.session.openWithCallback(execute_command, MessageBox, _("Do you want to execute the command?"), MessageBox.TYPE_YESNO)
			except Exception as e:
				print("error on emm", str(e))

	def callMyMsg(self, answer=False):
		if answer:
			self.cmd1 = "/usr/lib/enigma2/python/Plugins/Extensions/tvManager/data/emm_sender.sh"
			if not access(self.cmd1, X_OK):
				chmod(self.cmd1, 493)

			def run_command():
				subprocess.run(self.cmd1, shell=True)

			thread = Thread(target=run_command)
			thread.start()
		else:
			self.session.open(MessageBox, _("Command Cancelled"), MessageBox.TYPE_INFO, timeout=5)

	def closex(self):
		self.close()

	def resetcfg(self):
		if config.plugins.tvmanager.active.value is True:
			import shutil
			shutil.copy2(data_path + rstcfg, putlbl)
			system("chmod -R 755 %s" % putlbl)
			self.session.open(MessageBox, _("Reset") + " " + putlbl, type=MessageBox.TYPE_INFO, timeout=8)

	def showhide(self):
		if config.plugins.tvmanager.active.value is True:
			self["key_red"].setText(_("xLine"))
			self["key_green"].setText(buttn)
			self["key_yellow"].setText(_("Get Link"))
			self["key_blue"].setText(_("Reset"))
		else:
			self["key_red"].setText("")
			self["key_green"].setText("")
			self["key_yellow"].setText(_("Check Emm Send"))
			self["key_blue"].setText("")
		return

	def showInfo(self, info):
		self.session.openWithCallback(self.workingFinished, InfoScreen, info)

	def workingFinished(self, callback=None):
		self.working = False

	def check_output(self, result, retval, extra_args):
		if retval == 0:
			self.showInfo(result)
		else:
			self.showInfo(str(result))

	def green(self):
		try:
			if config.plugins.tvmanager.active.value is True:
				if putlbl == "/etc/CCcam.cfg":
					self.CCcam()
				elif putlbl in [
					"/etc/tuxbox/config/oscam.server",
					"/etc/tuxbox/config/oscam-emu/oscam.server",
					"/etc/tuxbox/config/Oscamicam/oscam.server"
				]:
					self.Oscam()
				elif putlbl == "/etc/tuxbox/config/ncam.server":
					self.Ncam()
				else:
					return
		except Exception as e:
			print("Error in green function:", str(e))
			self.session.open(MessageBox, _("An error occurred in the green function."), MessageBox.TYPE_ERROR, timeout=5)

	def createSetup(self):
		self.editListEntry = None
		self.list = []
		self.list.append(getConfigListEntry(_("Activate Insert line in Config File:"), config.plugins.tvmanager.active, _("If Active: Download/Reset Server Config")))
		if config.plugins.tvmanager.active.value:
			self.list.append(getConfigListEntry(_("Server Config"), config.plugins.tvmanager.cfgfile, putlbl))
			self.list.append(getConfigListEntry(_("Server Link"), config.plugins.tvmanager.Server, _("Select Get Link")))
			self.list.append(getConfigListEntry(_("Server URL"), config.plugins.tvmanager.hostaddress, _("Server Url i.e. 012.345.678.900")))
			self.list.append(getConfigListEntry(_("Server Port"), config.plugins.tvmanager.port, _("Port")))
			self.list.append(getConfigListEntry(_("Server Username"), config.plugins.tvmanager.user, _("Username")))
			self.list.append(getConfigListEntry(_("Server Password"), config.plugins.tvmanager.passw, _("Password")))
			self["key_green"].setText(buttn)
			self["key_yellow"].setText(_("Get Link"))
			self["key_blue"].setText(_("Reset"))

		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self.showhide()

	def KeyText(self):
		sel = self["config"].getCurrent()
		if sel:
			self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].value)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		print("current selection:", self["config"].l.getCurrentSelection())
		putlblcfg()
		self.createSetup()
		self.getcl()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		print("current selection:", self["config"].l.getCurrentSelection())
		putlblcfg()
		self.createSetup()
		self.getcl()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.createSetup()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.createSetup()

	def VirtualKeyBoardCallback(self, callback=None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].value = callback
			self["config"].invalidate(self["config"].getCurrent())
		return

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def selectionChanged(self):
		self.showhide()

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		self.selectionChanged()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def CCcam(self):
		global host, port, user, passw
		putlblcfg()
		print("putlblcfg CCcam ===================", putlbl)
		if "CCcam.cfg" not in putlbl:
			self.session.open(MessageBox, _("Select CCcam"), type=MessageBox.TYPE_INFO, timeout=5)
			return

		if config.plugins.tvmanager.cfgfile.value != "/etc/CCcam.cfg":
			self.session.open(MessageBox, _("Select CCcam"), type=MessageBox.TYPE_INFO, timeout=5)
			return
		dest = config.plugins.tvmanager.cfgfile.value
		host = "C: " + str(config.plugins.tvmanager.hostaddress.value)
		port = str(config.plugins.tvmanager.port.value)
		user = str(config.plugins.tvmanager.user.value)
		passw = str(config.plugins.tvmanager.passw.value)

		if fileExists("/etc/CCcam.cfg"):
			dest = "/etc/CCcam.cfg"
		else:
			self.session.open(MessageBox, _("Please Reset - No File CFG"), type=MessageBox.TYPE_INFO, timeout=5)
			return
		system("chmod -R 755 %s" % dest)
		cfgdok = open(dest, "a")
		cfgdok.write("\n\n" + host + " " + port + " " + user + " " + passw)
		cfgdok.close()
		self.session.open(MessageBox, _("Server Copy in ") + dest, type=MessageBox.TYPE_INFO, timeout=8)

	def Oscam(self):
		global host, port, user
		putlblcfg()
		print("putlbl Oscam ===================", putlbl)
		if "oscam.server" not in putlbl:
			self.session.open(MessageBox, _("Select OScam"), type=MessageBox.TYPE_INFO, timeout=5)
			return

		dest = config.plugins.tvmanager.cfgfile.value
		host = str(config.plugins.tvmanager.hostaddress.value)
		port = str(config.plugins.tvmanager.port.value)
		user = str(config.plugins.tvmanager.user.value)
		passw = str(config.plugins.tvmanager.passw.value)
		if not fileExists(dest):
			self.session.open(MessageBox, _("Please Reset - No File CFG"), type=MessageBox.TYPE_INFO, timeout=5)
			return
		system("chmod -R 755 %s" % dest)
		cfgdok = open(dest, "a")
		cfgdok.write("\n[reader]\nlabel = Server_" + host + "\nenable= 1\nprotocol = cccam\ndevice = " + host + "," + port + "\nuser = " + user + "\npassword = " + passw + "\ninactivitytimeout = 30\ngroup = 3\ncccversion = 2.2.1\ncccmaxhops = 0\nccckeepalive = 1\naudisabled = 1\n\n")
		cfgdok.close()
		self.session.open(MessageBox, _("Server Copy in ") + dest, type=MessageBox.TYPE_INFO, timeout=8)

	def Ncam(self):
		global host, port, user, passw
		putlblcfg()
		print("putlbl Oscam ===================", putlbl)
		if "ncam.server" not in putlbl:
			self.session.open(MessageBox, _("Select Ncam"), type=MessageBox.TYPE_INFO, timeout=5)
			return

		if not exists("/etc/tuxbox/config"):
			system("mkdir /etc/tuxbox/config")
		dest = config.plugins.tvmanager.cfgfile.value
		host = str(config.plugins.tvmanager.hostaddress.value)
		port = str(config.plugins.tvmanager.port.value)
		user = str(config.plugins.tvmanager.user.value)
		passw = str(config.plugins.tvmanager.passw.value)
		if fileExists("/etc/tuxbox/config/ncam.server"):
			dest = "/etc/tuxbox/config/ncam.server"
		else:
			self.session.open(MessageBox, _("Please Reset - No File CFG"), type=MessageBox.TYPE_INFO, timeout=5)
			return
		system("chmod -R 755 %s" % dest)
		cfgdok = open(dest, "a")
		cfgdok.write("\n[reader]\nlabel = Server_" + host + "\nenable= 1\nprotocol = cccam\ndevice = " + host + "," + port + "\nuser = " + user + "\npassword = " + passw + "\ngroup = 3\ncccversion = 2.0.11\ndisablecrccws_only_for= 0500:032830\ncccmaxhops= 1\nccckeepalive= 1\naudisabled = 1\n\n")
		cfgdok.close()
		self.session.open(MessageBox, _("Server Copy in ") + dest, type=MessageBox.TYPE_INFO, timeout=8)

	def getcl(self):
		try:
			data1 = str(config.plugins.tvmanager.Server.value)
			data = b64decoder(data1)
			try:
				data = getUrl(data)
				if PY3:
					import six
					data = six.ensure_str(data)
				self.timer = eTimer()
				if exists("/usr/bin/apt-get"):
					self.timer_conn = self.timer.timeout.connect(self.load_getcl(data))
				else:
					self.timer.callback.append(self.load_getcl(data))
				self.timer.start(600, 1)
			except Exception as e:
				print("getcl error: ", str(e))
		except Exception as e:
			print("error on host", str(e))

	def load_getcl(self, data):
		global host, port, user
		try:
			data = checkStr(data)
			url1 = re.findall(r"<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*", data)

			if "bosscccam" in data.lower():
				url1 = re.findall(r"<strong>c:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</strong", data)

			# <h3 class="elementor-heading-title elementor-size-default">C: free.cccamx.com 18804 Trial978532 89390137</h3>
			elif "cccamx" in data.lower():
				url1 = re.findall(r'">C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</h3>', data)

			elif '15days' in data.lower():
				url1 = re.findall(r'">C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</th></tr>', data)

			elif 'cccamia' in data:
				url1 = re.findall(r'>?C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)

			elif 'cccam.net/freecccam' in data.lower():
				url1 = re.findall(r'b>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)', data)

			elif 'testcline' in data.lower():
				url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</d', data)

			# <div id="cline">C: free.cccamiptv.club 13000 ggd32x cccamiptv.pro</div>
			elif 'cccamiptv' in data.lower():
				url1 = re.findall(r'cline">\s*C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)

			elif 'free.cccam.net' in data.lower():
				url1 = re.findall(r'<b>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</b>', data)

			elif 'cccam-premium.co' in data.lower():
				url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)', data)

			elif 'cccamsate' in data.lower():
				url1 = re.findall(r'<span><b>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</b>', data)

			elif 'cccameagle' in data.lower():
				url1 = re.findall(r'>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</h2>', data)

			elif 'cccamprime' in data.lower():
				url1 = re.findall(r'Cline : C:\s+(.*?)\s+(\d+)\s+(\w+)\s+(.*?)\s*Host', data)
				url1 = url1.replace('<br><br>', '')

			elif 'cccampri.me' in data.lower():
				# url1 = re.findall(r'Cline : C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)<br>', data)
				url1 = re.findall(r'line : C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)<br\s*/?>', data)

			elif 'iptvcccam' in data.lower():
				url1 = re.findall(r'?C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</h1>', data)

			elif 'cccameurop' in data.lower():
				url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s*</', data)

			elif 'infosat' in data.lower():
				# url1 = re.findall('host: (.+?)<br> port: (.+?) <br>.*?user:(.+?)<br>.*?pass: (.+?)\n', data)
				url1 = re.findall(r'host:\s*(.+?)<br\s*/?>\s*port:\s*(.+?)<br\s*/?>\s*user:\s*(.+?)<br\s*/?>\s*pass:\s*(.+?)\s*\n', data)

			# elif 'history' in data.lower():
				# # url1 = re.findall('of the line">C: (.+?) (.+?) (.+?) (.+?)</a>.*?title=', data)
				# url1 = re.findall(r'of the line">C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</a>.*?title=', data)

			# elif 'store' in data.lower():
				# # url1 = re.findall('<center><strong>C: (.+?) (.+?) (.+?) (.+?) <br>', data)
				# url1 = re.findall(r'<center><strong>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*<br>', data)

			# elif 'cccamhub' in data.lower():
				# url1 = re.findall(r'id="cline">.*?C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</div>', data)

			elif 'rogcam' in data.lower():
				url1 = re.findall(r'?C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</span>', data)

			# elif 'cccambird' in data.lower():
				# url1 = re.findall(r'>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</th>', data)

			else:
				url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)
			print("===========data=========", url1)

			if url1 != "":
				host = ""
				port = ""
				user = ""
				password = ""
				if "cccameurop" in data.lower():
					for u, pw in url1:
						# url1 = "cccameurop.com 19000" + url1[0] + url1[1]
						host = "cccameurop.com"
						port = "19000"
						user = str(u)
						password = str(pw)
						print("Host: %s - Port: %s - User: %s - Password: %s" % (host, port, user, password))
				else:
					for h, p, u, pw in url1:
						print(h, p, u, pw)
						host = str(h)
						port = str(p)
						user = str(u)
						password = str(pw)
						password = password.replace("</h1>", "").replace("</b>", "")
						password = password.replace("</div>", "").replace("</span>", "")
				# if config.plugins.tvmanager.active.getValue():
				config.plugins.tvmanager.hostaddress.setValue(host)
				config.plugins.tvmanager.port.setValue(port)
				config.plugins.tvmanager.user.setValue(user)
				config.plugins.tvmanager.passw.setValue(password)
				self.createSetup()
			else:
				return
		except Exception as e:
			print("error on string cline", str(e))

	def readCurrent(self):
		currCam = None
		self.FilCurr = ""
		if fileExists("/etc/CurrentBhCamName"):
			self.FilCurr = "/etc/CurrentBhCamName"
		else:
			self.FilCurr = "/etc/clist.list"
		if stat(self.FilCurr).st_size > 0:
			try:
				if sys.version_info[0] == 3:
					clist = open(self.FilCurr, "r", encoding="UTF-8")
				else:
					clist = open(self.FilCurr, "r")
			except:
				return
			if clist is not None:
				for line in clist:
					currCam = line
				clist.close()
		return currCam


if screenwidth.width() > 1200:
	InfoScreenx = """
	<screen position="center,center" size="800,620" title="CCcam Info">
		<widget name="text" position="0,0" size="800,620" font="Regular; 30" />
	</screen>"""
else:
	InfoScreenx = """
	<screen position="center,center" size="500,420" title="CCcam Info" >
		<widget name="text" position="0,0" size="500,420" font="Regular;20" />
	</screen>"""


class InfoScreen(Screen):

	def __init__(self, session, info):
		Screen.__init__(self, session)
		self.skin = InfoScreenx
		self.setTitle(_("Emm Info"))
		from Components.ScrollLabel import ScrollLabel
		self["text"] = ScrollLabel(info)
		self["actions"] = ActionMap(
			["OkCancelActions"],
			{
				"ok": self.close,
				"cancel": self.close,
				"up": self["text"].pageUp,
				"down": self["text"].pageDown,
				"left": self["text"].pageUp,
				"right": self["text"].pageDown,
			},
			-1
		)
