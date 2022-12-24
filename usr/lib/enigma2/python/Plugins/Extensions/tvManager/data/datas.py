# #!/usr/bin/env python
# -*- coding: UTF-8 -*-

# --------------------#
#  coded by Lululla  #
#   skin by MMark    #
#     25/09/2022     #
#      No Coppy      #
# --------------------#
from __future__ import print_function
# import base64
# import six
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.config import ConfigNumber, ConfigSelection, ConfigYesNo
from Components.config import ConfigSubsection, ConfigPassword
from Components.config import config, ConfigText
from Components.config import getConfigListEntry, NoSave
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import fileExists
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from random import choice
import os
import re
import ssl
import sys
global skin_path


def DreamOS():
    DreamOS = False
    if os.path.exists('/var/lib/dpkg/status'):
        DreamOS = True
        return DreamOS


PY3 = sys.version_info.major >= 3
if PY3:
    unicode = str
    unichr = chr
    long = int
    PY3 = True


def b64decoder(s):
    """Add missing padding to string and return the decoded base64 string."""
    import base64
    s = str(s).strip()
    try:
        # return base64.b64decode(s)
        outp = base64.b64decode(s)
        print('outp1 ', outp)
        if PY3:
            outp = outp.decode('utf-8')
            print('outp2 ', outp)
        return outp

    except TypeError:
        padding = len(s) % 4
        if padding == 1:
            print("Invalid base64 string: {}".format(s))
            return ''
        elif padding == 2:
            s += b'=='
        elif padding == 3:
            s += b'='
        outp = base64.b64decode(s)
        print('outp1 ', outp)
        if PY3:
            outp = outp.decode('utf-8')
            print('outp2 ', outp)
        return outp


name_plug = 'TiVuStream Softcam Manager'
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/")
data_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/data/")
skin_path = plugin_path


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def getDesktopSize():
    from enigma import getDesktop
    s = getDesktop(0).size()
    return (s.width(), s.height())


def isFHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] == 1920


def checkStr(txt):
    if PY3:
        if isinstance(type(txt), type(bytes())):
        # if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        # if type(txt) == type(unicode()):
        if isinstance(type(txt), type(unicode())):
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
    if sys.version_info.major == 3:
        import urllib.request as urllib2
    elif sys.version_info.major == 2:
        import urllib2
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
    r = urllib2.urlopen(req, None, 15)
    link = r.read()
    r.close()
    content = link
    if str(type(content)).find('bytes') != -1:
        try:
            content = content.decode("utf-8")
        except Exception as e:
            print("Error: %s." % str(e))
    return content


skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/skins/hd/")


if isFHD():
    # skin_path=res_plugin_path + 'skins/fhd/'
    skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/res/skins/fhd/")

if DreamOS():
    skin_path = skin_path + 'dreamOs/'

Serverlive = [
    ('aHR0cHM6Ly9ib3NzY2NjYW0uY28vVGVzdC5waHA=', 'Server01'),
    ('aHR0cHM6Ly9jY2NhbWlwdHYuY2x1Yi9mcmVlLWNjY2FtLw==', 'Server02'),
    ('aHR0cHM6Ly9jY2NhbS1wcmVtaXVtLmNvbS9mcmVlLWNjY2FtLw==', 'Server03'),
    ('aHR0cHM6Ly9pcHR2LTE1ZGF5cy5ibG9nc3BvdC5jb20=', 'Server04'),
    ('aHR0cHM6Ly9jY2NhbWVhZ2xlLmNvbS9mY2NhbS8=', 'Server05'),
    ('aHR0cDovL2NjY2FtcHJpbWEuY29tL2ZyZWU1L2dldDIucGhw', 'Server06'),
    ('aHR0cHM6Ly9jY2NhbWlwdHYuY2x1Yi9mcmVlLWNjY2Ft', 'Server07'),
    ('aHR0cHM6Ly9jY2NhbWZyZWkuY29tL2ZyZWUvZ2V0LnBocA==', 'Server08'),
    ('aHR0cHM6Ly9jY2NhbS5uZXQvZnJlZQ==', 'Server09'),
    ('aHR0cHM6Ly90ZXN0Y2xpbmUuY29tL2ZyZWUtY2NjYW0tc2VydmVyLnBocA==', 'Server10'),
    ('aHR0cHM6Ly9jY2NhbWlhLmNvbS9mcmVlLWNjY2FtLw==', 'Server11'),
    ]

