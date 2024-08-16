# #!/usr/bin/env python
# -*- coding: UTF-8 -*-

# --------------------#
#  coded by Lululla   #
#   skin by MMark     #
#     10/07/2023      #
#      No Coppy       #
# --------------------#
from __future__ import print_function
from .. import _, paypal
from ..plugin import currversion, runningcam
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.config import (
    ConfigNumber,
    ConfigSelection,
    ConfigYesNo,
    ConfigSubsection,
    ConfigPassword,
    config,
    ConfigText,
    getConfigListEntry,
    NoSave,
)
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import (fileExists, resolveFilename, SCOPE_PLUGINS)
from Components.Sources.StaticText import StaticText
from random import choice
from enigma import (eTimer, getDesktop)
import base64
import os
import re
import ssl
import sys
import subprocess
import codecs

global skin_path

sss = 'aHR0cHM6Ly9wYXN0ZWJpbi5jb20vcmF3L1U0ZU02RGpW'
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
        outp = base64.b64decode(s)
        print('outp1 ', outp)
        if PY3:
            outp = outp.decode('utf-8')
            print('outp2 ', outp)
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
            print('outp3 ', outp)
    return outp


# currversion = '2.3'
name_plug = 'TiVuStream Softcam Manager'
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/tvManager/")
data_path = os.path.join(plugin_path, 'data/')
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
            txt = txt.decode('utf-8')
    else:
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


# =============== SCREEN PATH SETTING
screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    skin_path = plugin_path + '/res/skins/uhd/'
elif screenwidth.width() == 1920:
    skin_path = plugin_path + '/res/skins/fhd/'
else:
    skin_path = plugin_path + '/res/skins/hd/'
if os.path.exists('/var/lib/dpkg/info'):
    skin_path = skin_path + '/dreamOs/'


def cccamPath():
    import os
    cmd = 'find /usr -name "CCcam.cfg"'
    res = os.popen(cmd).read()
    if res == '':
        cmd = 'find /var -name "CCcam.cfg"'
        res = os.popen(cmd).read()
        if res == '':
            cmd = 'find /etc -name "CCcam.cfg"'
            res = os.popen(cmd).read()
            if res == '':
                try:
                    folders = os.listdir('/etc/tuxbox/')
                    for folder in folders:
                        if folder.startswith('oscam'):
                            cmd = 'find /etc/tuxbox/config/' + folder + ' -name "CCcam.cfg"'
                            res = os.popen(cmd).read()
                            return '/etc/tuxbox/config/' + folder + "CCcam.cfg"
                        if res == '':
                            return "/etc/CCcam.cfg"
                except:
                    return "/etc/CCcam.cfg"
            else:
                return "/etc/CCcam.cfg"
        else:
            return "/var/CCcam.cfg"
    else:
        return "/usr/CCcam.cfg"
    return "/etc/CCcam.cfg"


Serverlive = [
    ('aHR0cHM6Ly9ib3NzY2NjYW0uY28vVGVzdC5waHA=', 'Server01'),
    ('aHR0cHM6Ly9pcHR2LTE1ZGF5cy5ibG9nc3BvdC5jb20=', 'Server02'),
    ('aHR0cHM6Ly9jY2NhbWlhLmNvbS9mcmVlLWNjY2FtLw==', 'Server03'),
    ('aHR0cHM6Ly9jY2NhbS5uZXQvZnJlZWNjY2Ft', 'Server04'),
    ('aHR0cHM6Ly9jY2NhbXNhdGUuY29tL2ZyZWU=', 'Server05'),
    ('aHR0cHM6Ly9jY2NhbXguY29tL2ZyZWUtY2NjYW0=', 'Server06'),
    ('aHR0cHM6Ly9jY2NhbS1wcmVtaXVtLmNvL2ZyZWUtY2NjYW0v', 'Server07'),
    ('aHR0cHM6Ly9jY2NhbS5uZXQvZnJlZWNjY2Ft', 'Server08'),
    ('aHR0cHM6Ly9jY2NhbWZyZWUuY28vZnJlZS9nZXQucGhw', 'Server9'),
    ('aHR0cHM6Ly9jY2NhbWZyZWkuY29tL2ZyZWUvZ2V0LnBocA==', 'Server10'),
    ('aHR0cHM6Ly9jY2NhbWlwdHYuY2x1Yi9mcmVlLWNjY2FtLw==', 'Server11'),
]

