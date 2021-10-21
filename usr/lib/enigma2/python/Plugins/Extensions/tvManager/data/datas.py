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
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
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
from random import choice
global skin_path
import six
from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
from six.moves.urllib.error import HTTPError, URLError
from six.moves.urllib.request import urlretrieve
# plugin_path = os.path.dirname(sys.modules[__name__].__file__)
# iconpic = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/{}".format('logo.png'))
# plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/tvManager'
# name_plug        = 'TiVuStream Softcam Manager'
# data_path    = plugin_path + '/data/'
name_plug = 'TiVuStream Softcam Manager'
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/")
data_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/data")
skin_path    = plugin_path

try:
    import http.cookiejar
except:
    import cookielib
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def checkStr(txt):
    if six.PY3:
        if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        if type(txt) == type(unicode()):
            txt = txt.encode('utf-8')

    return txt

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

def getUrl(url):
    try:
        import requests
        link = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'}).text
        print('link1: ', link)
        return link
    except ImportError:
        req = Request(url)

        req.add_header('User-Agent',RequestAgent())
        response = urlopen(req, None, 3)
        link = response.read()
        response.close()
        print('link2: ', link)
        return link
    except:
        e = URLError #, e:
        print('We failed to open "%s".' % url)
        if hasattr(e, 'code'):
            print('We failed with error code - %s.' % e.code)
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        return
    return

HD = getDesktop(0).size()
if HD.width() > 1280:
    # skin_path=res_plugin_path + 'skins/fhd/'
    skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/skins/fhd/")
else:
    # skin_path=res_plugin_path + 'skins/hd/'
    skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/skins/hd/")
if os.path.isfile('/var/lib/dpkg/status'):
    skin_path=skin_path + 'dreamOs/'

#============='<h1>C: (.*?) (.*?) (.*?) (.*?)\n'======================
Link1 = 'http://cccamsupreme.com/cccamfree/get.php'
Link5 = 'http://cccamprima.com/free5/get2.php'
Link11 = 'http://cccamfrei.com/free/get.php'
Link8 = 'https://cccamiptv.club/it/free-cccam/'
Link9 = 'http://cccamgoo.com/free5/get2.php'
Link2 = 'http://cccamas.com/free/get.php'
Link3 = 'http://cccamprime.com/cccam48h.php'
Link4 = 'http://cccam-premium.com/free-cccam/'
Link6 = 'http://cccamx.com/v2/getCode.php'
Link7 = 'http://iptvcccam.co/cccamfree/get.php'
Link10 = 'https://cccamia.com/free-cccam/'

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
        data = config.plugins.tvmanager.link.value
        data = getUrl(data)
        if six.PY3:
            data = six.ensure_str(data)
        print('=== Lnk ==== ', data)
        self.load_getcl(data)

    def load_getcl(self, data):
        url1 = re.findall('<h1>.*?C: (.*?) (.*?) (.*?) (.*?)\n', data)
        print('===========data=========', url1)
        if url1 != '':
            for h, p, u, pw in url1:
                print(h, p, u, pw)
                host = checkStr(h)
                port = checkStr(p)
                user = checkStr(u)
                password = checkStr(pw)
                password = password.replace('</h1>','')
            # if config.plugins.tvmanager.active.getValue():
                config.plugins.tvmanager.hostaddress.setValue(host)
                config.plugins.tvmanager.port.setValue(port)
                config.plugins.tvmanager.user.setValue(user)
                config.plugins.tvmanager.passw.setValue(password)
                self.createSetup()
        else:
            return





