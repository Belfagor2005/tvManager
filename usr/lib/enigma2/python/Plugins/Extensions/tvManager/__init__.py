#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
import os
sl = 'slManager'
PluginLanguageDomain = 'tvManager'
PluginLanguagePath = 'Extensions/tvManager/locale'

global isDreamOS
isDreamOS = False
if os.path.exists("/var/lib/dpkg/status"):
    isDreamOS = True


def wgetsts():
    wgetsts = False
    cmd22 = 'find /usr/bin -name "wget"'
    res = os.popen(cmd22).read()
    if 'wget' not in res.lower():
        if os.path.exists("/var/lib/dpkg/status"):
            cmd23 = 'apt-get update && apt-get install wget'
            os.popen(cmd23)
            wgetsts = True
        else:
            cmd23 = 'opkg update && opkg install wget'
            os.popen(cmd23)
            wgetsts = True
        return wgetsts


def paypal():
    conthelp = "If you like what I do you\n"
    conthelp += "can contribute with a coffee\n"
    conthelp += "scan the qr code and donate € 1.00"
    return conthelp


def localeInit():
    if isDreamOS:  # check if opendreambox image
        # getLanguage returns e.g. "fi_FI" for "language_country"
        lang = language.getLanguage()[:2]
        # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs
        # it!
        os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain(
        PluginLanguageDomain,
        resolveFilename(
            SCOPE_PLUGINS,
            PluginLanguagePath))


if isDreamOS:  # check if DreamOS image
    def _(txt):
        return gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
else:
    def _(txt):
        translation = gettext.dgettext(PluginLanguageDomain, txt)
        if translation:
            return translation
        else:
            print(("[%s] fallback to default translation for %s" %
                  (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)


localeInit()
language.addCallback(localeInit)
ftpxml = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2xldmktNDUvTXVsdGljYW0vbWFpbi9DYW1pbnN0YWxsZXIueG1s'
installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS90dk1hbmFnZXIvbWFpbi9pbnN0YWxsZXIuc2g='
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvdHZNYW5hZ2Vy'
