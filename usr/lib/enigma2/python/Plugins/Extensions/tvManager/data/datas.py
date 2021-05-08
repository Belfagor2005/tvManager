#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# from __future__ import print_function
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Label import Label
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.config import *
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import fileExists, copyfile
from enigma import *
from enigma import getDesktop
from os import path, listdir, remove, mkdir, chmod, sys, walk
import base64
import os, gettext
import re
import glob
from twisted.web import client
from twisted.web.client import getPage
from sys import version_info
import ssl
# plugin_path  = os.path.dirname(sys.modules[__name__].__file__)
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/tvManager'
name_plug        = 'TiVuStream Softcam Manager'
data_path    = plugin_path + '/data/'
skin_path    = plugin_path
HD           = getDesktop(0).size()
Agent        = {'User-agent': 'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.0.15) Gecko/2009102815 Ubuntu/9.04 (jaunty) Firefox/3.','Connection': 'Close'}

global isDreamOS
isDreamOS = False

PY3 = version_info[0] == 3
if PY3:
    import urllib.request, urllib.parse, urllib.error
    from urllib.error import URLError
    import http.cookiejar
else:
    from urllib2 import urlopen, Request, URLError
    import urllib2
    import cookielib
    import urllib

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def checkStr(txt):
    if PY3:
        if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        if type(txt) == type(unicode()):
            txt = txt.encode('utf-8')

    return txt

def getUrl(url):
        # if checkInternet():
            try:
                print("Here in getUrl url =", url)
                req = Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                # context = ssl._create_unverified_context()
                # response = urlopen(req, context=context)
                response = checkStr(urlopen(req, timeout = 50))
                link=response.read()
                response.close()
                return link
            except:
                return 'nodata'

try:
    from enigma import eMediaDatabase
    isDreamOS = True
except:
    isDreamOS = False

if HD.width() > 1280:
    if isDreamOS:
        skin_path = plugin_path + '/res/skins/fhd/dreamOs'
    else:
        skin_path = plugin_path + '/res/skins/fhd'
else:
    if isDreamOS:
        skin_path = plugin_path + '/res/skins/hd/dreamOs'
    else:
        skin_path = plugin_path + '/res/skins/hd'

#============='<h1>C: (.*?) (.*?) (.*?) (.*?)\n'======================
dcdlnk1 = 'aHR0cHM6Ly9jY2NhbXN1cHJlbWUuY29tL2NjY2FtZnJlZS9nZXQucGhw'
Link1 = base64.b64decode(dcdlnk1)
dcdlnk2 = 'aHR0cDovL2NjY2FtaXB0di5jby9GUkVFTjEyL25ldzAucGhw'
Link2 = base64.b64decode(dcdlnk2)
dcdlnk3 = 'aHR0cDovL2NjY2FtZ29hbC5jb20vZnJlZTUvZ2V0Mi5waHA='
Link3 = base64.b64decode(dcdlnk3)
dcdlnk4 = 'aHR0cDovL2NjY2Ftc3BvdC5jb20vY2NjYW1mcmVlL2dldC5waHA='
Link4 = base64.b64decode(dcdlnk4)
dcdlnk5 = 'aHR0cDovL2NjY2FtcHJpbWEuY29tL2ZyZWU1L2dldDIucGhw'
Link5 = base64.b64decode(dcdlnk5)
dcdlnk6 = 'aHR0cHM6Ly9jY2NhbXouY28vRlJFRU4xMi9uZXcwLnBocA=='
Link6 = base64.b64decode(dcdlnk6)
dcdlnk7 = 'aHR0cHM6Ly9jY2NhbXouY28vRlJFRS9uZXcwLnBocA=='
Link7 = base64.b64decode(dcdlnk7)
dcdlnk8 = 'aHR0cHM6Ly9jY2NhbWlwdHYuY28vRlJFRU4xMi9uZXcwLnBocA=='
Link8 = base64.b64decode(dcdlnk8)
dcdlnk9 = 'aHR0cDovL2NjY2FtZ29vLmNvbS9mcmVlNS9nZXQyLnBocA=='
Link9 = base64.b64decode(dcdlnk9)
dcdlnk10 = 'aHR0cHM6Ly9jY2NhbXNwb3QuY29tL2NjY2FtZnJlZS9nZXQucGhw'
Link10 = base64.b64decode(dcdlnk10)
dcdlnk11 = 'aHR0cHM6Ly9jY2NhbWZyZWkuY29t'
Link11 = base64.b64decode(dcdlnk11)


