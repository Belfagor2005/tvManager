#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#--------------------#
#  coded by Lululla  #
#   skin by MMark    #
#     update to      #
#     23/10/2021     #
#--------------------#
from __future__ import print_function
from . import _
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.FileList import FileList
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
# from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.PluginBrowser import PluginBrowser
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from ServiceReference import ServiceReference
from Tools import Notifications
from Tools.BoundFunction import boundFunction
from Tools.Directories import *
from Tools.Directories import fileExists, copyfile
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from os import path, listdir, remove, mkdir, chmod, walk
# from skin import loadSkin
from twisted.web.client import getPage
from xml.dom import Node, minidom
import base64
import os, sys, time, re
import ssl
import glob
import six
from time import sleep
from random import choice
from enigma import getDesktop, gFont, eListboxPythonMultiContent, eTimer, ePicLoad, loadPNG, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from Plugins.Extensions.tvManager.data.GetEcmInfo import GetEcmInfo
from sys import version_info
#======================================================
global active
active = False

from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
from six.moves.urllib.error import HTTPError, URLError
from six.moves.urllib.request import urlretrieve

global FTP_XML
currversion = '1.7'
name_plug = 'TiVuStream Softcam Manager'
title_plug = '..:: ' + name_plug + ' V. %s ::..' % currversion

plugin_path = os.path.dirname(sys.modules[__name__].__file__)
res_plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/")
iconpic = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/{}".format('logo.png'))
data_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/data")
FTP_XML = 'http://patbuweb.com/tvManager/tvManager.xml'
FTP_CFG = 'http://patbuweb.com/tvManager/cfg.txt'
HD = getDesktop(0).size()
keys = '/usr/keys'
camscript = '/usr/camscript'
ECM_INFO = '/tmp/ecm.info'
EMPTY_ECM_INFO = ('', '0', '0', '0')
old_ecm_time = time.time()
info = {}
ecm = ''
data = EMPTY_ECM_INFO
SOFTCAM = 0
CCCAMINFO = 1
OSCAMINFO = 2

ListAgent = [
          'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15',
          'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14',
          'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
          'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1284.0 Safari/537.13',
          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8',
          'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
          'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
          'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
          'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2',
          'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.16) Gecko/20120427 Firefox/15.0a1',
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1',
          'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2',
          'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0a2) Gecko/20111101 Firefox/9.0a2',
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110613 Firefox/6.0a2',
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110612 Firefox/6.0a2',
          'Mozilla/5.0 (Windows NT 6.1; rv:6.0) Gecko/20110814 Firefox/6.0',
          'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)',
          'Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
          'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)',
          'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0;  it-IT)',
          'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US)'
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/13.0.782.215)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/11.0.696.57)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0) chromeframe/10.0.648.205',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.1; SV1; .NET CLR 2.8.52393; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; chromeframe/11.0.696.57)',
          'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/4.0; GTB7.4; InfoPath.3; SV1; .NET CLR 3.1.76908; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; InfoPath.1; SV1; .NET CLR 3.8.36217; WOW64; en-US)',
          'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
          'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; it-IT)',
          'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
          'Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02',
          'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
          'Opera/9.80 (Windows NT 5.1; U; zh-sg) Presto/2.9.181 Version/12.00',
          'Opera/12.0(Windows NT 5.2;U;en)Presto/22.9.168 Version/12.00',
          'Opera/12.0(Windows NT 5.1;U;en)Presto/22.9.168 Version/12.00',
          'Mozilla/5.0 (Windows NT 5.1) Gecko/20100101 Firefox/14.0 Opera/12.0',
          'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10',
          'Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3'
          ]

def RequestAgent():
    RandomAgent = choice(ListAgent)
    return RandomAgent

def __createdir(list):
    dir = ''
    for line in list[1:].split('/'):
        dir += '/' + line
        if not os.path.exists(dir):
            try:
                mkdir(dir)
            except:
                print('Mkdir Failed', dir)

def checkStr(txt):
    if six.PY3:
        if isinstance(txt, type(bytes())):
            txt = txt.decode('utf-8')
    else:
        if isinstance(txt, type(six.text_type())):
            txt = txt.encode('utf-8')
    return txt

