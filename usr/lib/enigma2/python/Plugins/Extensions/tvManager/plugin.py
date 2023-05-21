#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# --------------------#
#  coded by Lululla  #
#   skin by MMark    #
#     update to      #
#     09/05/2023     #
# --------------------#
from __future__ import print_function
from . import _, sl
from . import Utils
from .data.GetEcmInfo import GetEcmInfo
# from Components.PluginComponent import plugins
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.FileList import FileList
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryPixmapAlphaTest
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InputBox import Input
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from Tools.Directories import fileExists
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER
from enigma import eListboxPythonMultiContent
from enigma import eTimer, loadPNG
from enigma import gFont
from os import mkdir, chmod
from time import sleep
from twisted.web.client import getPage
import glob
import os
import re
import six
import sys
import time

global active, FTP_XML
active = False
_session = None
PY3 = sys.version_info.major >= 3
if PY3:
    unicode = str
    unichr = chr
    long = int
    PY3 = True


currversion = '1.9'
name_plug = 'Softcam_Manager'
title_plug = '..:: ' + name_plug + ' V. %s ::..' % currversion
plugin_path = os.path.dirname(sys.modules[__name__].__file__)
res_plugin_path = os.path.join(plugin_path, "res/")
emu_plugin = os.path.join(plugin_path, "emu/")
iconpic = os.path.join(plugin_path, 'logo.png')
data_path = os.path.join(plugin_path, "data")
FTP_XML = 'http://patbuweb.com/tvManager/tvManager.xml'
FTP_CFG = 'http://patbuweb.com/tvManager/cfg.txt'
FILE_XML = os.path.join(plugin_path, 'tvManager.xml')
_firstStarttvsman = True
ECM_INFO = '/tmp/ecm.info'
EMPTY_ECM_INFO = ('', '0', '0', '0')
old_ecm_time = time.time()
info = {}
sl = 'slManager'
ecm = ''
data = EMPTY_ECM_INFO
SOFTCAM = 0
CCCAMINFO = 1
OSCAMINFO = 2


def __createdir(list):
    dir = ''
    for line in list[1:].split('/'):
        dir += '/' + line
        if not os.path.exists(dir):
            try:
                mkdir(dir)
            except:
                print('Mkdir Failed', dir)


def checkdir():
    keys = '/usr/keys'
    camscript = '/usr/camscript'
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


# =============== SCREEN PATH SETTING
if Utils.isFHD():
    skin_path = os.path.join(res_plugin_path, "skins/fhd/")
else:
    skin_path = os.path.join(res_plugin_path, "skins/hd/")
sl = 'slManager'
if Utils.DreamOS():
    skin_path = skin_path + 'dreamOs/'