cfgcam = [('/etc/CCcam.cfg', 'CCcam'),
          ('/etc/tuxbox/config/oscam.server', 'Oscam'),
          ('/etc/tuxbox/config/oscam-emu/oscam.server', 'oscam-emu'),
          ('/etc/tuxbox/config/ncam.server', 'Ncam'),
          ('/etc/tuxbox/config/gcam.server', 'Gcam'),
          ('/etc/tuxbox/config/Oscamicam/oscam.server', 'Oscamicam')]

config.plugins.tvmanager = ConfigSubsection()
config.plugins.tvmanager.active = ConfigYesNo(default=False)
config.plugins.tvmanager.Server = NoSave(ConfigSelection(choices=Serverlive))  # , default=Server1))
# config.plugins.tvmanager.cfgfile = NoSave(ConfigSelection(default='/etc/CCcam.cfg', choices=[('/etc/CCcam.cfg', _('CCcam')), ('/etc/tuxbox/config/oscam.server', _('Oscam')), ('/etc/tuxbox/config/ncam.server', _('Ncam'))]))
config.plugins.tvmanager.cfgfile = NoSave(ConfigSelection(choices=cfgcam))
config.plugins.tvmanager.hostaddress = NoSave(ConfigText(default='100.200.300.400'))
config.plugins.tvmanager.port = NoSave(ConfigNumber(default=15000))
config.plugins.tvmanager.user = NoSave(ConfigText(default='Enter Username', visible_width=50, fixed_size=False))
config.plugins.tvmanager.passw = NoSave(ConfigPassword(default='******', fixed_size=False, censor='*'))

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
    buttn = ''
    if putlbl == '/etc/CCcam.cfg':
        buttn = _('Write') + ' CCcam'
        rstcfg = 'CCcam.cfg'
    elif putlbl == '/etc/tuxbox/config/oscam.server':
        buttn = _('Write') + ' Oscam'
        rstcfg = 'oscam.server'
    elif putlbl == '/etc/tuxbox/config/gcam.server':
        buttn = _('Write') + ' Gcam'
        rstcfg = 'gcam.server'
    elif putlbl == '/etc/tuxbox/config/oscam-emu/oscam.server':
        buttn = _('Write') + ' OscamEmu'
        rstcfg = 'oscam.server'
    elif putlbl == '/etc/tuxbox/config/Oscamicam/oscam.server':
        buttn = _('Write') + ' Oscamicam'
        rstcfg = 'oscam.server'
    elif putlbl == '/etc/tuxbox/config/ncam.server':
        buttn = _('Write') + ' Ncam'
        rstcfg = 'ncam.server'


putlblcfg()