sessions = []
config.plugins.tvmanager = ConfigSubsection()
config.plugins.tvmanager.active = ConfigYesNo(default=False)
config.plugins.tvmanager.cfgfile = NoSave(ConfigSelection(default='/etc/CCcam.cfg', choices=[('/etc/CCcam.cfg', _('CCcam')), ('/etc/tuxbox/config/oscam.server', _('Oscam')), ('/etc/tuxbox/config/ncam.server', _('Ncam'))]))
config.plugins.tvmanager.hostaddress = NoSave(ConfigText(default='100.200.300.400'))
config.plugins.tvmanager.port = NoSave(ConfigNumber(default='15000'))
config.plugins.tvmanager.user = NoSave(ConfigText(default='Enter Username', visible_width=50, fixed_size=False))
# config.plugins.tvmanager.passw = NoSave(ConfigText(default='Enter Password', visible_width=50, fixed_size=False))
config.plugins.tvmanager.passw = NoSave(ConfigPassword(default='******', fixed_size=False, censor='*'))
config.plugins.tvmanager.link = NoSave(ConfigSelection(default=Link11, choices=[(Link1, ('Link1')),(Link2, ('Link2')),(Link3, ('Link3')),(Link4, ('Link4')),(Link5, ('Link5')),(Link6, ('Link6')), (Link7, ('Link7')), (Link8, ('Link8')), (Link9, ('Link9')), (Link10, ('Link10')), (Link11, ('Link11'))]))
#======================================================
host =          str(config.plugins.tvmanager.hostaddress.value)
port =          str(config.plugins.tvmanager.port.value)
user =          str(config.plugins.tvmanager.user.value)
password =      str(config.plugins.tvmanager.passw.value)

def putlblcfg():
    global rstcfg
    global buttn
    global putlbl
    putlbl = config.plugins.tvmanager.cfgfile.getValue()
    buttn = ''
    if putlbl == '/etc/CCcam.cfg':
        buttn = _('Write') + ' CCcam'
        rstcfg = 'CCcam.cfg'
    elif putlbl == '/etc/tuxbox/config/oscam.server':
        buttn = _('Write') + ' Oscam'
        rstcfg = 'oscam.server'
    elif putlbl == '/etc/tuxbox/config/ncam.server':
        buttn = _('Write') + ' Ncam'
        rstcfg = 'ncam.server'