def checkdir():
    if not os.path.exists(keys):
        __createdir('/usr/keys')
    if not os.path.exists(camscript):
        __createdir('/usr/camscript')
checkdir()

def readCurrent_1():
    currCam = ''
    FilCurr = ''
    if fileExists('/etc/CurrentBhCamName'):
        FilCurr = '/etc/CurrentBhCamName'
    else:
        FilCurr = '/etc/clist.list'
    try:
        clist = open(FilCurr, 'r')
    except:
        return
    if clist is not None:
        for line in clist:
            currCam = line
        clist.close()
    return currCam

#=============== SCREEN PATH SETTING
HD = getDesktop(0).size()
if HD.width() > 1280:
    skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/skins/fhd/")
else:
    skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/skins/hd/")
if os.path.isfile('/var/lib/dpkg/status'):
    skin_path=skin_path + 'dreamOs/'

def show_list(h):
    png1 = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/img/{}".format('actcam.png'))
    png2 = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/img/{}".format('defcam.png'))
    cond = readCurrent_1()
    if HD.width() > 1280:
        res = [h]
        if cond == h:
            active = True
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(43, 24), png=loadPNG(png1)))
            res.append(MultiContentEntryText(pos=(70, 3), size=(800, 48), font=8, text=h + ' (Active)', color=11403008, flags=RT_HALIGN_LEFT))
        else:
            res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(43, 24), png=loadPNG(png2)))
            res.append(MultiContentEntryText(pos=(70, 3), size=(800, 48), font=8, text=h, flags=RT_HALIGN_LEFT))
        return res
    else:
        res = [h]
        if cond == h:
            active = True
            res.append(MultiContentEntryText(pos=(70, 4), size=(406, 40), font=4, text=h + ' (Active)', color=11403008, flags=RT_HALIGN_LEFT))
            res.append(MultiContentEntryPixmapAlphaTest(pos=(2, 8), size=(43, 24), png=loadPNG(png1)))
        else:
            res.append(MultiContentEntryText(pos=(70, 4), size=(406, 40), font=4, text=h, flags=RT_HALIGN_LEFT))
            res.append(MultiContentEntryPixmapAlphaTest(pos=(2, 8), size=(43, 24), png=loadPNG(png2)))
        return res

def showlist(datal, list):
    icount = 0
    plist = []
    for line in datal:
        name = datal[icount]
        plist.append(show_list_1(name))
        icount = icount + 1
        list.setList(plist)

def show_list_1(h):
    if HD.width() > 1280:
        res = [h]
        res.append(MultiContentEntryText(pos=(2, 2), size=(670, 40), font=8, text=h, flags=RT_HALIGN_LEFT))
    else:
        res = [h]
        res.append(MultiContentEntryText(pos=(2, 2), size=(660, 30), font=3, text=h, flags=RT_HALIGN_LEFT))
    return res

def getUrl(url):
        link = []
        print(  "Here in getUrl url =", url)
        req = Request(url)
        req.add_header('User-Agent',RequestAgent())
        try:
           response = urlopen(req)
           link=response.read()
           response.close()
           return link
        except:
           import ssl
           gcontext = ssl._create_unverified_context()
           response = urlopen(req, context=gcontext)
           link=response.read()
           response.close()
           return link

class m2list(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 16))
        self.l.setFont(1, gFont('Regular', 20))
        self.l.setFont(2, gFont('Regular', 22))
        self.l.setFont(3, gFont('Regular', 24))
        self.l.setFont(4, gFont('Regular', 26))
        self.l.setFont(5, gFont('Regular', 28))
        self.l.setFont(6, gFont('Regular', 30))
        self.l.setFont(7, gFont('Regular', 32))
        self.l.setFont(8, gFont('Regular', 34))
        if HD.width() > 1280:
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(45)