# cfgcam = [(cccamPath(), 'CCcam'),
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
config.plugins.tvmanager.hostaddress = NoSave(ConfigText(default='127.0.0.1'))
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
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'tv_config.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = (name_plug)
        self['title'] = Label(_(name_plug))
        # self["key_red"] = Label(_("Back"))
        # self["key_green"] = Label("")
        # self["key_yellow"] = Label("")
        # self["key_blue"] = Label("")
        if os.path.exists('/usr/lib/enigma2/python/Plugins/PLi'):
            self["key_red"] = StaticText(_("Back"))
            self["key_green"] = StaticText("")
            self["key_yellow"] = StaticText("")
            self["key_blue"] = StaticText("")
            # self["key_red"] = Button(_("Back"))
            # self["key_green"] = Button("")
            # self["key_yellow"] = Button("")
            # self["key_blue"] = Button("")
            # self["key_red"] = Label(_("Back"))
            # self["key_green"] = Label("")
            # self["key_yellow"] = Label("")
            # self["key_blue"] = Label("")
        else:
            self["key_red"] = Label(_("Back"))
            self["key_green"] = Label("")
            self["key_yellow"] = Label("")
            self["key_blue"] = Label("")

        self['description'] = Label('')
        self['info'] = Label(_('Wait please...'))
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self["paypal"] = Label()
        # self.runningcam = None
        # self.runningcam = self.readCurrent()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'DirectionActions',
                                     'ColorActions',
                                     'VirtualKeyboardActions',
                                     'MenuActions',
                                     'EPGSelectActions',
                                     'InfobarChannelSelection'], {'left': self.keyLeft,
                                                                  'right': self.keyRight,
                                                                  'ok': self.closex,
                                                                  'showVirtualKeyboard': self.KeyText,
                                                                  'green': self.green,
                                                                  'yellow': self.sendemm,
                                                                  'blue': self.resetcfg,
                                                                  'red': self.closex,
                                                                  'cancel': self.closex,
                                                                  'info': self.infomsg,
                                                                  'back': self.closex}, -1)
        '''
        # if config.plugins.tvmanager.active.value is True:
            # self['key_green'].setText(buttn)
            # self['key_yellow'].setText(_('Get Link'))
            # self['key_blue'].setText(_('Reset'))
        # else:
            # self['key_green'].setText('Force Emm Send')
            # self['key_yellow'].setText('Check Emm Send')
            # self['key_blue'].setText('')
        '''
        self.createSetup()
        if self.selectionChanged not in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        self.selectionChanged()
        self.onLayoutFinish.append(self.layoutFinished)
        # self.onLayoutFinish.append(self.showhide)
        # self.onShown.append(self.showhide)

    def layoutFinished(self):
        self.setTitle(self.setup_title)
        payp = paypal()
        self["paypal"].setText(payp)
        # self.showhide()

        # self.runningcam = self.readCurrent()
        # print('runningcam 7 =', self.runningcam)

        self['info'].setText(_('Select Your Choice'))

    def infomsg(self):
        self.session.open(MessageBox, _("tvManager by Lululla\nV.%s\nInstall Cam Software\nForum Support www.corvoboys.org\n") % currversion,  MessageBox.TYPE_INFO, timeout=4)

    def sendemm(self):
        if config.plugins.tvmanager.active.value is True:
            self.getcl()
        else:
            try:
                print('runningcam1=', runningcam)
                if runningcam is None:
                    return
                # if runningcam == 'oscam' or runningcam == 'ncam':
                if runningcam == 'oscam':
                    cmd = 'ps -T'
                    res = os.popen(cmd).read()
                    print('res: ', res)
                    if 'oscam' in res.lower() or 'icam' in res.lower() or 'ncam' in res.lower() or 'gcam' in res.lower():
                        print('oscam exist')
                        msg = []
                        msg.append(_("\n....\n.....\n"))
                        self.cmd1 = '/usr/lib/enigma2/python/Plugins/Extensions/tvManager/data/emm_sender.sh'  # '/usr/lib/enigma2/python/Plugins/Extensions/tvManager/data/emm_sender.sh'
                        from os import access, X_OK
                        if not access(self.cmd1, X_OK):
                            os.chmod(self.cmd1, 493)
                        # os.system(self.cmd1)
                        # subprocess.check_output(['bash', self.cmd1])
                        try:
                            subprocess.check_output(['bash', self.cmd1])
                            self.session.open(MessageBox, _('Card Updated!'), MessageBox.TYPE_INFO, timeout=5)
                        except subprocess.CalledProcessError as e:
                            print(e.output)
                            self.session.open(MessageBox, _('Card Not Updated!'), MessageBox.TYPE_INFO, timeout=5)

                        os.system('sleep 5')
                        if not os.path.exists('/tmp/emm.txt'):
                            # import wget
                            # outp = base64.b64decode(sss)
                            # url = str(outp)
                            cmmnd = "wget --no-check-certificate -U 'Enigma2 - tvmanager Plugin' -c 'https://pastebin.com/raw/U4eM6DjV' -O '/tmp/emm.txt'"
                            # wget.download(url, '/tmp/emm.txt')
                            os.system(cmmnd)
                        if os.path.exists('/tmp/emm.txt'):
                            msg.append(_("READ EMM....\n"))
                            with open('/tmp/emm.txt') as f:
                                f = f.read()
                                if f.startswith('82708'):
                                    msg.append(_("CURRENT EMM IS:\n"))
                                    msg.append(f)
                                    msg.append(_("\nCurrent Emm saved to /tmp/emm.txt"))
                                else:
                                    msg.append('No Emm Read!')
                            msg = (" %s " % _("\n")).join(msg)
                            self.session.open(MessageBox, _("Please wait, %s.") % msg, MessageBox.TYPE_INFO, timeout=10)
                        else:
                            self.session.open(MessageBox, _("File no exist /tmp/emm.txt"), MessageBox.TYPE_INFO, timeout=10)
                else:
                    self.session.openWithCallback(self.callMyMsg, MessageBox, _('The Cam is not active, send the command anyway?'), MessageBox.TYPE_YESNO)
            except Exception as e:
                print('error on emm', str(e))

    def callMyMsg(self, answer=False):
        if answer:
            msg = []
            msg.append(_("\n....\n.....\n"))
            self.cmd1 = '/usr/lib/enigma2/python/Plugins/Extensions/tvManager/data/emm_sender.sh'
            from os import access, X_OK
            if not access(self.cmd1, X_OK):
                os.chmod(self.cmd1, 493)
            try:
                subprocess.check_output(['bash', self.cmd1])
                self.session.open(MessageBox, _('Card Updated!'), MessageBox.TYPE_INFO, timeout=5)
            except subprocess.CalledProcessError as e:
                print(e.output)
                self.session.open(MessageBox, _('Card Not Updated!'), MessageBox.TYPE_INFO, timeout=5)
            os.system('sleep 5')
            if not os.path.exists('/tmp/emm.txt'):
                outp = base64.b64decode(sss)
                url = str(outp)
                # cmd = 'wget -q --no-use-server-timestamps --no-clobber --timeout=5' + url + ' -O /tmp/emm.txt'
                try:
                    # subprocess.check_output(['bash', cmd])
                    subprocess.call(["wget", "-q", "--no-use-server-timestamps", "--no-clobber", "--timeout=5", url, "-O", '/tmp/emm.txt'])
                except subprocess.CalledProcessError as e:
                    print(e.output)
            if os.path.exists('/tmp/emm.txt'):
                msg.append(_("READ EMM....\n"))
                with open('/tmp/emm.txt') as f:
                    f = f.read()
                    if f.startswith('82708'):
                        msg.append(_("CURRENT EMM IS:\n"))
                        msg.append(f)
                        msg.append(_("\nCurrent Emm saved to /tmp/emm.txt"))
                    else:
                        msg.append('No Emm')
                msg = (" %s " % _("\n")).join(msg)
                self.session.open(MessageBox, _("Please wait, %s.") % msg, MessageBox.TYPE_INFO, timeout=10)
            else:
                self.session.open(MessageBox, _("No Action!\nFile no exist /tmp/emm.txt"), MessageBox.TYPE_INFO, timeout=5)
        else:
            self.session.open(MessageBox, _("Command Cancelled"), MessageBox.TYPE_INFO, timeout=5)

    def closex(self):
        self.close()

    def resetcfg(self):
        if config.plugins.tvmanager.active.value is True:
            import shutil
            shutil.copy2(data_path + rstcfg, putlbl)
            os.system('chmod -R 755 %s' % putlbl)
            self.session.open(MessageBox, _('Reset') + ' ' + putlbl, type=MessageBox.TYPE_INFO, timeout=8)

    def showhide(self):
        if config.plugins.tvmanager.active.value is True:
            self['key_green'].setText(buttn)
            self['key_yellow'].setText(_('Get Link'))
            self['key_blue'].setText(_('Reset'))
        else:
            self['key_green'].setText('Force Emm Send')
            self['key_yellow'].setText('Check Emm Send')
            self['key_blue'].setText('')
        return

    def green(self):
        if config.plugins.tvmanager.active.value is True:
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
            else:
                return
        else:
            if 'oscam' in str(runningcam):  # or 'movicam' in str(self.runningcam):
                msg = []
                msg.append(_("\n....\n.....\n"))
                self.cmd1 = data_path + 'emm_sender.sh'
                from os import access, X_OK
                if not access(self.cmd1, X_OK):
                    os.chmod(self.cmd1, 493)
                try:
                    subprocess.check_output(['bash', self.cmd1])
                except subprocess.CalledProcessError as e:
                    print(e.output)
                os.system('sleep 3')
                if os.path.exists('/tmp/emm.txt'):
                    msg.append(_("READ EMM....\n"))
                    with open('/tmp/emm.txt') as f:
                        f = f.read()
                        if f.startswith('82708'):
                            msg.append(_("CURRENT EMM IS:\n"))
                            msg.append(f)
                            msg.append(_("\nCurrent Emm saved to /tmp/emm.txt"))
                        else:
                            msg.append('No Emm')
                    msg = (" %s " % _("\n")).join(msg)
                    self.session.open(MessageBox, _("Please wait, %s.") % msg, MessageBox.TYPE_INFO, timeout=10)
                else:
                    self.session.open(MessageBox, _("No Action!\nFile no exist /tmp/emm.txt"), MessageBox.TYPE_INFO, timeout=5)
            else:
                self.session.open(MessageBox, _("No Action!\nOscam not active"), MessageBox.TYPE_INFO, timeout=5)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Activate Insert line in Config File:'), config.plugins.tvmanager.active, _('If Active: Download/Reset Server Config')))
        if config.plugins.tvmanager.active.value:
            self.list.append(getConfigListEntry(_('Server Config'), config.plugins.tvmanager.cfgfile, putlbl))
            self.list.append(getConfigListEntry(_('Server Link'), config.plugins.tvmanager.Server, _('Select Get Link')))
            self.list.append(getConfigListEntry(_('Server URL'), config.plugins.tvmanager.hostaddress, _('Server Url i.e. 012.345.678.900')))
            self.list.append(getConfigListEntry(_('Server Port'), config.plugins.tvmanager.port, _('Port')))
            self.list.append(getConfigListEntry(_('Server Username'), config.plugins.tvmanager.user, _('Username')))
            self.list.append(getConfigListEntry(_('Server Password'), config.plugins.tvmanager.passw, _('Password')))

            self['key_green'].setText(buttn)
            self['key_yellow'].setText(_('Get Link'))
            self['key_blue'].setText(_('Reset'))

        self['config'].list = self.list
        self['config'].l.setList(self.list)
        self.showhide()

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

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.createSetup()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.createSetup()

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self['config'].getCurrent()[1].value = callback
            self['config'].invalidate(self['config'].getCurrent())
        return

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def selectionChanged(self):
        # self["info"].setText(self["config"].getCurrent()[2])
        self.showhide()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        self.selectionChanged()

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
        # cfgdok = open(dest, 'a', encoding='utf-8')
        cfgdok.write('\n\n' + host + ' ' + port + ' ' + user + ' ' + pasw)
        cfgdok.close()
        self.session.open(MessageBox, _('Server Copy in ') + dest, type=MessageBox.TYPE_INFO, timeout=8)

    def Oscam(self):
        global host, port, user, passw
        cfgfile = config.plugins.tvmanager.cfgfile.value
        dest = cfgfile
        host = str(config.plugins.tvmanager.hostaddress.value)
        port = str(config.plugins.tvmanager.port.value)
        user = str(config.plugins.tvmanager.user.value)
        pasw = str(config.plugins.tvmanager.passw.value)
        if not fileExists(dest):
            self.session.open(MessageBox, _('Please Reset - No File CFG'), type=MessageBox.TYPE_INFO, timeout=5)
            return
        os.system('chmod -R 755 %s' % dest)
        cfgdok = open(dest, 'a')
        # cfgdok = open(dest, 'a', encoding='utf-8')
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
        # cfgdok = open(dest, 'a', encoding='utf-8')
        cfgdok.write('\n[reader]\nlabel = Server_' + host + '\nenable= 1\nprotocol = cccam\ndevice = ' + host + ',' + port + '\nuser = ' + user + '\npassword = ' + pasw + '\ngroup = 3\ncccversion = 2.0.11\ndisablecrccws_only_for= 0500:032830\ncccmaxhops= 1\nccckeepalive= 1\naudisabled = 1\n\n')
        cfgdok.close()
        self.session.open(MessageBox, _('Server Copy in ') + dest, type=MessageBox.TYPE_INFO, timeout=8)

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
                if os.path.exists('/var/lib/dpkg/info'):
                    self.timer_conn = self.timer.timeout.connect(self.load_getcl(data))
                else:
                    self.timer.callback.append(self.load_getcl(data))
                self.timer.start(600, 1)
                # self.load_getcl(data)
            except Exception as e:
                print('getcl error: ', str(e))
        except Exception as e:
            print('error on host', str(e))

    def load_getcl(self, data):
        global host, port, user, passw
        try:
            # data = checkStr(data)
            url1 = re.findall(r'<h1>C: (.+?) (.+?) (.+?) (.+?)\n', data)
            if 'bosscccam' in data.lower():
                url1 = re.findall(r'ong>c: (.+?) (.+?) (.+?) (.+?)</', data)

            elif 'cccam.net/freecccam' in data.lower():
                # <b>C: free.cccam.net 21126 by5MtVIk cccam.net</b>
                url1 = re.findall(r'b>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)', data)

            elif 'testcline' in data.lower():
                url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</d', data)

            elif 'free.cccam.net' in data.lower():
                url1 = re.findall(r'<b>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</b>', data)

            elif 'cccam-premium.co' in data.lower():
                url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)', data)

            elif 'cccamsate' in data.lower():
                url1 = re.findall(r'<span><b>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</b>', data)

            elif 'cccameagle' in data.lower():
                url1 = re.findall(r'>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)</h2>', data)

            elif 'cccamprime' in data.lower():
                # url1 = re.findall('Cline : C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+).*?Host', data)
                url1 = re.findall(r'Cline : C:\s+(.*?)\s+(\d+)\s+(\w+)\s+(.*?)\s*Host', data)
                url1 = url1.replace('<br><br>', '')

            elif 'cccamprima.com' in data.lower():
                # url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\n', data)
                url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)

            elif 'cccampri.me' in data.lower():
                # url1 = re.findall(r'Cline : C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)<br>', data)
                url1 = re.findall(r'Cline : C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)<br\s*/?>', data)

            elif 'cccamfree.co' in data.lower():
                # url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\n', data)
                url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)

            elif 'iptvcccam' in data.lower():
                url1 = re.findall('C: (.+?) (.+?) (.+?) (*?).*?</h1>', data)

            # elif 'premium' in data.lower():
                # url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)\n', data)

            elif 'cccamia' in data:
                # url1 = re.findall(r'>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)
                url1 = re.findall(r'>?C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)

            elif 'cccameurop' in data.lower():
                # url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)</', data)
                url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s*</', data)

            elif 'infosat' in data.lower():
                # url1 = re.findall('host: (.+?)<br> port: (.+?) <br>.*?user:(.+?)<br>.*?pass: (.+?)\n', data)
                url1 = re.findall(r'host:\s*(.+?)<br\s*/?>\s*port:\s*(.+?)<br\s*/?>\s*user:\s*(.+?)<br\s*/?>\s*pass:\s*(.+?)\s*\n', data)

            elif 'cccamx' in data.lower():
                # url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)\n', data)
                url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)

            elif 'cccamiptv' in data.lower():
                # url1 = re.findall('C: (.+?) (.+?) (.+?) (.+?)\n.*?</h3>', data)
                url1 = re.findall(r'C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</h3>', data)

            elif 'FREEN12' in data.lower():
                # url1 = re.findall('<h1>\nC: (.+?) (.+?) (.+?) (.+?)\n', data)
                url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)

            elif 'history' in data.lower():
                # url1 = re.findall('of the line">C: (.+?) (.+?) (.+?) (.+?)</a>.*?title=', data)
                url1 = re.findall(r'of the line">C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</a>.*?title=', data)

            elif 'store' in data.lower():
                # url1 = re.findall('<center><strong>C: (.+?) (.+?) (.+?) (.+?) <br>', data)
                url1 = re.findall(r'<center><strong>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*<br>', data)

            elif 'cccamhub' in data.lower():
                url1 = re.findall(r'id="cline">.*?C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</div>', data)

            elif 'rogcam' in data.lower():
                url1 = re.findall(r'bg-primary"> C: (.+?) (.+?) (.+?) (.+?) </span>', data)

            elif 'cccambird' in data.lower():
                url1 = re.findall(r'>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</th>', data)

            elif 'bosscccam' in data.lower():
                url1 = re.findall(r'<strong>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</strong', data)

            elif '15days' in data.lower():
                url1 = re.findall(r'">C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*</th></tr>', data)

            elif 'cccamfrei' in data.lower():
                # url1 = re.findall('<h1>C: (.+?) (.+?) (.+?) (.+?)\n', data)
                url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)
            elif 'cccamazon' in data.lower():
                # url1 = re.findall('<h1>C: (.+?) (.+?) (.+?) (.+?)\n', data)
                url1 = re.findall(r'<h1>C:\s+([\w.-]+)\s+(\d+)\s+(\w+)\s+([\w.-]+)\s*', data)
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
                elif 'cccam.net' in data.lower():
                    for h, p, u, pw in url1:
                        print(h, p, u, pw)
                        host = str(h)
                        port = str(p)
                        user = str(u)
                        password = str(pw)
                        password = password.replace('</b>', '').replace('</span>', '')
                        password = password.replace('</div>', '')
                        password = password.replace('</h1>', '')
                        password = password.replace('</div>', '')
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

    def readCurrent(self):
        currCam = None
        self.FilCurr = ''
        if fileExists('/etc/CurrentBhCamName'):
            self.FilCurr = '/etc/CurrentBhCamName'
        else:
            self.FilCurr = '/etc/clist.list'
        if os.stat(self.FilCurr).st_size > 0:
            try:
                if sys.version_info[0] == 3:
                    clist = open(self.FilCurr, 'r', encoding='UTF-8')
                else:
                    clist = open(self.FilCurr, 'r')
            except:
                return
            if clist is not None:
                for line in clist:
                    currCam = line
                clist.close()
        return currCam