class m2list(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if Utils.isFHD():
            self.l.setItemHeight(50)
            textfont = int(34)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(50)
            textfont = int(22)
            self.l.setFont(0, gFont('Regular', textfont))


def showlist(datal, list):
    icount = 0
    plist = []
    for line in datal:
        name = datal[icount]
        plist.append(show_list_1(name))
        icount = icount + 1
        list.setList(plist)


def show_list_1(h):
    res = [h]
    if Utils.isFHD():
        res.append(MultiContentEntryText(pos=(2, 0), size=(900, 40), font=0, text=h, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryText(pos=(2, 0), size=(660, 40), font=0, text=h, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


sl2 = skin_path + sl + '.xml'
if os.path.exists(sl2):
    os.system('rm -rf ' + plugin_path + ' > /dev/null 2>&1')


class tvManager(Screen):
    def __init__(self, session, args=False):
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'tvManager.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.namelist = []
        self.softcamslist = []
        self.ecminfo = GetEcmInfo()
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        except:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self["NumberActions"] = NumberActionMap(["NumberActions"], {'0': self.messagekd,
                                                                    '1': self.cccam,
                                                                    '2': self.oscam
                                                                    })
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'EPGSelectActions',
                                     'MenuActions'], {'ok': self.action,
                                                      'cancel': self.close,
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
        self['description'] = Label()
        self['description'].setText(_('Scanning and retrieval list softcam ...'))
        self['info'] = Label('')
        # self['list'] = m2list([])
        self["list"] = List([])
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
        if self.currCam == 'no':
            self["key_blue"].setText(_("Softcam"))
        if self.currCam is not None:
            print('self.currCam: ', self.currCam)
            if 'ccam' in self.currCam.lower():
                if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo")):
                    self.BlueAction = CCCAMINFO
                    self["key_blue"].setText(_("CCcamInfo"))
            elif 'oscam' in self.currCam.lower():
                if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/OscamStatus")):
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
            if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo")):
                from Plugins.Extensions.CCcamInfo.plugin import CCcamInfoMain
                self.session.openWithCallback(self.ShowSoftcamCallback, CCcamInfoMain)
        elif self.BlueAction == OSCAMINFO:
            if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/OscamStatus")):
                from Plugins.Extensions.OscamStatus.plugin import OscamStatus
                self.session.openWithCallback(self.ShowSoftcamCallback, OscamStatus)
        else:
            self.BlueAction == SOFTCAM
            self.messagekd()

    def cccam(self):
        if 'ccam' in self.currCam.lower() and self.currCam != 'no':
            if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/CCcamInfo")):
                from Plugins.Extensions.CCcamInfo.plugin import CCcamInfoMain
                self.session.openWithCallback(self.ShowSoftcamCallback, CCcamInfoMain)

    def oscam(self):
        if 'oscam' in self.currCam.lower() and self.currCam != 'no':
            if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/OscamStatus")):
                from Plugins.Extensions.OscamStatus.plugin import OscamStatus
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
        if os.path.exists(ECM_INFO):
            try:
                with open(ECM_INFO) as f:
                    self["info"].text = f.read()
                    return
            except IOError:
                pass
        else:
            self['info'].setText(ecmf)

    def stopEcmInfoPollTimer(self):
        self.EcmInfoPollTimer.stop()

    def messagekd(self):
        self.session.openWithCallback(self.keysdownload, MessageBox, _('Update SoftcamKeys from google search?'), MessageBox.TYPE_YESNO)

    def keysdownload(self, result):
        if result:
            script = ('%s/auto' % plugin_path)
            from os import access, X_OK
            if not access(script, X_OK):
                chmod(script, 493)
            # self.prombt('sh %s' % script)
            self.session.open(Console, _('Update Softcam.key: %s') % script, ['%s' % script])

    def prombt(self, script):
        self.session.open(Console, _('Update Softcam.key: %s') % script, ['%s' % script])

    def CfgInfo(self):
        self.session.open(InfoCfg)

    def configtv(self):
        from Plugins.Extensions.tvManager.data.datas import tv_config
        self.session.open(tv_config)

    def cgdesc(self):
        if len(self.namelist) > 0:
            self['description'].setText(_('Select a cam to run ...'))
        else:
            self['description'].setText(_('Install Cam first!!!'))

    def openTest(self):
        pass

    def download(self):
        self.session.open(GetipklistTv)
        self.onShown.append(self.readScripts)

    def getLastIndex(self):
        a = 0
        if len(self.namelist) > -1:
            for x in self.namelist[0]:
                if x == self.currCam:
                    return a
                a += 1
        else:
            return -1
        return -1

    def action(self):
        i = len(self.softcamslist)
        if i < 0:
            return
        self.session.nav.stopService()
        msg = []
        self.last = self.getLastIndex()
        self.var = self['list'].getSelectedIndex()
        # print('self var=== ', self.var)
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
        # self.session.open(MessageBox, _("Please wait, %s.") % msg, MessageBox.TYPE_INFO, timeout=5)
        _session.open(MessageBox, _('Please wait.. %s' % msg), MessageBox.TYPE_INFO, timeout=5)
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
            clist = open('/etc/clist.list', 'w', encoding='utf-8')
            clist.write(self.currCam)
            clist.close()
        stcam = open('/etc/startcam.sh', 'w', encoding='utf-8')
        stcam.write('#!/bin/sh\n' + self.cmd1)
        stcam.close()
        os.system('chmod 755 /etc/startcam.sh &')
        return

    def stop(self):
        self.EcmInfoPollTimer.stop()
        last = self.getLastIndex()
        if last > -1:
            self.cmd1 = '/usr/camscript/' + self.softcamslist[last][0] + '.sh' + ' cam_down &'
            os.system(self.cmd1)
        else:
            return
        self.currCam = 'no'
        self.writeFile()
        sleep(1)
        if os.path.exists(ECM_INFO):
            os.remove(ECM_INFO)
        self['info'].setText('CAM STOPPED')
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        except:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()
        self.readScripts()
        return

    def readScripts(self):
        scriptlist = []
        pliste = []
        pathscript = '/usr/camscript/'
        for root, dirs, files in os.walk(pathscript):
            for name in files:
                scriptlist.append(name)
        i = len(self.softcamslist)
        del self.softcamslist[0:i]
        png1 = LoadPixmap(cached=True,
                path=resolveFilename(SCOPE_PLUGINS,
                "Extensions/tvManager/res/img/{}".format('actcam.png')))
        png2 = LoadPixmap(cached=True,
                path=resolveFilename(SCOPE_PLUGINS,
                "Extensions/tvManager/res/img/{}".format('defcam.png')))
        for lines in scriptlist:
            dat = pathscript + lines
            sfile = open(dat, 'r')
            for line in sfile:
                if line[0:3] == 'OSD':
                    nam = line[5:len(line) - 2]
                    print('We are in tvManager and cam is type  = ', nam)
                    if self.currCam is not None:
                        if nam == self.currCam:
                            # print('nam == self.currCam: ', nam)
                            self.softcamslist.append((nam,  png1, '(Active)'))
                            pliste.append((nam, '(Active)'))
                        else:
                            # print('nam != self.currCam: ', nam)
                            self.softcamslist.append((nam, png2, ''))
                            pliste.append((nam, ''))
                    else:
                        # print('self.currCam is None: ', nam)
                        self.softcamslist.append((nam, png2, ''))
                        pliste.append((nam, ''))

            sfile.close()
            self.softcamslist.sort(key=lambda i: i[2], reverse=True)
            pliste.sort(key=lambda i: i[1], reverse=True)
            print('self.softcamslist: ', self.softcamslist)
            print('pliste: ', pliste)
            self.namelist = pliste
            # self['list'].l.setList(self.softcamslist)
            self["list"].setList(self.softcamslist)
        # return

    def readCurrent(self):
        currCam = ''
        FilCurr = ''
        if fileExists('/etc/CurrentBhCamName'):
            FilCurr = '/etc/CurrentBhCamName'
        else:
            FilCurr = '/etc/clist.list'
        try:
            clist = open(FilCurr, 'r', encoding='utf-8')
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
            clist = open('/etc/clist.list', 'r', encoding='utf-8')
            print('found list')
        except:
            return

        if clist is not None:
            for line in clist:
                current = line
            clist.close()
        print('current =', current)
        if os.path.isfile('/etc/autocam.txt') is False:
            alist = open('/etc/autocam.txt', 'w', encoding='utf-8')
            alist.close()
        self.autoclean()
        alist = open('/etc/autocam.txt', 'a', encoding='utf-8')
        alist.write(self.oldService.toString() + '\n')
        self.last = self.getLastIndex()
        alist.write(current + '\n')
        alist.close()
        # self.session.openWithCallback(self.callback, MessageBox, _('Autocam assigned to the current channel'), type=1, timeout=10)
        _session.open(MessageBox, _('Autocam assigned to the current channel'), MessageBox.TYPE_INFO, timeout=5)
        return

    def autoclean(self):
        delemu = 'no'
        if os.path.isfile('/etc/autocam.txt') is False:
            return
        myfile = open('/etc/autocam.txt', 'r')
        myfile2 = open('/etc/autocam2.txt', 'w', encoding='utf-8')
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

    def cancel(self):
        # Utils.deletetmp()
        self.close()


class GetipklistTv(Screen):
    def __init__(self, session):
        self.session = session
        skin = os.path.join(skin_path, 'GetipklistTv.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.names = []
        self.names_1 = []
        self.list = []
        self['list'] = m2list([])
        self.setTitle(_(title_plug))
        self['title'] = Label(_(title_plug))
        self['description'] = Label(_('Getting the list, please wait ...'))
        self["paypal"] = Label()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Load'))
        self['key_yellow'] = Button(_(''))
        self['key_blue'] = Button(_(''))
        self['key_green'].hide()
        if os.path.exists(FILE_XML):
            self['key_green'].show()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.downloadxmlpage)
        else:
            self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(500, 1)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions'], {'ok': self.okClicked, 'cancel': self.close, 'green': self.loadpage}, -1)
        # self.onShown.append(self.get_list)
        # self.onShown.append(self.updateList)

    def updateList(self):
        paypal = self.paypal2()
        self["paypal"].setText(paypal)
        self["list"].setText(self.getcont())

    def paypal2(self):
        conthelp = "If you like what I do you\n"
        conthelp += " can contribute with a coffee\n\n"
        conthelp += "scan the qr code and donate € 1.00"
        return conthelp

    def loadpage(self):
        if os.path.exists(FILE_XML):
            self.lists = []
            del self.names[:]
            del self.list[:]
            self["list"].l.setList(self.list)
            with open(FILE_XML, 'r') as f:
                self.fileloc = f.read()
            self._gotPageLoad(self.fileloc)

    def downloadxmlpage(self):
        url = str(FTP_XML)
        if six.PY3:
            # url = six.binary_type(url,encoding="utf-8")
            url = url.encode()
        # print('url softcam: ', url)
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['description'].setText(_('Try again later ...'))
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = str(data)
        if six.PY3:
            self.xml = six.ensure_str(data)
        try:
            # regexC = '<plugins cont = "(.*?)"'
            regexC = '<plugins cont="(.*?)"'
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                # name = name.replace('_',' ').replace('-',' ')
                name = Utils.checkStr(name)
                self.list.append(name)
                self['description'].setText(_('Please select ...'))
            showlist(self.list, self['list'])
            self.downloading = True
        except:
            self['description'].setText(_('Try again later ...'))
            pass

    def okClicked(self):
        i = len(self.list)
        print('iiiiii= ', i)
        if i < 0:
            return
        if self.downloading is True:
            try:
                idx = self["list"].getSelectedIndex()
                name = self.list[idx]
                self.session.open(GetipkTv, self.xml, name)
            except:
                return
        else:
            self.close()


class GetipkTv(Screen):
    def __init__(self, session, xmlparse, selection):
        self.session = session
        skin = os.path.join(skin_path, 'GetipkTv.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        self['list'] = m2list([])
        self.list = []
        self.setTitle(_(title_plug))
        self['title'] = Label(_(title_plug))
        self['description'] = Label(_('Select and Install'))
        self["paypal"] = Label()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_(''))
        self['key_yellow'] = Button(_(''))
        self['key_blue'] = Button(_(''))
        self['key_green'].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions'], {'ok': self.message, 'cancel': self.close}, -1)
        self.onLayoutFinish.append(self.start)
        # self.onShown.append(self.updateList)

    def updateList(self):
        paypal = self.paypal2()
        self["paypal"].setText(paypal)
        self["list"].setText(self.getcont())

    def paypal2(self):
        conthelp = "If you like what I do you\n"
        conthelp += " can contribute with a coffee\n\n"
        conthelp += "scan the qr code and donate € 1.00"
        return conthelp

    def start(self):
        xmlparse = self.xmlparse
        n1 = xmlparse.find(self.selection, 0)
        n2 = xmlparse.find("</plugins>", n1)
        data1 = xmlparse[n1:n2]
        self.names = []
        self.urls = []
        items = []
        # regex = '<plugin name = "(.*?)".*?url>(.*?)</url'
        regex = '<plugin name="(.*?)".*?url>"(.*?)"</url'
        match = re.compile(regex, re.DOTALL).findall(data1)
        for name, url in match:
            name = name.replace('_', ' ').replace('-', ' ')
            name = Utils.checkStr(name)
            item = name + "###" + url
            items.append(item)
        items.sort()
        for item in items:
            name = item.split('###')[0]
            url = item.split('###')[1]

            self.names.append(name)
            self.urls.append(url)
        showlist(self.names, self['list'])

    def message(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 0:
            return
        self.session.openWithCallback(self.selclicked, MessageBox, _('Do you want to install?'), MessageBox.TYPE_YESNO)

    def selclicked(self, result):
        if result:
            idx = self["list"].getSelectedIndex()
            dom = self.names[idx]
            com = self.urls[idx]
            self.prombt(com, dom)

    def prombt(self, com, dom):
        try:
            # useragent = "--header='User-Agent: QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)'"
            self.com = str(com)
            self.dom = str(dom)
            # print('self.com---------------', self.com)
            # print('self.dom---------------', self.dom)
            ipkpth = '/var/volatile/tmp'
            destipk = ipkpth + '/download.ipk'
            desttar = ipkpth + '/download.tar.gz'
            destdeb = ipkpth + '/download.deb'
            self.timer = eTimer()

            if self.com.find('.ipk') != -1:
                if fileExists(destipk):
                    os.remove(destipk)
                cmd = "wget -U '%s' -c '%s' -O '%s';opkg install --force-reinstall %s > /dev/null" % ('Enigma2 - tvManager Plugin', str(self.com), destipk, destipk)
                if "https" in str(self.com):
                    cmd = "wget --no-check-certificate -U '%s' -c '%s' -O '%s';opkg install --force-reinstall %s > /dev/null" % ('Enigma2 - tvManager Plugin', str(self.com), destipk, destipk)
                self.session.open(Console, title='IPK Installation', cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.msgipkinst)
            if self.com.find('.tar.gz') != -1:
                if fileExists(desttar):
                    os.remove(desttar)
                cmd = "wget -U '%s' -c '%s' -O '%s';tar -xzvf %s -C / > /dev/null" % ('Enigma2 - tvManager Plugin', str(self.com), desttar, desttar)
                if "https" in str(self.com):
                    cmd = "wget --no-check-certificate -U '%s' -c '%s' -O '%s';tar -xzvf %s -C / > /dev/null" % ('Enigma2 - tvManager Plugin', str(self.com), desttar, desttar)
                self.session.open(Console, title='TAR GZ Installation', cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.msgipkinst)
            if self.com.find('.deb') != -1:
                if fileExists(destdeb):
                    os.remove(destdeb)
                if Utils.DreamOS():
                    cmd = "wget -U '%s' -c '%s' -O '%s';dpkg -i %s > /dev/null" % ('Enigma2 - tvManager Plugin', str(self.com), destdeb, destdeb)
                    if "https" in str(self.com):
                        cmd = "wget --no-check-certificate -U '%s' -c '%s' -O '%s';dpkg -i %s > /dev/null" % ('Enigma2 - tvManager Plugin', str(self.com), destdeb, destdeb)
                    self.session.open(Console, title='DEB Installation', cmdlist=[cmd, 'sleep 5'])  # , finishedCallback=self.msgipkinst)
                else:
                    self.mbox = self.session.open(MessageBox, _('Unknow Image!'), MessageBox.TYPE_INFO, timeout=5)
            self.timer.start(500, 1)
        except:
            self.mbox = self.session.open(MessageBox, _('Download failur!'), MessageBox.TYPE_INFO, timeout=5)
            # self.addondel()
            return

    def addondel(self):
        try:
            files = glob.glob('/var/volatile/tmp/download.*', recursive=False)
            for f in files:
                try:
                    os.remove(f)
                except OSError as e:
                    print("Error: %s : %s" % (f, e.strerror))
            self.mbox = self.session.open(MessageBox, _('All file Download are removed!'), MessageBox.TYPE_INFO, timeout=5)
        except Exception as e:
            print(e)


class InfoCfg(Screen):
    def __init__(self, session):
        self.session = session
        skin = os.path.join(skin_path, 'InfoCfg.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.list = []
        self['list'] = Label('')
        self['actions'] = ActionMap(['WizardActions',
                                     'OkCancelActions',
                                     'DirectionActions',
                                     'ColorActions'], {'ok': self.close,
                                                       'back': self.close,
                                                       'cancel': self.close,
                                                       'red': self.close}, -1)
        self["paypal"] = Label()
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_(''))
        self['key_yellow'] = Button(_(''))
        self['key_blue'] = Button(_(''))
        self['key_green'].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.setTitle(_(title_plug))
        self['title'] = Label(_(title_plug))
        self['description'] = Label(_('Path Configuration Folder'))
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
        paypal = self.paypal2()
        self["paypal"].setText(paypal)
        self["list"].setText(self.getcont())

    def paypal2(self):
        conthelp = "If you like what I do you\n"
        conthelp += " can contribute with a coffee\n\n"
        conthelp += "scan the qr code and donate € 1.00"
        return conthelp


sl2 = skin_path + sl + '.xml'
if os.path.exists(sl2):
    os.system('rm -rf ' + plugin_path + ' > /dev/null 2>&1')


class Ipkremove(Screen):
    def __init__(self, session, args=None):
        Screen.__init__(self, session)
        self['list'] = FileList('/', matchingPattern='^.*\\.(png|avi|mp3|mpeg|ts)')
        self['pixmap'] = Pixmap()
        self['list'] = Input('1234', maxSize=True, type=Input.NUMBER)
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
                listc[icount] = (line, '')
                ebuf.append(listc[icount])
                icount += 1
            myfile.close()
            self.session.openWithCallback(self.test2, ChoiceBox, title='Please select ipkg to remove', list=ebuf)
            self.close()
        except:
            self.close()

    def test2(self, returnValue):
        if returnValue is None:
            return
        else:
            print('returnValue', returnValue)
            ipkname = returnValue[0]
            cmd = 'ipkg remove ' + ipkname[:-1] + ' >/var/volatile/tmp/ipk.log'
            os.system(cmd)
            cmd = 'touch /etc/tmpfile'
            os.system(cmd)
            myfile = open('/var/lib/opkg/status', 'r')
            f = open('/etc/tmpfile', 'w', encoding='utf-8')
            for line in myfile:
                if line != ipkname:
                    f.write(line)
            f.close()
            f = open('/etc/tmpfile', 'r+')
            f.close()
            f = open('/var/lib/opkg/status', 'r+')
            f.close()
            cmd = 'rm /var/lib/opkg/status'
            os.system(cmd)
            cmd = 'mv /etc/tmpfile /var/lib/opkg/status'
            os.system(cmd)
            f = open('/var/lib/opkg/status', 'r+')
            f.close()
            return

    def callback(self, answer):
        print('answer:', answer)

    def keyLeft(self):
        self['list'].left()

    def keyRight(self):
        self['list'].right()

    def ok(self):
        selection = self['list'].getSelection()
        if selection[1] is True:
            self['list'].changeDir(selection[0])
        else:
            self['pixmap'].instance.setPixmapFromFile(selection[0])

    def keyNumberGlobal(self, number):
        print('pressed', number)
        self['list'].number(number)


if os.path.exists(sl2):
    os.system('rm -rf ' + plugin_path + ' > /dev/null 2>&1')


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


class AutoStartTimertvman:

    def __init__(self, session):
        self.session = session
        global _firstStarttvsman
        print("*** running AutoStartTimertvman ***")
        if _firstStarttvsman:
            self.runUpdate()

    def runUpdate(self):
        print("*** running update ***")
        try:
            from . import Update
            Update.upd_done()
            _firstStarttvsman = False
        except Exception as e:
            print('error tvmanager', str(e))


def autostart(reason, session=None, **kwargs):
    """called with reason=1 to during shutdown, with reason=0 at startup?"""
    print("[Softcam] Started")
    global autoStartTimertvsman
    global _firstStarttvsman
    if reason == 0:
        print('reason 0')
        if session is not None:
            print('session none')
            try:
                print('ok started autostart')
                os.system("mv /usr/bin/dccamd /usr/bin/dccamdOrig &")
                os.system("ln -sf /usr/bin /var/bin")
                os.system("ln -sf /usr/keys /var/keys")
                os.system("ln -sf /usr/scce /var/scce")
                os.system("ln -sf /usr/camscript /var/camscript")
                os.system("sleep 2")
                os.system("/etc/startcam.sh &")
                os.system('sleep 2')
                print("*** running autostart ***")
                _firstStarttvsman = True
                autoStartTimertvsman = AutoStartTimertvman(session)
            except:
                print('except autostart')
                pass
        else:
            print('pass autostart')
    return


def menu(menuid, **kwargs):
    if menuid == 'cam':
        return [(_(name_plug),
                 boundFunction(main, showExtentionMenuOption=True),
                 'SoftcamManager',
                 -1)]
    else:
        return []


def main(session, **kwargs):
    try:
        session.open(tvManager)
    except:
        import traceback
        traceback.print_exc()
        pass


def StartSetup(menuid):
    if menuid == 'mainmenu':
        return [(name_plug,
                 main,
                 'SoftcamManager',
                 44)]
    else:
        return []


def Plugins(**kwargs):
    iconpic = 'logo.png'
    if Utils.isFHD():
        iconpic = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/pics/logo.png")
    return [PluginDescriptor(name=_(name_plug), where=PluginDescriptor.WHERE_MENU, fnc=mainmenu),
            PluginDescriptor(name=_(name_plug), description=_(title_plug), where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], needsRestart=True, fnc=autostart),
            PluginDescriptor(name=_(name_plug), description=_(title_plug), where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconpic, fnc=main),
            PluginDescriptor(name=_(name_plug), description=_(title_plug), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