#======================================================
class tvManager(Screen):
    def __init__(self, session, args = False):
    # def __init__(self, session, args = 0):
        self.session = session
        skin = skin_path + '/tvManager.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.index = 0
        self.emulist = []
        self.namelist = []
        self.softcamslist = []
        self.ecminfo = GetEcmInfo()
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        except:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'SetupActions',
         'MenuActions',
         'NumberActions'], {'ok': self.action,
         'cancel': self.close,
         '0': self.messagekd,
         '1': self.cccam,
         '2': self.oscam,
         'menu': self.configtv,
         'blue': self.Blue,
         'yellow': self.download,
         'green': self.action,
         'info': self.CfgInfo,
         'red': self.stop}, -1)
        self.setTitle(_(title_plug))
        self['title'] = Label(_(title_plug))
        self['key_green'] = Button(_('Start'))
        self['key_yellow'] = Button(_('Download'))
        self['key_red'] = Button(_('Stop'))
        self['key_blue'] = Button(_('Softcam'))
        self['desc'] = Label()
        self['desc'].setText(_('Scanning and retrieval list softcam ...'))
        self['info'] = Label('')
        self['list'] = m2list([])
        self.currCam = self.readCurrent()
        self.readScripts()
        self.BlueAction = SOFTCAM
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.cgdesc)
        except:
            self.timer.callback.append(self.cgdesc)
        self.timer.start(500, 1)
        self.EcmInfoPollTimer = eTimer()
        try:
            self.EcmInfoPollTimer_conn = self.EcmInfoPollTimer.timeout.connect(self.setEcmInfo)
        except:
            self.EcmInfoPollTimer.callback.append(self.setEcmInfo)
        self.EcmInfoPollTimer.start(200)
        self.onShown.append(self.ecm)
        self.onShown.append(self.setBlueKey)
        self.onHide.append(self.stopEcmInfoPollTimer)

    def setBlueKey(self):
        if  self.currCam == 'no':
            self["key_blue"].setText(_("Softcam"))
        if self.currCam is not None:
            print('self.currCam: ', self.currCam)
            if 'ccam' in self.currCam.lower():
                if os.path.exists (resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo")):
                    self.BlueAction = CCCAMINFO
                    self["key_blue"].setText(_("CCcamInfo"))
            elif 'oscam' in self.currCam.lower():
                if os.path.exists (resolveFilename(SCOPE_PLUGINS, "Extensions/OscamStatus")):
                    self.BlueAction = OSCAMINFO
                    self["key_blue"].setText(_("OscamInfo"))
            else:
                self.BlueAction = SOFTCAM
                self["key_blue"].setText(_("SOFTCAM"))
        else:
            self.BlueAction = SOFTCAM
            self["key_blue"].setText(_("SOFTCAM"))

    def ShowSoftcamCallback(self):
        pass

    def Blue(self):
        if self.BlueAction == CCCAMINFO:
            if os.path.exists (resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo")):
                from Plugins.Extensions.CCcamInfo.plugin import CCcamInfoMain
                self.session.openWithCallback(self.ShowSoftcamCallback, CCcamInfoMain)
        elif self.BlueAction == OSCAMINFO:
            if os.path.exists (resolveFilename(SCOPE_PLUGINS, "Extensions/OscamStatus")):
                from Plugins.Extensions.OscamStatus.plugin import OscamStatus
                self.session.openWithCallback(self.ShowSoftcamCallback, OscamStatus)
        else:
            self.BlueAction == SOFTCAM
            self.messagekd()

    def cccam(self):
        if 'ccam' in self.currCam.lower()and self.currCam != 'no':
            if os.path.exists (resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo")):
                from Plugins.Extensions.CCcamInfo.plugin import CCcamInfoMain
                self.session.openWithCallback(self.ShowSoftcamCallback, CCcamInfoMain)

    def oscam(self):
        if 'oscam' in self.currCam.lower() and self.currCam != 'no':
            if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/OscamStatus")):
                from Plugins.Extensions.OscamStatus.plugin  import OscamStatus
                self.session.openWithCallback(self.ShowSoftcamCallback, OscamStatus)

    def tvPanel(self):
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/tvaddon'):
            from Plugins.Extensions.tvaddon.plugin import Hometv
            self.session.openWithCallback(self.close, Hometv)
        else:
            self.session.open(MessageBox, 'tvAddon Panel Not Installed!!', type=MessageBox.TYPE_INFO, timeout=3)

    def setEcmInfo(self):
        self.ecminfo = GetEcmInfo()
        newEcmFound, ecmInfo = self.ecminfo.getEcm()
        if newEcmFound:
            self['info'].setText(''.join(ecmInfo))
        else:
            self.ecm()

    def ecm(self):
        ecmf = ''
        if os.path.isfile('/tmp/ecm.info'): # is True:
            myfile = open('/tmp/ecm.info')
            for line in myfile.readlines():
                print('line: ', line)
                ecmf = ecmf + line
                print('ecmf + line: ', ecmf)
                self['info'].setText(ecmf)
        else:
            self['info'].setText(ecmf)

    def stopEcmInfoPollTimer(self):
        self.EcmInfoPollTimer.stop()
        return

    def messagekd(self):
        self.session.openWithCallback(self.keysdownload, MessageBox, _('Update SoftcamKeys from google search?'), MessageBox.TYPE_YESNO)

    def keysdownload(self, result):
        if result:
            script = ('%s/auto' % plugin_path)
            from os import access, X_OK, chmod
            if not access(script, X_OK):
                chmod(script, 493)
            self.prombt('sh %s' % script)

    def prombt(self, com):
        self.session.open(Console, _('Update Softcam.key: %s') % com, ['%s' % com])

    def CfgInfo(self):
        self.session.open(InfoCfg)

    def configtv(self):
        from Plugins.Extensions.tvManager.data.datas import tv_config
        self.session.open(tv_config)

    def cgdesc(self):
        self['desc'].setText(_('Select a cam to run ...'))

    def openTest(self):
        pass

    def download(self):
        self.session.open(GetipklistTv)
        self.onShown.append(self.readScripts)

    def getLastIndex(self):
        a = 0
        if len(self.namelist) > 0:
            for x in self.namelist:
                if x == self.currCam:
                    return a
                a += 1
        else:
            return -1
        return -1

    def action(self):
        self.session.nav.stopService()
        msg = []
        self.last = self.getLastIndex()
        self.var = self['list'].getSelectionIndex()
        if self.last > -1:
            if self.last == self.var:
                self.cmd1 = '/usr/camscript/' + self.softcamslist[self.var][0] + '.sh' + ' cam_res &'
                msg.append(_("RESTART CAM "))
                os.system(self.cmd1)
                sleep(1)
            else:
                self.cmd1 = '/usr/camscript/' + self.softcamslist[self.last][0] + '.sh' + ' cam_down &'
                msg.append(_("STOP & RESTART CAM "))
                os.system(self.cmd1)
                sleep(1)
                self.cmd1 = '/usr/camscript/' + self.softcamslist[self.var][0] + '.sh' + ' cam_up &'
                os.system(self.cmd1)
        else:
            try:
                self.cmd1 = '/usr/camscript/' + self.softcamslist[self.var][0] + '.sh' + ' cam_up &'
                msg.append(_("UP CAM 2"))
                os.system(self.cmd1)
                sleep(1)
            except:
                self.close()
        if self.last != self.var:
            try:
                self.currCam = self.softcamslist[self.var][0]
                self.writeFile()
            except:
                self.close()
        msg = (" %s " % _("and")).join(msg)
        self.mbox = self.session.open(MessageBox, _("Please wait, %s.") % msg, MessageBox.TYPE_INFO, timeout=5)
        # self.session.nav.playService(self.oldService, adjust=False)
        self.session.nav.playService(self.oldService)

        self.EcmInfoPollTimer = eTimer()
        try:
            self.EcmInfoPollTimer_conn = self.EcmInfoPollTimer.timeout.connect(self.setEcmInfo)
        except:
            self.EcmInfoPollTimer.callback.append(self.setEcmInfo)
        self.EcmInfoPollTimer.start(200)
        self.readScripts()
        return

    def writeFile(self):
        if self.currCam is not None:
            clist = open('/etc/clist.list', 'w')
            clist.write(self.currCam)
            clist.close()
        stcam = open('/etc/startcam.sh', 'w')
        stcam.write('#!/bin/sh\n' + self.cmd1)
        stcam.close()
        os.system('chmod 755 /etc/startcam.sh &')
        return

    def stop(self):
        self.EcmInfoPollTimer.stop()
        last = self.getLastIndex()
        if last > -1:
            self.cmd1 = '/usr/camscript/' + self.softcamslist[last][0] + ' cam_down &'
            os.system(self.cmd1)
        else:
            return
        self.currCam = 'no'
        self.writeFile()
        sleep(1)
        self['info'].setText('CAM STOPPED')
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        except:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()
        self.readScripts()
        return

    def readScripts(self):
        self.index = 0
        self.indexto = ''
        scriptlist = []
        pliste = []
        path = '/usr/camscript/'
        for root, dirs, files in os.walk(path):
            for name in files:
                scriptlist.append(name)
        self.emulist = scriptlist
        i = len(self.softcamslist)
        del self.softcamslist[0:i]
        for lines in scriptlist:
            dat = path + lines
            sfile = open(dat, 'r')
            for line in sfile:
                if line[0:3] == 'OSD':
                    nam = line[5:len(line) - 2]
                    print('We are in tvManager and cam is type  = ', nam)
                    if self.currCam is not None:
                        if nam == self.currCam:
                            self.softcamslist.append(show_list(nam))
                        else:
                            self.softcamslist.append(show_list(nam))
                            self.index += 1
                    else:
                        self.softcamslist.append(show_list(nam))
                        self.index += 1
                    pliste.append(nam)
            sfile.close()
            self['list'].l.setList(self.softcamslist)
            self.namelist = pliste
        return

    def readCurrent(self):
        currCam = ''
        FilCurr = ''
        if fileExists('/etc/CurrentBhCamName'):
            FilCurr = '/etc/CurrentBhCamName'
        else:
            FilCurr = '/etc/clist.list'
        try:
            clist = open(FilCurr, 'r')
        except:
            return

        if clist is not None:
            for line in clist:
                currCam = line
            clist.close()
        return currCam

    def autocam(self):
        current = None
        try:
            clist = open('/etc/clist.list', 'r')
            print('found list')
        except:
            return

        if clist is not None:
            for line in clist:
                current = line
            clist.close()
        print('current =', current)
        if os.path.isfile('/etc/autocam.txt') is False:
            alist = open('/etc/autocam.txt', 'w')
            alist.close()
        self.autoclean()
        alist = open('/etc/autocam.txt', 'a')
        alist.write(self.oldService.toString() + '\n')
        self.last = self.getLastIndex()
        alist.write(current + '\n')
        alist.close()
        self.session.openWithCallback(self.callback, MessageBox, _('Autocam assigned to the current channel'), type=1, timeout=10)
        return

    def autoclean(self):
        delemu = 'no'
        if os.path.isfile('/etc/autocam.txt') is False:
            return
        myfile = open('/etc/autocam.txt', 'r')
        myfile2 = open('/etc/autocam2.txt', 'w')
        icount = 0
        for line in myfile.readlines():
            print('We are in tvManager line, self.oldService.toString() =', line, self.oldService.toString())
            if line[:-1] == self.oldService.toString():
                delemu = 'yes'
                icount = icount + 1
                continue
            if delemu == 'yes':
                delemu = 'no'
                icount = icount + 1
                continue
            myfile2.write(line)
            icount = icount + 1
        myfile.close()
        myfile2.close()
        os.system('rm /etc/autocam.txt')
        os.system('cp /etc/autocam2.txt /etc/autocam.txt')


class GetipklistTv(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + '/GetipklistTv.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.names = []
        self.names_1 = []
        self.list = []
        self['text'] = m2list([])
        self.setTitle(_(title_plug))
        self['title'] = Label(_(title_plug))
        self['desc2'] = Label(_('Getting the list, please wait ...'))
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_(''))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_green'].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'cancel': self.close}, -1)
        self.onShown.append(self.get_list)

    def get_list(self):
        self.timer = eTimer()
        if os.path.isfile('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.downloadxmlpage)
        else:
            self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(200, 1)

    def downloadxmlpage(self):
        url = str(FTP_XML)
        if six.PY3:
            url = six.binary_type(url,encoding="utf-8")
        print('url softcam: ', url)
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['desc2'].setText(_('Try again later ...'))
        self.downloading = False

    def _gotPageLoad(self, result):
        self.xml = str(result)
        if six.PY3:
            self.xml = six.ensure_str(result)
        self.data = []
        self.names = []
        icount = 0
        list = []
        try:
            if self.xml:
                self.xmlparse = minidom.parseString(self.xml)
            else:
                self.downloading = False
                return
            for plugins in self.xmlparse.getElementsByTagName('plugins'):
                namex = checkStr(plugins.getAttribute('cont'))
                self.names.append(namex)
                self.names.sort()
            self['desc2'].setText(_('PLEASE SELECT...'))
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            self.downloading = False

    def okClicked(self):
        inx = self['text'].getSelectionIndex()
        if self.downloading == True:
            try:
                selection = self.names[inx]
                self.session.open(GetipkTv, self.xmlparse, selection)
            except:
                return
        else:
            return

class GetipkTv(Screen):
    def __init__(self, session, xmlparse, selection):
        self.session = session
        skin = skin_path + '/GetipkTv.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        self['text'] = m2list([])
        self.list = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            # # if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
            namex = checkStr(plugins.getAttribute('cont'))
            namex = namex.replace('_',' ')
            if str(namex) == self.selection:                                          
            # if str(plugins.getAttribute('cont')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    pluginname = plugin.getAttribute('name')
                    pluginname = checkStr(pluginname)
                    self.list.append(pluginname)
                    self.list.sort()
                    # self.list.append(plugin.getAttribute('name'))
                    # self.list.append(plugin.getAttribute('name').encode('utf8'))
        showlist(self.list, self['text'])
        self.setTitle(_(title_plug))
        self['title'] = Label(_(title_plug))
        self['desc'] = Label(_('Select and Install'))
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_(''))
        self['key_yellow'] = Button(_(''))
        self['key_blue'] = Button(_(''))
        self['key_green'].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.message,
         'cancel': self.close}, -1)

    def message(self):
        self.session.openWithCallback(self.selclicked, MessageBox, _('Do you want to install?'), MessageBox.TYPE_YESNO)

    def selclicked(self, result):
        inx = self['text'].getSelectionIndex()
        try:
            selection_country = self.list[inx]
        except:
            return
        if result:
            for plugins in self.xmlparse.getElementsByTagName('plugins'):
                namex = checkStr(plugins.getAttribute('cont'))
                namex = namex.replace('_',' ')
                if str(namex) == self.selection:
                # if str(plugins.getAttribute('cont')) == self.selection:
                # # if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                    for plugin in plugins.getElementsByTagName('plugin'):
                        # if plugin.getAttribute('name') == selection_country:
                        # # if plugin.getAttribute('name').encode('utf8') == selection_country:
                            urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                            pluginname = plugin.getAttribute('name')
                            pluginname = checkStr(pluginname)
                            self.prombt(urlserver, pluginname)
        else:
            return

    def prombt(self, com, dom):
        try:
            useragent = "--header='User-Agent: QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)'"
            # com = getUrl(com)
            self.com = str(com)
            self.dom = str(dom)
            print('self.com---------------', self.com)
            print('self.dom---------------', self.dom)
            # self.dom = dom
            # self.com = com
            ipkpth = '/var/volatile/tmp'
            destipk = ipkpth + '/download.ipk'
            desttar = ipkpth + '/download.tar.gz'
            destdeb = ipkpth + '/download.deb'
            self.timer = eTimer()
            self.timer.start(1500, 1)
            if self.com.find('.ipk') != -1:
                os.system("wget %s -c %s -O %s > /dev/null" %(useragent, self.com, destipk))
                # cmd0 = "wget %s -c %s -O %s > /dev/null" %(useragent,self.com,destipk)
                cmd0 = 'opkg install --force-overwrite ' + destipk #self.com #dest
                self.session.open(Console, title='IPK Installation', cmdlist=[cmd0, 'sleep 5']) #, finishedCallback=self.msgipkinst)
            if self.com.find('.tar.gz') != -1:
                os.system("wget %s -c %s -O %s > /dev/null" %(useragent, self.com, desttar) )
                # cmd0 = 'tar -xzvf ' + self.com + ' -C /'
                cmd0 = 'tar -xzvf ' + desttar + ' -C /'
                self.session.open(Console, title='TAR GZ Installation', cmdlist=[cmd0, 'sleep 5']) #, finishedCallback=self.msgipkinst)
            if self.com.find('.deb') != -1:
                if os.path.isfile('/var/lib/dpkg/status'):
                    os.system("wget %s -c %s -O %s > /dev/null" %(useragent, self.com, destdeb) )
                    cmd0 = 'dpkg -i ' + destdeb
                    # cmd0 = 'dpkg -i ' + self.com
                    self.session.open(Console, title='DEB Installation', cmdlist=[cmd0, 'sleep 5']) #, finishedCallback=self.msgipkinst)
                else:
                     self.mbox = self.session.open(MessageBox, _('Unknow Image!'), MessageBox.TYPE_INFO, timeout=5)
        except:
            self.mbox = self.session.open(MessageBox, _('Download failur!'), MessageBox.TYPE_INFO, timeout=5)
            self.addondel()
            return

    def addondel(self):
        files = glob.glob('/var/volatile/tmp/download.*', recursive=True)
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))
        self.mbox = self.session.open(MessageBox, _('All file Download are removed!'), MessageBox.TYPE_INFO, timeout=5)