putlblcfg()
#======================================================
class tv_config(Screen, ConfigListScreen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + '/tv_config.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.setup_title = _(name_plug)
        self['title'] = Label(_(name_plug))
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'setupActions',
         'ColorActions',
         'VirtualKeyboardActions',
         'MenuActions',
         'InfobarChannelSelection'], {'left': self.keyLeft,
         'right': self.keyRight,
         'ok': self.closex,
         'showVirtualKeyboard': self.KeyText,
         'green': self.green,
         'yellow': self.getcl,
         'blue': self.resetcfg,
         'red': self.closex,
         'cancel': self.closex,
         'back': self.closex}, -1)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_(''))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_green'].hide()
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['info'] = Label('')
        self['description'] = Label('')
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def closex(self):
        self.close()

    def resetcfg(self):
        if config.plugins.tvmanager.active.getValue():
            import shutil
            shutil.copy2(data_path + rstcfg, putlbl)
            os.system('chmod -R 755 %s' % putlbl)
            self.session.open(MessageBox, _('Reset') + ' ' + putlbl, type=MessageBox.TYPE_INFO, timeout=8)

    def showhide(self):
        if config.plugins.tvmanager.active.getValue():
            self['key_green'].setText(buttn)
            self['key_green'].show()
            self['key_yellow'].setText(_('Get Link'))
            self['key_yellow'].show()
            self['key_blue'].setText(_('Reset'))
            self['key_blue'].show()
        else:
            self['key_green'].hide()
            self['key_green'].setText('')
            self['key_yellow'].hide()
            self['key_yellow'].setText('')
            self['key_blue'].hide()
            self['key_blue'].setText('')

    def green(self):
        if config.plugins.tvmanager.active.getValue():
            if putlbl == '/etc/CCcam.cfg':
                self.CCcam()
            elif putlbl == '/etc/tuxbox/config/oscam.server':
                self.Oscam()
            elif putlbl == '/etc/tuxbox/config/ncam.server':
                self.Ncam()

    def layoutFinished(self):
        config.plugins.tvmanager.hostaddress.setValue('100.200.300.400')
        config.plugins.tvmanager.port.setValue('15000')
        config.plugins.tvmanager.user.setValue('Enter Username')
        config.plugins.tvmanager.passw.setValue('Enter Password')
        config.plugins.tvmanager.link.setValue('Link6')
        self.setTitle(self.setup_title)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Activate Insert line in Config File:'), config.plugins.tvmanager.active, _('If Active: Download/Reset Server Config')))
        if config.plugins.tvmanager.active.getValue():
            self.list.append(getConfigListEntry(_('Server Config'), config.plugins.tvmanager.cfgfile, putlbl))
            self.list.append(getConfigListEntry(_('Server Link'), config.plugins.tvmanager.link, _('Select Get Link')))
            self.list.append(getConfigListEntry(_('Server URL'), config.plugins.tvmanager.hostaddress, _('Server Url i.e. 012.345.678.900')))
            self.list.append(getConfigListEntry(_('Server Port'), config.plugins.tvmanager.port, _('Port')))
            self.list.append(getConfigListEntry(_('Server Username'), config.plugins.tvmanager.user, _('Username')))
            self.list.append(getConfigListEntry(_('Server Password'), config.plugins.tvmanager.passw, _('Password')))

        self['config'].list = self.list
        self['config'].setList(self.list)
        self.showhide()
        return

    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        print('current selection:', self['config'].l.getCurrentSelection())
        putlblcfg()
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        print('current selection:', self['config'].l.getCurrentSelection())
        putlblcfg()
        self.createSetup()

    def VirtualKeyBoardCallback(self, callback = None):
        if callback is not None and len(callback):
            self['config'].getCurrent()[1].value = callback
            self['config'].invalidate(self['config'].getCurrent())
        return

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self['config'].getCurrent()[0]

    def getCurrentValue(self):
        return str(self['config'].getCurrent()[1].getText())

    def CCcam(self):
        if config.plugins.tvmanager.cfgfile.value != '/etc/CCcam.cfg':
            self.session.open(MessageBox, _('Select CCcam'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        cfgfile = config.plugins.tvmanager.cfgfile.value
        dest = cfgfile
        host = 'C: ' + str(config.plugins.tvmanager.hostaddress.value)
        port = str(config.plugins.tvmanager.port.value)
        user = str(config.plugins.tvmanager.user.value)
        pasw = str(config.plugins.tvmanager.passw.value)
        if fileExists('/etc/CCcam.cfg'):
            dest = '/etc/CCcam.cfg'
        else:
            self.session.open(MessageBox, _('Please Reset - No File CFG'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        os.system('chmod -R 755 %s' % dest)
        cfgdok = open(dest, 'a')
        cfgdok.write('\n\n' + host + ' ' + port + ' ' + user + ' ' + pasw)
        cfgdok.close()
        self.session.open(MessageBox, _('Server Copy in ') + dest, type=MessageBox.TYPE_INFO, timeout=8)

    def Oscam(self):
        if config.plugins.tvmanager.cfgfile.value != '/etc/tuxbox/config/oscam.server':
            self.session.open(MessageBox, _('Select Oscam'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        cfgfile = config.plugins.tvmanager.cfgfile.value
        dest = cfgfile
        host = str(config.plugins.tvmanager.hostaddress.value)
        port = str(config.plugins.tvmanager.port.value)
        user = str(config.plugins.tvmanager.user.value)
        pasw = str(config.plugins.tvmanager.passw.value)
        if fileExists('/etc/tuxbox/config/oscam.server'):
            dest = '/etc/tuxbox/config/oscam.server'
        else:
            self.session.open(MessageBox, _('Please Reset - No File CFG'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        os.system('chmod -R 755 %s' % dest)
        cfgdok = open(dest, 'a')
        cfgdok.write('\n[reader]\nlabel = Server_' + host + '\nenable= 1\nprotocol = cccam\ndevice = ' + host + ',' + port + '\nuser = ' + user + '\npassword = ' + pasw + '\ninactivitytimeout = 30\ngroup = 3\ncccversion = 2.2.1\ncccmaxhops = 0\nccckeepalive = 1\naudisabled = 1\n\n')
        cfgdok.close()
        self.session.open(MessageBox, _('Server Copy in ') + dest, type=MessageBox.TYPE_INFO, timeout=8)

    def Ncam(self):
        if config.plugins.tvmanager.cfgfile.value != '/etc/tuxbox/config/ncam.server':
            self.session.open(MessageBox, _('Select Ncam'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        if not os.path.exists('/etc/tuxbox/config'):
            os.system('mkdir /etc/tuxbox/config')
        cfgfile = config.plugins.tvmanager.cfgfile.value
        dest = cfgfile
        host = str(config.plugins.tvmanager.hostaddress.value)
        port = str(config.plugins.tvmanager.port.value)
        user = str(config.plugins.tvmanager.user.value)
        pasw = str(config.plugins.tvmanager.passw.value)
        if fileExists('/etc/tuxbox/config/ncam.server'):
            dest = '/etc/tuxbox/config/ncam.server'
        else:
            self.session.open(MessageBox, _('Please Reset - No File CFG'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        os.system('chmod -R 755 %s' % dest)
        cfgdok = open(dest, 'a')
        cfgdok.write('\n[reader]\nlabel = Server_' + host + '\nenable= 1\nprotocol = cccam\ndevice = ' + host + ',' + port + '\nuser = ' + user + '\npassword = ' + pasw + '\ngroup = 3\ncccversion = 2.0.11\ndisablecrccws_only_for= 0500:032830\ncccmaxhops= 1\nccckeepalive= 1\naudisabled = 1\n\n')
        cfgdok.close()
        self.session.open(MessageBox, _('Server Copy in ') + dest, type=MessageBox.TYPE_INFO, timeout=8)

    def getcl(self):
        Lnk = str(config.plugins.tvmanager.link.value)
        data = getUrl(Lnk)
        print('=== Lnk ==== ', data)
        self.load_getcl(data)

    def load_getcl(self, data):
        url1 = re.findall('<h1>.*?C: (.*?) (.*?) (.*?) (.*?)\n', data)
        print('===========data=========', url1)

        if url1 != '':
            for h, p, u, pw in url1:
                print(h, p, u, pw)
                host = h
                port = p
                user = u
                password = pw
                password = password.replace('</h1>','')
            # if config.plugins.tvmanager.active.getValue():
                config.plugins.tvmanager.hostaddress.setValue(host)
                config.plugins.tvmanager.port.setValue(port)
                config.plugins.tvmanager.user.setValue(user)
                config.plugins.tvmanager.passw.setValue(password)
                self.createSetup()
        else:
            return