class tv_config(Screen, ConfigListScreen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tv_config.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.setup_title = (name_plug)
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self['title'] = Label(_(name_plug))
        self["paypal"] = Label()
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
        self.createSetup()
        # self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.layoutFinished)
        # self.onFirstExecBegin.append(self.layoutFinished)

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
            elif putlbl == '/etc/tuxbox/config/oscam-emu/oscam.server':
                self.Oscam()
            elif putlbl == '/etc/tuxbox/config/Oscamicam/oscam.server':
                self.Oscam()
            elif putlbl == '/etc/tuxbox/config/ncam.server':
                self.Ncam()

    def paypal2(self):
        conthelp = "If you like what I do you\n"
        conthelp += " can contribute with a coffee\n\n"
        conthelp += "scan the qr code and donate € 1.00"
        return conthelp

    def layoutFinished(self):
        self.setTitle(self.setup_title)
        paypal = self.paypal2()
        self["paypal"].setText(paypal)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Activate Insert line in Config File:'), config.plugins.tvmanager.active, _('If Active: Download/Reset Server Config')))
        if config.plugins.tvmanager.active.getValue():
            self.list.append(getConfigListEntry(_('Server Config'), config.plugins.tvmanager.cfgfile, putlbl))
            self.list.append(getConfigListEntry(_('Server Link'), config.plugins.tvmanager.Server, _('Select Get Link')))
            self.list.append(getConfigListEntry(_('Server URL'), config.plugins.tvmanager.hostaddress, _('Server Url i.e. 012.345.678.900')))
            self.list.append(getConfigListEntry(_('Server Port'), config.plugins.tvmanager.port, _('Port')))
            self.list.append(getConfigListEntry(_('Server Username'), config.plugins.tvmanager.user, _('Username')))
            self.list.append(getConfigListEntry(_('Server Password'), config.plugins.tvmanager.passw, _('Password')))

        self['config'].list = self.list
        self['config'].l.setList(self.list)
        # self['config'].setList(self.list)
        self.showhide()
        # return

    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        print('current selection:', self['config'].l.getCurrentSelection())
        putlblcfg()
        self.createSetup()
        self.getcl()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        print('current selection:', self['config'].l.getCurrentSelection())
        putlblcfg()
        self.createSetup()
        self.getcl()

    def VirtualKeyBoardCallback(self, callback=None):
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
        global host, port, user, passw
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
        global host, port, user, passw
        # if config.plugins.tvmanager.cfgfile.value != '/etc/tuxbox/config/oscam.server':
            # self.session.open(MessageBox, _('Select Oscam'), type=MessageBox.TYPE_INFO, timeout=5)
            # return
        cfgfile = config.plugins.tvmanager.cfgfile.value
        dest = cfgfile
        host = str(config.plugins.tvmanager.hostaddress.value)
        port = str(config.plugins.tvmanager.port.value)
        user = str(config.plugins.tvmanager.user.value)
        pasw = str(config.plugins.tvmanager.passw.value)
        if not fileExists(dest):
            # dest = '/etc/tuxbox/config/oscam.server'
        # else:
            self.session.open(MessageBox, _('Please Reset - No File CFG'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        os.system('chmod -R 755 %s' % dest)
        cfgdok = open(dest, 'a')
        cfgdok.write('\n[reader]\nlabel = Server_' + host + '\nenable= 1\nprotocol = cccam\ndevice = ' + host + ',' + port + '\nuser = ' + user + '\npassword = ' + pasw + '\ninactivitytimeout = 30\ngroup = 3\ncccversion = 2.2.1\ncccmaxhops = 0\nccckeepalive = 1\naudisabled = 1\n\n')
        cfgdok.close()
        self.session.open(MessageBox, _('Server Copy in ') + dest, type=MessageBox.TYPE_INFO, timeout=8)

    def Ncam(self):
        global host, port, user, passw
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
        try:
            data1 = str(config.plugins.tvmanager.Server.value)
            print(data1)
            data = b64decoder(data1)
            print('data2 ', data)
            try:
                data = getUrl(data)
                if PY3:
                    import six
                    data = six.ensure_str(data)
                print('=== Lnk ==== ', data)
                self.load_getcl(data)
            except Exception as e:
                print('getcl error: ', str(e))
        except Exception as e:
            print('error on host', str(e))

    def load_getcl(self, data):
        global host, port, user, passw
        try:
            data = checkStr(data)
            url1 = re.findall('<h1>C: (.+?) (.+?) (.+?) (.*?)\n', data)
            if 'testcline' in data.lower():
                # <div>C: s2.livetvip.com 9626 gf023 pon</div>
                # <div>C: top2.supercline.net 18802 paisilvpenedo 89682009</div>
                # <div>C: top1.supercline.net 18801 paisilvpenedo 89682009</div>
                url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)</d', data)

            elif 'cccameagle' in data.lower():
                # >C: free1.cccameagle.com 13065 yf24n cccameagle</h2>
                url1 = re.findall('>C: (.+?) (.+?) (.+?) (.+?)</h2>', data)
                
            elif 'cccamfrei' in data.lower():
                # >C: free1.cccameagle.com 13065 yf24n cccameagle</h2>
                url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)</h2>', data)
                
            elif 'cccamprime' in data.lower():
                # <br>Cline : C: s2.cccamprime.com 14808 50853334 cccamprime<br>
                url1 = re.findall('Cline : C: (.+?) (.+?) (.+?) (.+?).*?Host', data)
                url1 = url1.replace('<br><br>', '')

            elif 'cccamprima.com' in data.lower():
                # <div>C: egygold.co 51002 jsp271 88145</div>
                url1 = re.findall('<h1>C: (.+?) (.+?) (.+?) (.+?)\n', data)

            elif 'iptvcccam' in data.lower():
                # <h1>C: free.iptvcccam.co 2021 tcsi iptvcccam.co        </h1>
                url1 = re.findall('C: (.+?) (.+?) (.+?) (*?).*?</h1>', data)

            elif 'premium' in data.lower():
                # <h3 style="color:red;">
                url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)\n', data)

            elif 'cccamia' in data:
                # C: free.CCcamia.com 18000 e4xd88 CCcamia.com
                url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)\n', data)

            elif 'cccameurop' in data.lower():
                # ">C:  873259 527418</strong></H3><br><br>
                # C: cccameurop.com 19000
                # </div>
                url1 = re.findall('C: (.+?) (.+?)</', data)
                # url1 = 'cccameurop.com 19000' + url1[0] + url1[1]
            elif 'cccamx' in data.lower():
                # ">
                url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)\n', data)
            elif 'cccamiptv' in data.lower():
                # <h3 style="color:red;">
                # C: free.cccamiptv.club 13100 8n1gv9 cccamiptv.club
                # </h3>
                url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)\n.*?</h3>', data)
            elif 'FREEN12' in data.lower():
                # <h3 style="color:red;">
                # C: free.cccamiptv.co 13100 9d0of5 cccamiptv.co
                # </h3>
                url1 = re.findall('<h1>\nC: (.+?) (.+?) (.+?) (.+?)\n', data)
            elif 'history' in data.lower():
                url1 = re.findall('of the line">C: (.+?) (.+?) (.+?) (.+?)</a>.*?title="CCcam server online and valid"></span>', data)

            elif 'store' in data.lower():
                # view-source:http://cccamstore.tv/free-server.php
                # <center><strong>C: free.cccamstore.tv 12892 93t60rhi cccamstore.tv <br>
                url1 = re.findall('<center><strong>C: (.+?) (.+?) (.+?) (.+?) <br>', data)

            elif 'cccam.net' in data.lower():
                # >C: free1.cccameagle.com 13065 yc8sn cccameagle</h2>
                url1 = re.findall('span><b>C: (.+?) (.+?) (.+?) (.+?)</b>', data)

            elif 'cccameagle' in data.lower():
                # >C: free1.cccameagle.com 13065 yc8sn cccameagle</h2>
                url1 = re.findall('>C: (.+?) (.+?) (.+?) (.+?)</h2>', data)

            elif 'rogcam' in data.lower():
                url1 = re.findall('bg-primary"> C: (.+?) (.+?) (.+?) (.+?) </span>', data)

            elif 'cccambird' in data.lower():
                # >C: t2.cccambird.com 14800 51190374 cccambird</th>
                url1 = re.findall('">C: (.+?) (.+?) (.+?) (.+?)</th></tr>', data)

            elif 'bosscccam' in data.lower():
                # <strong>c: bosscccam.nowddns.com 26210 L2O000mhI8 BosS-ccCAm.coM</strong></p>
                url1 = re.findall('<strong>c: (.+?) (.+?) (.+?) (.+?)</strong', data)

            elif '15days' in data.lower():
                # ">C: s7.cccambird.com 12550 72953333 cccambird</th></tr>
                url1 = re.findall('">C: (.*?) (.*?) (.*?) (.+?)</th></tr>', data)
            print('===========data=========', url1)
            if url1 != '':
                host = ''
                port = ''
                user = ''
                password = ''
                if 'cccameurop' in data.lower():
                    for u, pw in url1:
                        # url1 = 'cccameurop.com 19000' + url1[0] + url1[1]
                        host = 'cccameurop.com'
                        port = '19000'
                        user = str(u)
                        password = str(pw)
                        print('Host: %s - Port: %s - User: %s - Password: %s' % (host, port, user, password))
                else:
                    for h, p, u, pw in url1:
                        print(h, p, u, pw)
                        host = str(h)
                        port = str(p)
                        user = str(u)
                        password = str(pw)
                        password = password.replace('</h1>', '')
                        password = password.replace('</div>', '')
                # if config.plugins.tvmanager.active.getValue():
                config.plugins.tvmanager.hostaddress.setValue(host)
                config.plugins.tvmanager.port.setValue(port)
                config.plugins.tvmanager.user.setValue(user)
                config.plugins.tvmanager.passw.setValue(password)
                self.createSetup()
            else:
                return
        except Exception as e:
            print('error on string cline', str(e))