class InfoCfg(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + '/InfoCfg.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        info = ''
        self.list = []
        self['text'] = Label("")
        self['actions'] = ActionMap(['WizardActions',
         'OkCancelActions',
         'DirectionActions',
         'ColorActions'], {'ok': self.close,
         'back': self.close,
         'cancel': self.close,
         'red': self.close}, -1)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_(''))
        self['key_yellow'] = Button(_(''))
        self['key_blue'] = Button(_(''))
        self['key_green'].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.setTitle(_(title_plug))
        self['title'] = Label(_(title_plug))
        self['desc'] = Label(_('Path Configuration Folder'))
        self.onShown.append(self.updateList)

    def getcont(self):
        cont = "Config Softcam Manager' :\n"
        cont += "cccam_221\n"
        cont += "/etc/cccam.cfg\n"
        cont += "cccam_230\n"
        cont += "/usr/cfmngr/cccam/cccam.cfg\n"
        cont += "doscam_0.30\n"
        cont += "/usr/cfmngr/doscam/doscam.cfg\n"
        cont += "oscam/powervu/svn_yy.xx\n"
        cont += "/usr/cfmngr/oscam/oscam.server\n"
        cont += "oscamymod_yy.xx\n"
        cont += "/usr/cfmngr/oscamymod/oscam.server\n"
        cont += "wicardd_19\n"
        cont += "/usr/cfmngr/wicardd/wicardd.conf\n"
        cont += "mgcamd_1.38d\n"
        cont += "/usr/keys/cccamd.list \n"
        return cont

    def updateList(self):
        self["text"].setText(self.getcont())

class Ipkremove(Screen):
    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self['list'] = FileList('/', matchingPattern='^.*\\.(png|avi|mp3|mpeg|ts)')
        self['pixmap'] = Pixmap()
        self['text'] = Input('1234', maxSize=True, type=Input.NUMBER)
        self['actions'] = NumberActionMap(['WizardActions', 'InputActions'], {'ok': self.ok,
         'back': self.close,
         'left': self.keyLeft,
         'right': self.keyRight,
         '1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal}, -1)
        self.onShown.append(self.openTest)

    def openTest(self):
        try:
            myfile = open('/var/lib/opkg/status', 'r+')
            icount = 0
            listc = []
            ebuf = []
            for line in myfile:
                listc.append(icount)
                listc[icount] = (_(line), '')
                ebuf.append(listc[icount])
                icount = icount + 1
            myfile.close()
            ipkres = self.session.openWithCallback(self.test2, ChoiceBox, title='Please select ipkg to remove', list=ebuf)
            self.close()
        except:
            self.close()

    def test2(self, returnValue):
        if returnValue is None:
            return
        else:
            print('returnValue', returnValue)
            nos = len
            emuname = ''
            ipkname = returnValue[0]
            print('ipkname =', ipkname)
            cmd = 'ipkg remove ' + ipkname[:-1] + ' >/var/volatile/tmp/ipk.log'
            print(cmd)
            os.system(cmd)
            cmd = 'touch /etc/tmpfile'
            os.system(cmd)
            myfile = open('/var/lib/opkg/status', 'r')
            f = open('/etc/tmpfile', 'w')
            icount = 0
            for line in myfile:
                if line != ipkname:
                    print('myfile line=', line)
                    f.write(line)
            f.close()
            f = open('/etc/tmpfile', 'r+')
            f2 = f.readlines()
            print('/etc/tmpfile', f2)
            f.close()
            f = open('/var/lib/opkg/status', 'r+')
            f2 = f.readlines()
            print('/var/lib/opkg/status', f2)
            f.close()
            cmd = 'rm /var/lib/opkg/status'
            os.system(cmd)
            cmd = 'mv /etc/tmpfile /var/lib/opkg/status'
            os.system(cmd)
            f = open('/var/lib/opkg/status', 'r+')
            f2 = f.readlines()
            print('/var/lib/opkg/status 2', f2)
            f.close()
            return
            return

    def callback(self, answer):
        print('answer:', answer)

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def ok(self):
        selection = self['list'].getSelection()
        if selection[1] == True:
            self['list'].changeDir(selection[0])
        else:
            self['pixmap'].instance.setPixmapFromFile(selection[0])

    def keyNumberGlobal(self, number):
        print('pressed', number)
        self['text'].number(number)

def startConfig(session, **kwargs):
    session.open(tvManager)

def mainmenu(menuid):
    if menuid != 'setup':
        return []
    else:
        return [(_('Softcam Manager'),
          startConfig,
          'Softcam Manager',
          None)]

def autostart(reason, session=None, **kwargs):
    "called with reason=1 to during shutdown, with reason=0 at startup?"
    print("[Softcam] Started")
    if reason == 0:
        print('reason 0')
        if session is not None:
            print('session none')
            try:
                os.system("mv /usr/bin/dccamd /usr/bin/dccamdOrig &")
                os.system("ln -sf /usr/bin /var/bin")
                os.system("ln -sf /usr/keys /var/keys")
                os.system("ln -sf /usr/scce /var/scce")
                os.system("ln -sf /usr/camscript /var/camscript")
                os.system("sleep 2")
                os.system("/etc/startcam.sh &")
                os.system('sleep 2')
                print('ok started autostart')
            except:
                print('except autostart')
                pass
        else:
            print('pass autostart')
            pass

def menu(menuid, **kwargs):
    if menuid == 'cam':
        return [(_(name_plug),
          boundFunction(main, showExtentionMenuOption=True),
          'Softcam Manager',
          -1)]
    return []

def main(session, **kwargs):
    session.open(tvManager)

def StartSetup(menuid):
    if menuid == 'mainmenu':
        return [(name_plug,
          main,
          'Softcam Manager',
          44)]
    else:
        return []

def Plugins(**kwargs):
    iconpic = 'logo.png'
    if HD.width() > 1280:
        iconpic = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/pics/logo.png")
    return [PluginDescriptor(name=_(name_plug), where=PluginDescriptor.WHERE_MENU, fnc=mainmenu),
     PluginDescriptor(name=_(name_plug), description=_(title_plug), where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], needsRestart=True, fnc=autostart),
     PluginDescriptor(name=_(name_plug), description=_(title_plug), where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconpic, fnc=main),
     PluginDescriptor(name=_(name_plug), description=_(title_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]

