#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
###############################################################################
#                                                                             #
#                      S O F T C A M   M A N A G E R                          #
#                                                                             #
#                     Enterprise Grade Enigma2 Plugin                         #
#                                                                             #
#     Copyright (c) 2024-2025 Lululla. All rights reserved.                   #
#     Skin Design by MMark. Licensed under GNU General Public License v3.0    #
#                                                                             #
#     Version: 3.1.0 Professional Edition      Build Date: 2025-02-27         #
#     Core Developer: Lululla                   Lead Designer: MMark          #
#     Architecture: Multi-Platform Enigma2      Python: 2.7/3.x Compatible    #
#                                                                             #
#     Official Repository: https://github.com/Belfagor2005/tvManager          #
#                                                                             #
#     This program is free software: you can redistribute it and/or modify    #
#     it under the terms of the GNU General Public License as published by    #
#     the Free Software Foundation, either version 3 of the License, or       #
#     (at your option) any later version.                                     #
#                                                                             #
#     This program is distributed in the hope that it will be useful,         #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the            #
#     GNU General Public License for more details.                            #
#                                                                             #
#     For commercial licensing inquiries, contact: business@lululla.com       #
#                                                                             #
###############################################################################

# =========================
# Standard library imports
# =========================
import codecs
import json
import subprocess
import sys
import time
from base64 import b64decode
from datetime import datetime
from os import (
    mkdir,
    access,
    X_OK,
    system,
    popen,
    chmod,
    remove,
    walk,
    stat,
    listdir
)
from os.path import dirname, join, exists, islink, basename
from re import sub
from time import sleep
from xml.dom import minidom

# =========================
# Third-party imports
# =========================
from twisted.web.client import getPage

# =========================
# Enigma2 / framework imports
# =========================
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from enigma import (
    RT_HALIGN_LEFT,
    RT_VALIGN_CENTER,
    eListboxPythonMultiContent,
    eTimer,
    gFont,
    getDesktop,
)

# =========================
# Local project imports
# =========================
from . import _, paypal, installer_url, developer_url, ftpxml  # , wgetsts
from .data.Utils import RequestAgent, b64decoder, checkGZIP
from .data.GetEcmInfo import GetEcmInfo
from .data.Console import Console


global active, skin_path
global _session


active = False
_session = None
local = False
PY3 = sys.version_info.major >= 3

if PY3:
    unicode = str
    unichr = chr
    long = int
    PY3 = True
    from urllib.request import urlopen, Request
else:
    from urllib2 import urlopen, Request


currversion = "3.2"
NAME_PLUG = "Softcam Manager"
TITLE_PLUG = "..:: " + NAME_PLUG + " V. %s ::.." % currversion
plugin_path = dirname(sys.modules[__name__].__file__)
ICONPIC = join(plugin_path, "logo.png")
DATA_PATH = join(plugin_path, "data")
DIR_WORK = "/usr/lib/enigma2/python/Screens"
FILE_XML = join(plugin_path, "tvManager.xml")
ECM_INFO = "/tmp/ecm.info"
EMPTY_ECM_INFO = ("", "0", "0", "0")
old_ecm_time = time.time()
info = {}
ecm = ""
SOFTCAM = 0
CCCAMINFO = 1
OSCAMINFO = 2

AgentRequest = RequestAgent()


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "deflate"}


# =========================
# Utility Functions
# =========================


def execute_cam_command(cmd):
    """Executes cam commands without blocking - uses simple system()"""
    print("Executing cam command: %s" % cmd)
    try:
        system(cmd)
        # Do not wait for completion, return immediately
        return True
    except Exception as e:
        print("Cam command error: %s" % str(e))
        return False


def safe_system_call(cmd, max_retries=3, timeout=30, background=False):
    """Execute system commands with intelligent management"""
    # Identify command type
    is_cam_command = "camscript" in cmd and (
        "cam_up" in cmd or "cam_down" in cmd or "cam_res" in cmd)
    is_background_command = background or cmd.strip().endswith('&')

    # For cam and background commands: use system() without waiting
    if is_cam_command or is_background_command:
        print("Executing background command: %s" % cmd)
        try:
            system(cmd)
            return True, "background_command_executed"
        except Exception as e:
            print("Background command error: %s" % str(e))
            return False, str(e)

    for attempt in range(max_retries):
        try:
            if PY3:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, timeout=timeout)
                if result.returncode == 0:
                    return True, result.stdout
                print("Attempt %d failed: %s" % (attempt + 1, result.stderr))
            else:
                import subprocess as sub
                result = sub.Popen(
                    cmd, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
                stdout, stderr = result.communicate()
                if result.returncode == 0:
                    return True, stdout
                print("Attempt %d failed: %s" % (attempt + 1, stderr))
        except subprocess.TimeoutExpired:
            print("Command timed out after %d seconds: %s" % (timeout, cmd))
            if attempt == max_retries - 1:
                return False, "timeout"
        except Exception as e:
            print("System call error: %s" % str(e))

        if attempt < max_retries - 1:
            sleep(2)

    return False, None


def execute_background_command(cmd):
    """For non-blocking commands (cam, backup, cleanup)"""
    print("Executing background: %s" % cmd)
    try:
        system(cmd)
        return True
    except Exception as e:
        print("Background command error: %s" % str(e))
        return False


def execute_blocking_command(cmd, max_retries=3, timeout=30):
    """For commands that need output (resource monitoring, checks)"""
    for attempt in range(max_retries):
        try:
            if PY3:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, timeout=timeout)
                if result.returncode == 0:
                    return True, result.stdout
                print("Attempt %d failed: %s" % (attempt + 1, result.stderr))
            else:
                import subprocess as sub
                result = sub.Popen(
                    cmd, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
                stdout, stderr = result.communicate()
                if result.returncode == 0:
                    return True, stdout
                print("Attempt %d failed: %s" % (attempt + 1, stderr))
        except Exception as e:
            print("Blocking command error: %s" % str(e))

        if attempt < max_retries - 1:
            sleep(2)

    return False, None


def get_resource_info_safe():
    """Get resource info without blocking - use alternative methods"""
    try:
        # For memory: read /proc/meminfo
        mem_info = ""
        if exists("/proc/meminfo"):
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line or "MemAvailable" in line:
                        mem_info += line.strip() + "\n"

        # For CPU: read /proc/loadavg
        cpu_info = ""
        if exists("/proc/loadavg"):
            with open("/proc/loadavg", "r") as f:
                cpu_info = f.read().strip()

        return mem_info, cpu_info

    except Exception as e:
        print("Safe resource info error: %s" % str(e))
        return "N/A", "N/A"


def backup_configs(backup_name=None):
    """Create backup of important configurations"""
    if backup_name is None:
        backup_name = "backup_%s" % datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_dir = join("/tmp", backup_name)
    try:
        if not exists(backup_dir):
            mkdir(backup_dir)

        config_files = [
            "/etc/CCcam.cfg",
            "/etc/tuxbox/config/oscam.server",
            "/etc/tuxbox/config/ncam.server",
            "/usr/keys/SoftCam.Key",
            "/etc/clist.list"
        ]

        backed_up = []
        for config_file in config_files:
            if exists(config_file):
                dest_file = join(backup_dir, basename(config_file))
                success, _ = safe_system_call(
                    "cp '%s' '%s'" %
                    (config_file, dest_file))
                if success:
                    backed_up.append(config_file)

        print(
            "Backup completed: %d files saved in %s" %
            (len(backed_up), backup_dir))
        return backup_dir, backed_up

    except Exception as e:
        print("Error during backup: %s" % str(e))
        return None, []


def cleanup_temp_files():
    """Clean temporary files"""
    temp_patterns = [
        "/tmp/*.ipk",
        "/tmp/*.deb",
        "/tmp/*.tar.gz",
        "/tmp/*.zip",
        "/tmp/ecm.info.old"
    ]

    for pattern in temp_patterns:
        safe_system_call("rm -f %s" % pattern)


def check_dependencies():
    """Check and install missing dependencies"""
    missing_deps = []

    if not exists(
            "/usr/lib/libusb-1.0.so.0") and not exists("/usr/lib/libusb-1.0.so"):
        missing_deps.append("libusb-1.0-0")

    ssl_check = safe_system_call("ldconfig -p | grep libssl > /dev/null")
    if not ssl_check[0]:
        missing_deps.append("libssl")
    return missing_deps


def install_package():
    """Install necessary packages with error handling"""
    try:
        if exists("/usr/bin/apt-get"):  # DreamOS
            check_cmd = ["dpkg", "-l"]
            install_cmd = ["apt-get", "install", "-y"]
        else:  # OpenPLi/OpenATV
            check_cmd = ["opkg", "list-installed"]
            install_cmd = ["opkg", "install"]

        # Update repositories
        print("Updating package repositories...")
        if exists("/usr/bin/apt-get"):
            safe_system_call("apt-get update")
        else:
            safe_system_call("opkg update")

        # Install libusb if necessary
        libusb_check = safe_system_call(
            " ".join(check_cmd + ["|", "grep", "-q", "libusb-1.0-0"]))
        if not libusb_check[0]:
            print("Installing libusb-1.0-0...")
            success, _ = safe_system_call(
                " ".join(install_cmd + ["libusb-1.0-0"]))
            if success:
                print("libusb-1.0-0 installed successfully")
            else:
                print("Failed to install libusb-1.0-0")

        # Check other dependencies
        missing = check_dependencies()
        if missing:
            print("Missing dependencies: %s" % ", ".join(missing))
            for dep in missing:
                safe_system_call(" ".join(install_cmd + [dep]))

    except Exception as e:
        print("Package installation error: %s" % str(e))


install_package()


def checkdir():
    """Create necessary directories"""
    directories = ["/usr/keys", "/usr/camscript", "/tmp/softcam_backups"]

    for directory in directories:
        if not exists(directory):
            try:
                mkdir(directory)
                print("Created directory: %s" % directory)
            except Exception as e:
                print("Error creating directory %s: %s" % (directory, str(e)))


checkdir()

screenwidth = getDesktop(0).size()
if screenwidth.width() == 2560:
    skin_path = plugin_path + "/res/skins/uhd/"
elif screenwidth.width() == 1920:
    skin_path = plugin_path + "/res/skins/fhd/"
else:
    skin_path = plugin_path + "/res/skins/hd/"

if exists("/usr/bin/apt-get"):
    skin_path = skin_path + "dreamOs/"

if not exists("/etc/clist.list"):
    with open("/etc/clist.list", "w"):
        print("/etc/clist.list has been created")
        system("chmod 755 /etc/clist.list")


class m2list(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setItemHeight(60)
            textfont = int(46)
            self.l.setFont(0, gFont("Regular", textfont))
        elif screenwidth.width() == 1920:
            self.l.setItemHeight(50)
            textfont = int(34)
            self.l.setFont(0, gFont("Regular", textfont))
        else:
            self.l.setItemHeight(50)
            textfont = int(22)
            self.l.setFont(0, gFont("Regular", textfont))


def show_list_1(h):
    res = [h]
    if screenwidth.width() == 2560:
        res.append(
            MultiContentEntryText(
                pos=(
                    2,
                    0),
                size=(
                    1000,
                    50),
                font=0,
                text=h,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(
            MultiContentEntryText(
                pos=(
                    2,
                    0),
                size=(
                    780,
                    40),
                font=0,
                text=h,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(
            MultiContentEntryText(
                pos=(
                    2,
                    0),
                size=(
                    780,
                    40),
                font=0,
                text=h,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlist(datal, list):
    plist = []
    for name in datal:
        plist.append(show_list_1(name))
    list.setList(plist)


class ResourceMonitor:
    """Resource monitoring for softcams"""

    @staticmethod
    def get_cam_resources():
        """Get real information about resource usage"""
        try:
            print("[DEBUG] get_cam_resources called")

            # 1. Memory used by cams
            memory_usage = ResourceMonitor._get_memory_usage()

            # 2. CPU usage
            cpu_usage = ResourceMonitor._get_cpu_usage()

            # 3. Active cam processes - USE THE SAFE VERSION
            active_cams = ResourceMonitor._get_active_cams_safe()

            return "Mem: %s | CPU: %s | Cams: %s" % (
                memory_usage, cpu_usage, active_cams)

        except Exception as e:
            print("[DEBUG] get_cam_resources error: %s" % str(e))
            return "Stats error"

    @staticmethod
    def _get_active_cams_safe():
        """Count active cam processes - count only unique processes"""
        try:
            cam_keywords = [
                "oscam",
                "cccam",
                "ncam",
                "mgcamd",
                "gcam",
                "wicardd"]
            found_cams = set()

            if exists("/proc"):
                for item in listdir("/proc"):
                    if item.isdigit():
                        try:
                            # Read comm file for process name
                            comm_path = join("/proc", item, "comm")
                            if exists(comm_path):
                                with open(comm_path, "r") as f:
                                    comm = f.read().strip().lower()

                                # Check if it's a cam
                                for cam in cam_keywords:
                                    if cam in comm:
                                        # Use base cam name (without
                                        # numbers/versions)
                                        base_cam = cam
                                        found_cams.add(base_cam)
                                        break
                        except (IOError, OSError):
                            continue

            print("[DEBUG] Unique cams found: %s" % list(found_cams))
            return str(len(found_cams))

        except Exception as e:
            print("[DEBUG] _get_active_cams_safe error: %s" % str(e))
            return "?"

    @staticmethod
    def _get_memory_usage():
        """Get memory usage from cams"""
        try:
            if exists("/proc/meminfo"):
                with open("/proc/meminfo", "r") as f:
                    content = f.read()

                mem_total = 0
                mem_available = 0

                for line in content.split('\n'):
                    if line.startswith('MemTotal:'):
                        mem_total = int(line.split()[1])
                    elif line.startswith('MemAvailable:'):
                        mem_available = int(line.split()[1])

                if mem_total > 0 and mem_available > 0:
                    used_kb = mem_total - mem_available
                    used_percent = (used_kb / mem_total) * 100
                    return "%.1f%%" % used_percent

            return "N/A"
        except BaseException:
            return "N/A"

    @staticmethod
    def _get_cpu_usage():
        """Get CPU usage"""
        try:
            if exists("/proc/loadavg"):
                with open("/proc/loadavg", "r") as f:
                    load_avg = f.read().split()[0]
                return load_avg
            return "N/A"
        except BaseException:
            return "N/A"


class ConfigBackupManager:
    """Configuration backup management"""

    def __init__(self):
        self.backup_dir = "/tmp/softcam_backups"
        if not exists(self.backup_dir):
            mkdir(self.backup_dir)

    def create_backup(self, backup_name=None):
        """Create a configuration backup"""
        return backup_configs(backup_name)

    def list_backups(self):
        """List available backups"""
        try:
            backups = []
            for item in listdir(self.backup_dir):
                if item.startswith("backup_"):
                    backups.append(item)
            return sorted(backups, reverse=True)
        except BaseException:
            return []

    def restore_backup(self, backup_name):
        """Restore a backup"""
        try:
            backup_path = join(self.backup_dir, backup_name)
            if not exists(backup_path):
                print("Backup path does not exist: %s" % backup_path)
                return False

            print("Restoring backup from: %s" % backup_path)

            # List of configuration files to restore
            config_files = [
                ("CCcam.cfg", "/etc/CCcam.cfg"),
                ("oscam.server", "/etc/tuxbox/config/oscam.server"),
                ("ncam.server", "/etc/tuxbox/config/ncam.server"),
                ("SoftCam.Key", "/usr/keys/SoftCam.Key"),
                ("clist.list", "/etc/clist.list")
            ]

            restored_files = []

            for backup_file, destination in config_files:
                source_file = join(backup_path, backup_file)

                if exists(source_file):
                    try:
                        destination_dir = dirname(destination)
                        if not exists(destination_dir):
                            mkdir(destination_dir)

                        success, _ = safe_system_call(
                            "cp '%s' '%s'" %
                            (source_file, destination), background=True)

                        if success:
                            safe_system_call(
                                "chmod 644 '%s'" %
                                destination, background=True)
                            restored_files.append(backup_file)
                            print(
                                "Restored: %s -> %s" %
                                (backup_file, destination))
                        else:
                            print("Failed to restore: %s" % backup_file)

                    except Exception as file_error:
                        print(
                            "Error restoring %s: %s" %
                            (backup_file, str(file_error)))

            if restored_files:
                print(
                    "Backup restoration completed: %d files restored" %
                    len(restored_files))
                return True, restored_files
            else:
                print("No files were restored")
                return False, []

        except Exception as e:
            print("Restore error: %s" % str(e))
            return False, []


class tvManager(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session, runningcam
        runningcam = None
        _session = session
        self.resource_monitor = ResourceMonitor()
        self.backup_manager = ConfigBackupManager()
        skin = join(skin_path, "tvManager.xml")
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.namelist = []
        self.softcamslist = []
        self.oldService = ""
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        except BaseException:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self["NumberActions"] = NumberActionMap(
            ["NumberActions"],
            {
                "0": self.keyNumberGlobal,
                "1": self.keyNumberGlobal,
                "2": self.keyNumberGlobal,
                "3": self.keyNumberGlobal,
                "4": self.keyNumberGlobal,
                "5": self.keyNumberGlobal,
                "6": self.keyNumberGlobal,
                "7": self.keyNumberGlobal,
                "8": self.keyNumberGlobal,
                "9": self.keyNumberGlobal
            }
        )
        self["actions"] = ActionMap(
            [
                "OkCancelActions",
                "ColorActions",
                "EPGSelectActions",
                "MenuActions"
            ],
            {
                "ok": self.action,
                "cancel": self.close,
                "menu": self.configtv,
                "blue": self.Blue,
                "yellow": self.download,
                "green": self.action,
                "info": self.CfgInfo,
                "red": self.stop
            },
            -1
        )
        self.setTitle(_(TITLE_PLUG))
        self["title"] = Label(_(TITLE_PLUG))
        self["key_green"] = Label(_("Start"))
        self["key_yellow"] = Label(_("Cam Download"))
        self["key_red"] = Label(_("Stop"))
        self["key_blue"] = Label("Softcam")
        self["description"] = Label(
            _("Scanning and retrieval list softcam ..."))
        self["resource_label"] = Label()
        self["info"] = Label()
        self["list"] = List([])
        self.curCam = None
        self.curCam = self.readCurrent()
        self.readScripts()
        self.BlueAction = "SOFTCAM"
        runningcam = "softcam"
        self.setBlueKey()
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.cgdesc)
        except BaseException:
            self.timer.callback.append(self.cgdesc)
        self.timer.start(300, 1)

        self.EcmInfoPollTimer = eTimer()
        try:
            self.EcmInfoPollTimer_conn = self.EcmInfoPollTimer.timeout.connect(
                self.setEcmInfo)
        except BaseException:
            self.EcmInfoPollTimer.callback.append(self.setEcmInfo)
        self.EcmInfoPollTimer.start(200)

        self["resource_label"] = Label()
        self["resource_label"].setText("Loading resources...")
        self.resource_timer = eTimer()
        try:
            self.resource_timer_conn = self.resource_timer.timeout.connect(
                self.update_resource_info)
        except BaseException:
            self.resource_timer.callback.append(self.update_resource_info)
        self.resource_timer.start(10000)
        self.onShown.append(self.ecm)
        self.onShown.append(self.setBlueKey)
        self.onHide.append(self.stopEcmInfoPollTimer)

    def update_resource_info(self):
        """Update resource information"""
        try:
            print("[DEBUG] update_resource_info called")
            resource_info = self.resource_monitor.get_cam_resources()
            print("[DEBUG] Resource info:", resource_info)
            self["resource_label"].setText(resource_info)
            print("[DEBUG] Resource label updated")
        except Exception as e:
            print("[DEBUG] Resource update error: %s" % str(e))
            self["resource_label"].setText("Error: " + str(e))

    def create_backup(self):
        """Create configuration backup"""
        backup_dir, backed_up = backup_configs()
        if backup_dir:
            message = "Backup created successfully!\nSaved %d files to:\n%s" % (
                len(backed_up), backup_dir)
            self.session.open(
                MessageBox,
                _(message),
                MessageBox.TYPE_INFO,
                timeout=10)
        else:
            self.session.open(
                MessageBox,
                _("Backup failed!"),
                MessageBox.TYPE_ERROR,
                timeout=5)

    def show_restore_menu(self):
        """Show menu to select backup to restore"""
        backups = self.backup_manager.list_backups()

        if not backups:
            self.session.open(
                MessageBox,
                _("No backups available!"),
                MessageBox.TYPE_INFO,
                timeout=5)
            return

        backup_list = []
        for backup in backups:
            backup_path = join(self.backup_manager.backup_dir, backup)
            if exists(backup_path):
                try:
                    backup_time = backup.replace(
                        "backup_",
                        "").replace(
                        "_",
                        " ").replace(
                        "-",
                        ":")
                    file_count = len([f for f in listdir(
                        backup_path) if exists(join(backup_path, f))])
                    backup_list.append(
                        (backup, "Backup: %s (%d files)" %
                         (backup_time, file_count)))
                except BaseException:
                    backup_list.append((backup, backup))

        if not backup_list:
            self.session.open(
                MessageBox,
                _("No valid backups found!"),
                MessageBox.TYPE_INFO,
                timeout=5)
            return

        def backup_selected(selected_backup):
            if selected_backup:
                self.session.openWithCallback(
                    lambda result: self._execute_restore(
                        selected_backup[0],
                        result),
                    MessageBox,
                    _("Restore backup '%s'?\nThis will overwrite current configurations.") %
                    selected_backup[0],
                    MessageBox.TYPE_YESNO)

        self.session.openWithCallback(
            backup_selected,
            ChoiceBox,
            _("Select backup to restore:"),
            backup_list
        )

    def _execute_restore(self, backup_name, confirm):
        """Execute restore after confirmation"""
        if confirm:
            success, restored_files = self.backup_manager.restore_backup(
                backup_name)
            if success:
                message = _(
                    "Backup restored successfully!\nRestored files:\n- %s") % "\n- ".join(restored_files)
                self.session.open(
                    MessageBox,
                    message,
                    MessageBox.TYPE_INFO,
                    timeout=10)
                self.session.openWithCallback(
                    lambda result: self._restart_cam_after_restore(result),
                    MessageBox,
                    _("Restart softcam to apply restored configuration?"),
                    MessageBox.TYPE_YESNO
                )
            else:
                self.session.open(
                    MessageBox,
                    _("Backup restoration failed!"),
                    MessageBox.TYPE_ERROR,
                    timeout=5)

    def _restart_cam_after_restore(self, restart):
        """Restart cam after restore"""
        if restart:
            if self.curCam and self.curCam != "None":
                self.cmd1 = "/usr/camscript/" + self.curCam + ".sh cam_res &"
                system(self.cmd1)
                self.session.open(
                    MessageBox,
                    _("Softcam restarted with new configuration!"),
                    MessageBox.TYPE_INFO,
                    timeout=5)
            else:
                self.session.open(
                    MessageBox,
                    _("No active cam to restart!"),
                    MessageBox.TYPE_INFO,
                    timeout=5)

    def setBlueKey(self):
        global runningcam
        self.curCam = self.readCurrent()
        self["key_blue"].setText("Softcam")
        self.BlueAction = None
        if self.curCam is not None:
            cam_name = str(self.curCam).lower()
            print("cam_name=", cam_name)
            cam_info = {
                "oscam": ("OSCAMINFO", "OScamInfo"),
                "cccam": ("CCCAMINFO", "CCcamInfo"),
                "movicam": ("MOVICAMINFO", "OScamInfo"),
                "ncam": ("NCAMINFO", "NcamInfo")
            }

            for key, (action, file_name) in cam_info.items():
                if key in cam_name:
                    print("%s detected in cam_name" % key)
                    runningcam = key
                    self.BlueAction = action
                    self["key_blue"].setText(action)
                    pyo_file = join(plugin_path, "data/%s.pyo" % file_name)
                    pyc_file = join(plugin_path, "data/%s.pyc" % file_name)
                    py_file = join(plugin_path, "data/%s.py" % file_name)
                    if exists(pyo_file) or exists(pyc_file) or exists(py_file):
                        print("exists %s" % file_name)
                    break

            print("[setBlueKey] self.curCam=", self.curCam)
            print("[setBlueKey] self.BlueAction=", self.BlueAction)
            print("[setBlueKey] runningcam=", runningcam)

    def Blue(self):
        print("[Blue] self.BlueAction:", self.BlueAction)
        cam_name = str(self.curCam).lower()
        print("cam_name=", cam_name)
        try:
            if "oscam" in cam_name:
                self.open_oscam_info()
            elif "cccam" in cam_name:
                self.open_cccam_info()
            elif "ncam" in cam_name:
                self.open_ncam_info()
            elif "movicam" in cam_name:
                self.open_oscam_info()  # Use OSCamInfo for Movicam
            else:
                print("[Blue] Default action: CCcam")
                self.open_cccam_info()
        except Exception as e:
            print("[Blue] General Error:", e)
            self.session.open(
                MessageBox, _(
                    "Error opening cam info: %s" %
                    str(e)), MessageBox.TYPE_ERROR, timeout=5)

    def open_oscam_info(self):
        """Open OSCamInfo with error handling"""
        try:
            from Screens.OScamInfo import OSCamInfo
            self.session.open(OSCamInfo)
        except ImportError:
            try:
                from .data.OScamInfo import OSCamInfo
                self.session.open(OSCamInfo)
            except ImportError as e:
                print("OSCamInfo import error:", e)
                self.session.open(
                    MessageBox,
                    _("OSCamInfo not available"),
                    MessageBox.TYPE_ERROR,
                    timeout=5)

    def open_cccam_info(self):
        """Open CCcamInfo with error handling"""
        try:
            from Screens.CCcamInfo import CCcamInfoMain
            self.session.open(CCcamInfoMain)
        except ImportError:
            try:
                from .data.CCcamInfo import CCcamInfoMain
                self.session.open(CCcamInfoMain)
            except ImportError as e:
                print("CCcamInfo import error:", e)
                self.session.open(
                    MessageBox,
                    _("CCcamInfo not available"),
                    MessageBox.TYPE_ERROR,
                    timeout=5)

    def open_ncam_info(self):
        """Open NCamInfo with error handling"""
        try:
            from Screens.NcamInfo import NcamInfoMenu
            self.session.open(NcamInfoMenu)
        except ImportError:
            try:
                from .data.NcamInfo import NcamInfoMenu
                self.session.open(NcamInfoMenu)
            except ImportError as e:
                print("NCamInfo import error:", e)
                self.session.open(
                    MessageBox,
                    _("NCamInfo not available"),
                    MessageBox.TYPE_ERROR,
                    timeout=5)

    def keyNumberGlobal(self, number):
        print("[DEBUG] keyNumberGlobal CALLED with number: %s" % number)
        try:
            number = int(number)
            print("[DEBUG] Processing number: %d" % number)
            self.session.open(
                MessageBox,
                "Number %d pressed!" %
                number,
                MessageBox.TYPE_INFO,
                timeout=3)
            # Actions Map
            key_actions = {
                0: self.messagekd,
                1: self.open_cccam_info,
                2: self.open_oscam_info,
                3: self.open_ncam_info,
                4: self.create_backup,
                5: self.show_restore_menu,
                6: self.cleanup_system,
                8: self.show_help,
                9: self.restart_gui
            }

            if number in key_actions:
                print("[DEBUG] Executing action for number: %d" % number)
                key_actions[number]()
            else:
                print("[DEBUG] No action defined for number: %d" % number)

        except Exception as e:
            print("[DEBUG] Error in keyNumberGlobal: %s" % str(e))

    def show_help(self):
        """Show help for quick keys"""
        help_text = _("""Number Key Shortcuts:
            0 - Update Softcam Keys
            1 - CCcam Info
            2 - OSCam Info
            3 - NCam Info
            4 - Create Backup
            5 - Restore Backup
            6 - Cleanup System  # <-- ADDED
            8 - This Help
            Press OK to close""")
        self.session.open(
            MessageBox,
            help_text,
            MessageBox.TYPE_INFO,
            timeout=15)

    def show_resource_info(self):
        """Show system resource information"""
        try:
            mem_info, cpu_info = get_resource_info_safe()

            memory_usage = self._parse_memory_info(mem_info)
            cpu_usage = self._parse_cpu_info(cpu_info)
            disk_cmd = "df -h / | tail -1 | awk '{print $4\"/\"$2\" free (\"$5\" used)\"}'"
            success, disk_info = safe_system_call(disk_cmd, timeout=5)
            disk = disk_info.strip() if success else "N/A"
            cam_resources = self.resource_monitor.get_cam_resources()

            resource_text = _("""System Resources:
                Memory Used: %s
                CPU Load: %s
                Disk: %s
                Cam Resources: %s
                Press OK to close""") % (memory_usage, cpu_usage, disk, cam_resources)

            self.session.open(
                MessageBox,
                resource_text,
                MessageBox.TYPE_INFO,
                timeout=10)

        except Exception as e:
            print("Error getting resource info: %s" % str(e))
            self.session.open(
                MessageBox,
                _("Error getting resource information"),
                MessageBox.TYPE_ERROR,
                timeout=3)

    def quick_restart(self):
        """Quick restart of current softcam"""
        if not self.curCam or self.curCam == "None":
            self.session.open(MessageBox, _("No active cam to restart!"),
                              MessageBox.TYPE_ERROR, timeout=3)
            return

        self.session.openWithCallback(self._execute_quick_restart, MessageBox,
                                      _("Quick restart %s?") % self.curCam,
                                      MessageBox.TYPE_YESNO)

    def _execute_quick_restart(self, answer):
        """Execute quick restart after confirmation"""
        if answer:
            try:
                stop_cmd = "/usr/camscript/%s.sh cam_down &" % self.curCam
                success, _ = safe_system_call(stop_cmd)

                if success:
                    sleep(1)
                    start_cmd = "/usr/camscript/%s.sh cam_up &" % self.curCam
                    safe_system_call(start_cmd)

                    self.session.open(
                        MessageBox, _("%s restarted successfully!") %
                        self.curCam, MessageBox.TYPE_INFO, timeout=3)
                else:
                    self.session.open(MessageBox,
                                      _("Error stopping %s!") % self.curCam,
                                      MessageBox.TYPE_ERROR, timeout=3)

            except Exception as e:
                print("Quick restart error: %s" % str(e))
                self.session.open(MessageBox,
                                  _("Restart error: %s") % str(e),
                                  MessageBox.TYPE_ERROR, timeout=3)

    def cleanup_system(self):
        """System cleanup - direct version"""
        print("[DEBUG] Starting system cleanup")

        try:
            cleanup_temp_files()

            if exists("/usr/bin/apt-get"):
                system("apt-get clean &")
            else:
                system("opkg clean &")

            system("find /tmp -name \"*.log\" -mtime +7 -delete &")

            self["description"].setText(_("System cleanup completed!"))
            print("[DEBUG] System cleanup completed")

        except Exception as e:
            print("[DEBUG] Cleanup error: %s" % str(e))
            self["description"].setText(_("Cleanup error: %s") % str(e))

    def restart_gui(self):
        """GUI restart"""
        self.session.openWithCallback(self._execute_restart_gui, MessageBox,
                                      _("Restart GUI?"),
                                      MessageBox.TYPE_YESNO)

    def _execute_restart_gui(self, answer):
        """Execute GUI restart"""
        if answer:
            self.session.open(TryQuitMainloop, 3)

    def setEcmInfo(self):
        """Update ECM information with robust error handling"""
        try:
            self.ecminfo = GetEcmInfo()
            newEcmFound, ecmInfo = self.ecminfo.getEcm()
            if newEcmFound:
                formatted_ecm = self.format_ecm_info(ecmInfo)
                self["info"].setText(formatted_ecm)
                self.last_valid_ecm = time.time()
            else:
                current_time = time.time()
                if hasattr(self, 'last_valid_ecm'):
                    if current_time - self.last_valid_ecm > 30:
                        self["info"].setText(_("No ECM data - Timeout"))
                    else:
                        self.ecm()
                else:
                    self.ecm()

        except Exception as e:
            print("Error in setEcmInfo: %s" % str(e))
            self.ecm()

    def format_ecm_info(self, ecm_info):
        """Format ECM information for better display"""
        if not ecm_info:
            return _("No ECM data")

        try:
            ecm_text = "".join(ecm_info).strip()
            ecm_text = ''.join(
                char for char in ecm_text if char.isprintable() or char in [
                    '\n', '\t'])
            if len(ecm_text) > 200:
                ecm_text = ecm_text[:197] + "..."

            return ecm_text

        except Exception as e:
            print("Error formatting ECM info: %s" % str(e))
            return _("ECM data format error")

    def ecm(self):
        """Direct reading of ECM_INFO file with improved error handling"""
        try:
            if not exists(ECM_INFO):
                self["info"].setText(_("No ECM file"))
                return

            with open(ECM_INFO, 'r') as f:
                content = f.read().strip()

            if content:
                clean_content = self.clean_ecm_content(content)
                self["info"].setText(clean_content)
            else:
                self["info"].setText(_("ECM file empty"))

        except IOError as e:
            if e.errno == 2:
                self["info"].setText(_("ECM file not found"))
            else:
                self["info"].setText(_("ECM read error"))
            print("ECM file IO error: %s" % str(e))

        except Exception as e:
            print("Unexpected error reading ECM: %s" % str(e))
            self["info"].setText(_("ECM error"))

    def clean_ecm_content(self, content):
        """Clean ECM content from problematic characters"""
        try:
            if PY3:
                cleaned = ''.join(
                    char for char in content if char.isprintable() or char in [
                        '\n', '\t'])
            else:
                if isinstance(content, unicode):
                    cleaned = ''.join(
                        char for char in content if char.isprintable() or char in [
                            u'\n', u'\t'])
                else:
                    cleaned = ''.join(
                        char for char in content if char.isprintable() or char in [
                            '\n', '\t'])

            cleaned = sub(r'\n+', '\n', cleaned)
            cleaned = sub(r' +', ' ', cleaned)

            return cleaned.strip()

        except Exception as e:
            print("Error cleaning ECM content: %s" % str(e))
            return content[:100] + "..." if len(content) > 100 else content

    def stopEcmInfoPollTimer(self):
        self.EcmInfoPollTimer.stop()

    def messagekd(self):
        """Update Softcam Keys"""
        print("[DEBUG] Opening Console for keys update")

        script = join(plugin_path, "auto")
        if not access(script, X_OK):
            chmod(script, 493)
        if exists("/usr/keys/SoftCam.Key"):
            system("rm -rf /usr/keys/SoftCam.Key")

        cmd = script
        title = _("Installing Softcam Keys\nPlease Wait...")

        self.session.open(Console, title, [cmd], closeOnSuccess=False)

    def CfgInfo(self):
        self.session.open(InfoCfg)

    def configtv(self):
        from Plugins.Extensions.tvManager.data.datas import tv_config
        self.session.open(tv_config)

    def cgdesc(self):
        if len(self.namelist) >= 1:
            self["description"].setText(_("Select a cam to run ..."))
        else:
            self["description"].setText(_("Install Cam first!!!"))
            self.updateList()

    def getcont(self):
        cont = "Your Config:\n"
        arc = ""
        arkFull = ""
        libsssl = ""
        python = popen("python -V").read().strip("\n\r")
        arcx = popen("uname -m").read().strip("\n\r")
        libs = popen("ls -l /usr/lib/libss*.*").read().strip("\n\r")
        if arcx:
            arc = arcx
            print("arc= ", arc)
        if self.arckget():
            print("arkget= ", arkFull)
            arkFull = self.arckget()
        if libs:
            libsssl = libs
        cont += " ------------------------------------------ \n"
        cont += "Cpu: %s\nArchitecture info: %s\nPython V.%s\nLibssl(oscam):\n%s" % (
            arc, arkFull, python, libsssl)
        cont += " ------------------------------------------ \n"
        cont += "Button Info for Other Info\n"
        return cont

    def arckget(self):
        zarcffll = "by Lululla"
        try:
            if exists("/usr/bin/apt-get"):
                zarcffll = popen(
                    "dpkg --print-architecture | grep -iE 'arm|aarch64|mips|cortex|sh4|sh_4'").read().strip("\n\r")
            else:
                zarcffll = popen(
                    "opkg print-architecture | grep -iE 'arm|aarch64|mips|cortex|h4|sh_4'").read().strip("\n\r")
            return str(zarcffll)
        except Exception as e:
            print("Error ", e)

    def updateList(self):
        poPup = self.getcont()
        _session.open(MessageBox, poPup, MessageBox.TYPE_INFO, timeout=10)

    def download(self):
        self.session.open(GetipklistTv)
        self.onShown.append(self.readScripts)

    def getLastIndex(self):
        a = 0
        if len(self.namelist) >= 0:
            for x in self.namelist[0]:
                if x == self.curCam:
                    return a
                a += 1
                print("aa=", a)
        return None

    def action(self):
        i = len(self.softcamslist)
        if i < 1:
            self.session.open(
                MessageBox,
                _("No softcams available!"),
                MessageBox.TYPE_ERROR,
                timeout=5)
            return

        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        except BaseException:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()

        self.session.nav.stopService()
        self.last = self.getLastIndex()
        if self["list"].getCurrent():
            self.var = self["list"].getIndex()

            system("chmod 755 /etc/clist.list")
            system("chmod 755 /usr/camscript/*.*")
            curCam = self.readCurrent()
            if self.last is not None:
                try:
                    foldcurr = "/usr/bin/" + str(curCam)
                    foldscrpt = "/usr/camscript/" + str(curCam) + ".sh"
                    system("chmod 755 '%s'" % foldcurr)
                    system("chmod 755 '%s'" % foldscrpt)
                except OSError:
                    pass

                if self.last == self.var:
                    self.cmd1 = "/usr/camscript/" + \
                        self.softcamslist[self.var][0] + ".sh" + " cam_res &"
                    _session.open(
                        MessageBox,
                        _("Please wait..\nRESTART CAM"),
                        MessageBox.TYPE_INFO,
                        timeout=5)
                    system(self.cmd1)
                    sleep(1)
                else:
                    self.cmd1 = "/usr/camscript/" + \
                        self.softcamslist[self.last][0] + ".sh" + " cam_down &"
                    _session.open(
                        MessageBox,
                        _("Please wait..\nSTOP & RESTART CAM"),
                        MessageBox.TYPE_INFO,
                        timeout=5)
                    system(self.cmd1)
                    sleep(1)
                    self.cmd1 = "/usr/camscript/" + \
                        self.softcamslist[self.var][0] + ".sh" + " cam_up &"
                    system(self.cmd1)
            else:
                try:
                    self.cmd1 = "/usr/camscript/" + \
                        self.softcamslist[self.var][0] + ".sh" + " cam_up &"
                    _session.open(
                        MessageBox,
                        _("Please wait..\nSTART UP CAM"),
                        MessageBox.TYPE_INFO,
                        timeout=5)
                    system(self.cmd1)
                    sleep(1)
                except BaseException:
                    self.close()

            if self.last != self.var:
                try:
                    self.curCam = self.softcamslist[self.var][0]
                    self.writeFile()
                except BaseException:
                    self.close()

        self.session.nav.playService(self.oldService)
        self.EcmInfoPollTimer.start(200)
        self.readScripts()

    def writeFile(self):
        if self.curCam != "" or self.curCam is not None:
            print("self.curCam= 2 ", self.curCam)
            if sys.version_info[0] == 3:
                clist = open("/etc/clist.list", "w", encoding="UTF-8")
            else:
                clist = open("/etc/clist.list", "w")
            system("chmod 755 /etc/clist.list")
            clist.write(str(self.curCam))
            clist.close()

        if sys.version_info[0] == 3:
            stcam = open("/etc/startcam.sh", "w", encoding="UTF-8")
        else:
            stcam = open("/etc/startcam.sh", "w")
        stcam.write("#!/bin/sh\n" + self.cmd1)
        stcam.close()
        system("chmod 755 /etc/startcam.sh")
        return

    def stop(self):
        i = len(self.softcamslist)
        if i < 1:
            return

        global runningcam
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        except BaseException:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()

        self.session.nav.stopService()
        if self.curCam and self.curCam != "None":
            self.EcmInfoPollTimer.stop()
            self.last = self.getLastIndex()

            if self.last is not None:
                self.cmd1 = "/usr/camscript/" + \
                    self.softcamslist[self.last][0] + ".sh" + " cam_down &"
                system(self.cmd1)
                self.curCam = None
                self.writeFile()
                sleep(1)

                if exists(ECM_INFO):
                    remove(ECM_INFO)

                self.session.open(
                    MessageBox,
                    _("Please wait..\nSTOP CAM"),
                    MessageBox.TYPE_INFO,
                    timeout=5)
                self["info"].setText("CAM STOPPED")
                self.BlueAction = "SOFTCAM"
                runningcam = "softcam"
                self.readScripts()
        self.session.nav.playService(self.oldService)

    def readScripts(self):
        try:
            scriptlist = []
            pliste = []
            self.index = 0
            s = 0
            pathscript = "/usr/camscript/"
            for root, dirs, files in walk(pathscript):
                for name in files:
                    scriptlist.append(name)
                    s += 1
            i = len(self.softcamslist)
            del self.softcamslist[0:i]
            png1 = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/tvManager/res/img/{}".format("actcam.png")))
            png2 = LoadPixmap(
                cached=True,
                path=resolveFilename(
                    SCOPE_PLUGINS,
                    "Extensions/tvManager/res/img/{}".format("defcam.png")))
            if s >= 1:
                for lines in scriptlist:
                    dat = pathscript + lines
                    if sys.version_info[0] == 3:
                        sfile = open(dat, "r", encoding="UTF-8")
                    else:
                        sfile = open(dat, "r")
                    for line in sfile:
                        if line[0:3] == "OSD":
                            nam = line[5:len(line) - 2]
                            print(
                                "We are in tvManager and cam is type  = ", nam)
                            if self.curCam != "None" or self.curCam is not None:
                                if nam == self.curCam:
                                    self.softcamslist.append(
                                        (nam, png1, "(Active)"))
                                    pliste.append((nam, "(Active)"))
                                else:
                                    self.softcamslist.append((nam, png2, ""))
                                    pliste.append((nam, ""))
                            else:
                                self.softcamslist.append((nam, png2, ""))
                                pliste.append((nam, ""))
                            self.index += 1
                    sfile.close()
                self.softcamslist.sort(key=lambda i: i[2], reverse=True)
                pliste.sort(key=lambda i: i[1], reverse=True)
                self.namelist = pliste
                print("self.namelist:", self.namelist)
                self["list"].setList(self.softcamslist)
            self.setBlueKey()
        except Exception as e:
            print("error scriptlist: ", e)

    def readCurrent(self):
        currCam = None
        self.FilCurr = ""
        if exists("/etc/CurrentBhCamName"):
            self.FilCurr = "/etc/CurrentBhCamName"
        else:
            self.FilCurr = "/etc/clist.list"
        if stat(self.FilCurr).st_size > 0:
            try:
                if sys.version_info[0] == 3:
                    clist = open(self.FilCurr, "r", encoding="UTF-8")
                else:
                    clist = open(self.FilCurr, "r")
            except BaseException:
                return
            if clist is not None:
                for line in clist:
                    currCam = line
                clist.close()
        return currCam

    """
    def autocam(self):
        current = None
        try:
            # clist = open("/etc/clist.list", "r")
            if sys.version_info[0] == 3:
                clist = open("/etc/clist.list", "r", encoding="UTF-8")
            else:
                clist = open("/etc/clist.list", "r")
            print("found list")
        except:
            return

        if clist is not None:
            for line in clist:
                current = line
            clist.close()
        print("current =", current)
        if os.path.isfile("/etc/autocam.txt") is False:
            if sys.version_info[0] == 3:
                alist = open("/etc/autocam.txt", "w", encoding="UTF-8")
            else:
                alist = open("/etc/autocam.txt", "w")
            alist.close()
        self.cleanauto()
        if sys.version_info[0] == 3:
            alist = open("/etc/autocam.txt", "a", encoding="UTF-8")
        else:
            alist = open("/etc/autocam.txt", "a")
        alist.write(self.oldService.toString() + "\n")
        # last = self.getLastIndex()
        alist.write(current + "\n")
        alist.close()
        self.session.openWithCallback(self.callback, MessageBox, _("Autocam assigned to the current channel"), type=1, timeout=10)
        return

    def cleanauto(self):
        delemu = "no"
        if os.path.isfile("/etc/autocam.txt") is False:
            return
        if sys.version_info[0] == 3:
            myfile = open("/etc/autocam.txt", "r", encoding="UTF-8")
        else:
            myfile = open("/etc/autocam.txt", "r")

        if sys.version_info[0] == 3:
            myfile2 = open("/etc/autocam2.txt", "w", encoding="UTF-8")
        else:
            myfile2 = open("/etc/autocam2.txt", "w")
        icount = 0
        for line in myfile.readlines():
            if line[:-1] == self.oldService.toString():
                delemu = "yes"
                icount = icount + 1
                continue
            if delemu == "yes":
                delemu = "no"
                icount = icount + 1
                continue
            myfile2.write(line)
            icount = icount + 1
        myfile.close()
        myfile2.close()
        system("rm /etc/autocam.txt")
        system("cp /etc/autocam2.txt /etc/autocam.txt")
        """

    def cancel(self):
        self.close()


class GetipklistTv(Screen):

    def __init__(self, session):
        self.session = session
        skin = join(skin_path, "GetipkTv.xml")
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.names = []
        self.names_1 = []
        self.list = []
        self["list"] = MenuList([])
        self.setTitle(_(TITLE_PLUG))
        self["title"] = Label(_(TITLE_PLUG))
        self["description"] = Label(_("Getting the list, please wait ..."))
        self["paypal"] = Label()
        self["key_red"] = Button(_("Back"))
        self["key_green"] = Button(_("Load"))
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        self["key_green"].hide()
        if exists(FILE_XML):
            self["key_green"].show()
        self["key_yellow"].hide()
        self["key_blue"].hide()
        self.addon = "emu"
        self.url = ""
        self.xml = b64decode(ftpxml).decode('utf-8')
        self.icount = 0
        self.downloading = False
        self.timer = eTimer()
        if exists("/usr/bin/apt-get"):
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(500, 1)
        self["actions"] = ActionMap(
            [
                "OkCancelActions",
                "ColorActions"
            ],
            {
                "ok": self.okClicked,
                "cancel": self.close,
                "green": self.loadpage,
                "red": self.close
            },
            -1
        )
        self.onShown.append(self.pasx)

    def pasx(self):
        pass

    def updateList(self):
        payp = paypal()
        self["paypal"].setText(payp)

    def loadpage(self):
        global local
        if exists(FILE_XML):
            self.lists = []
            del self.names[:]
            del self.list[:]
            self["list"].l.setList(self.list)
            with open(FILE_XML, "r") as f:
                self.xml = f.read()
                local = True
                self._gotPageLoad()

    def _gotPageLoad(self):
        if local:
            if exists("/usr/bin/apt-get"):
                print("have an dreamOs!!!")
                self.data = checkGZIP(self.xml)
                print("XML Data fetched via checkGZIP")
                self.downloadxmlpage(self.data)
            else:
                print("have an Atv-PLi - etc..!!!")
                getPage(self.xml.encode(
                    "utf-8")).addCallback(self.downloadxmlpage).addErrback(self.errorLoad)
        else:
            getPage(self.xml.encode("utf-8")
                    ).addCallback(self.downloadxmlpage).addErrback(self.errorLoad)
            print("Local XML loaded")

    def downloadxmlpage(self, data):
        print("Downloading XML page...")
        self.xml = data
        self.list = []
        self.names = []
        try:
            if self.xml:
                print("Parsing XML...")
                self.xmlparse = minidom.parseString(self.xml)
                for plugins in self.xmlparse.getElementsByTagName("plugins"):
                    if not exists("/usr/bin/apt-get"):
                        if "deb" in str(plugins.getAttribute("cont")).lower():
                            continue

                    if exists("/usr/bin/apt-get"):
                        if "deb" not in str(
                                plugins.getAttribute("cont")).lower():
                            continue
                    self.names.append(str(plugins.getAttribute("cont")))
                print("have an Atv-PLi - etc..!!!", self.names)
                self["list"].l.setList(self.names)
                self["description"].setText(_("Please select ..."))
                self.downloading = True
        except Exception as e:
            print("Error during XML parsing:", e)
            self["description"].setText(
                _("Error processing server addons data"))

    def errorLoad(self, error):
        print(str(error))
        self["description"].setText(_("Try again later ..."))
        self.downloading = False

    def okClicked(self):
        try:
            if self.downloading is True:
                selection = str(self["list"].getCurrent())
                self.session.open(GetipkTv, self.xmlparse, selection)
            else:
                self.close()
        except BaseException:
            return


class GetipkTv(Screen):
    def __init__(self, session, xmlparse, selection):
        Screen.__init__(self, session)
        self.session = session
        skin = join(skin_path, "GetipkTv.xml")
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.xmlparse = xmlparse
        self.selection = selection
        self.list = []
        adlist = []
        for plugins in self.xmlparse.getElementsByTagName("plugins"):
            if str(plugins.getAttribute("cont")) == self.selection:
                for plugin in plugins.getElementsByTagName("plugin"):
                    adlist.append(str(plugin.getAttribute("name")))
                continue
        adlist.sort()
        self["list"] = MenuList(adlist)
        self.setTitle(_(TITLE_PLUG))
        self["title"] = Label(_(TITLE_PLUG))
        self["description"] = Label(_("Select and Install"))
        self["paypal"] = Label()
        self["key_red"] = Button(_("Back"))
        self["key_green"] = Button("Remove")
        self["key_yellow"] = Button("Restart")
        self["key_blue"] = Button()
        self["key_green"].hide()
        # self["key_yellow"].hide()
        self["key_blue"].hide()
        self["actions"] = ActionMap(
            [
                "OkCancelActions",
                "ColorActions"
            ],
            {
                "ok": self.message,
                "cancel": self.close,
                # "green": self.remove,
                "yellow": self.restart,
            },
            -1
        )
        self.onLayoutFinish.append(self.start)

    def start(self):
        pass

    def updateList(self):
        payp = paypal()
        self["paypal"].setText(payp)

    def message(self):
        self.session.openWithCallback(
            self.selclicked,
            MessageBox,
            _("Do you install this plugin ?"),
            MessageBox.TYPE_YESNO)

    def selclicked(self, result):
        if result:
            try:
                selection_country = self["list"].getCurrent()
                for plugins in self.xmlparse.getElementsByTagName("plugins"):
                    if str(plugins.getAttribute("cont")) == self.selection:
                        for plugin in plugins.getElementsByTagName("plugin"):
                            if str(
                                    plugin.getAttribute("name")) == selection_country:
                                self.com = str(
                                    plugin.getElementsByTagName("url")[0].childNodes[0].data)
                                self.dom = str(plugin.getAttribute("name"))
                                # test lululla
                                self.com = self.com.replace('"', "")
                                if ".deb" in self.com:
                                    if not exists("/usr/bin/apt-get"):
                                        self.session.open(
                                            MessageBox, _("Unknow Image!"), MessageBox.TYPE_INFO, timeout=5)
                                        return
                                    n2 = self.com.find("_", 0)
                                    self.dom = self.com[:n2]

                                if ".ipk" in self.com:
                                    if exists("/usr/bin/apt-get"):
                                        self.session.open(
                                            MessageBox, _("Unknow Image!"), MessageBox.TYPE_INFO, timeout=5)
                                        return
                                    n2 = self.com.find("_", 0)
                                    self.dom = self.com[:n2]
                                elif ".zip" in self.com:
                                    self.dom = self.com
                                elif ".tar" in self.com or ".gz" in self.com or "bz2" in self.com:
                                    self.dom = self.com
                                print("self.prombt self.com: ", self.com)
                                self.prombt()
                            else:
                                print("Return from prompt ")
                                self["description"].setText("Select")
                            continue
            except Exception as e:
                print("error prompt ", e)
                self["description"].setText("Error")
                return

    def prombt(self):
        self.plug = self.com.split("/")[-1]
        dest = "/tmp"
        if not exists(dest):
            system("ln -sf  /var/volatile/tmp /tmp")
        self.folddest = "/tmp/" + self.plug
        cmd2 = ""
        if ".deb" in self.plug:
            cmd2 = "dpkg -i '/tmp/" + self.plug + "'"
        if ".ipk" in self.plug:
            cmd2 = "opkg install --force-reinstall --force-overwrite '/tmp/" + self.plug + "'"
        elif ".zip" in self.plug:
            cmd2 = "unzip -o -q '/tmp/" + self.plug + "' -d /"
        elif ".tar" in self.plug and "gz" in self.plug:
            cmd2 = "tar -xvf '/tmp/" + self.plug + "' -C /"
        elif ".bz2" in self.plug and "gz" in self.plug:
            cmd2 = "tar -xjvf '/tmp/" + self.plug + "' -C /"
        cmd = cmd2
        cmd00 = "wget --no-check-certificate -U '%s' -c '%s' -O '%s';%s > /dev/null" % (
            AgentRequest, str(self.com), self.folddest, cmd)
        print("cmd00:", cmd00)
        title = (_("Installing %s\nPlease Wait...") % self.dom)
        self.session.open(Console, _(title), [cmd00], closeOnSuccess=False)

    def remove(self):
        self.session.openWithCallback(
            self.removenow,
            MessageBox,
            _("Do you want to remove?"),
            MessageBox.TYPE_YESNO)

    def removenow(self, answer=False):
        if answer:
            selection_country = self["list"].getCurrent()
            for plugins in self.xmlparse.getElementsByTagName("plugins"):
                if str(plugins.getAttribute("cont")) == self.selection:
                    for plugin in plugins.getElementsByTagName("plugin"):
                        if str(
                                plugin.getAttribute("name")) == selection_country:
                            self.com = str(
                                plugin.getElementsByTagName("url")[0].childNodes[0].data)
                            self.dom = str(plugin.getAttribute("name"))
                            # test lululla
                            self.com = self.com.replace('"', "")
                            cmd = ""

                            if ".deb" in self.com:
                                if not exists("/usr/bin/apt-get"):
                                    self.session.open(
                                        MessageBox, _("Unknow Image!"), MessageBox.TYPE_INFO, timeout=5)
                                    return
                                self.plug = self.com.split("/")[-1]
                                n2 = self.plug.find("_", 0)
                                self.dom = self.plug[:n2]
                                cmd = "dpkg -r " + self.dom  # + """
                                print("cmd deb remove:", cmd)
                            if ".ipk" in self.com:
                                if exists("/usr/bin/apt-get"):
                                    self.session.open(
                                        MessageBox, _("Unknow Image!"), MessageBox.TYPE_INFO, timeout=5)
                                    return
                                self.plug = self.com.split("/")[-1]
                                n2 = self.plug.find("_", 0)
                                self.dom = self.plug[:n2]
                                cmd = "opkg remove " + self.dom  # + """
                                print("cmd ipk remove:", cmd)

                            title = (_("Removing %s") % self.dom)
                            self.session.open(Console, _(title), [cmd])

    def restart(self):
        self.session.openWithCallback(
            self.restartnow,
            MessageBox,
            _("Do you want to restart Gui Interface?"),
            MessageBox.TYPE_YESNO)

    def restartnow(self, answer=False):
        if answer:
            self.session.open(TryQuitMainloop, 3)


class InfoCfg(Screen):
    def __init__(self, session):
        self.session = session
        skin = join(skin_path, "InfoCfg.xml")
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        self.list = []
        self.setTitle(_(TITLE_PLUG))
        self["list"] = Label()
        self["actions"] = ActionMap(
            [
                "OkCancelActions",
                "DirectionActions",
                "HotkeyActions",
                "InfobarEPGActions",
                "ColorActions",
                "ChannelSelectBaseActions"
            ],
            {
                "ok": self.close,
                "back": self.close,
                "cancel": self.close,
                "yellow": self.update_me,
                "green": self.update_dev,
                "blue": self.toggleContent,
                "yellow_long": self.update_dev,
                "info_long": self.update_dev,
                "infolong": self.update_dev,
                "showEventInfoPlugin": self.update_dev,
                "red": self.close,
                "up": self.pageUp,
                "down": self.pageDown
            },
            -1
        )
        self["paypal"] = Label()
        self["key_red"] = Button(_("Back"))
        self["key_green"] = Button(_("Force Update"))
        self["key_yellow"] = Button(_("Update"))
        self["key_blue"] = Button(_("Resources"))
        self["key_green"].hide()
        self["key_yellow"].hide()
        self["key_blue"].show()

        self.Update = False
        self.current_content = "help"  # help, resources, system
        self.timer = eTimer()
        if exists("/usr/bin/apt-get"):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(500, 1)
        self["title"] = Label(_(TITLE_PLUG))
        self.onShown.append(self.updateList)

    def check_vers(self):
        remote_version = "0.0"
        remote_changelog = ""
        req = Request(
            b64decoder(installer_url), headers={
                "User-Agent": AgentRequest})
        page = urlopen(req).read()
        if PY3:
            data = page.decode("utf-8")
        else:
            data = page.encode("utf-8")
        if data:
            lines = data.split("\n")
            for line in lines:
                if line.startswith("version"):
                    remote_version = line.split("=")
                    remote_version = line.split("'")[1]
                if line.startswith("changelog"):
                    remote_changelog = line.split("=")
                    remote_changelog = line.split("'")[1]
                    break
        self.new_version = remote_version
        self.new_changelog = remote_changelog
        if currversion < remote_version:
            self.Update = True
            self["key_yellow"].show()
            self.session.open(
                MessageBox,
                _("New version %s is available\n\nChangelog: %s\n\nPress yellow button to update.") %
                (self.new_version,
                 self.new_changelog),
                MessageBox.TYPE_INFO,
                timeout=5)
        self["key_green"].show()

    def update_me(self):
        if self.Update is True:
            self.session.openWithCallback(
                self.install_update,
                MessageBox,
                _("New version %s is available.\n\nChangelog: %s \n\nInstall now?") %
                (self.new_version,
                 self.new_changelog),
                MessageBox.TYPE_YESNO)
        else:
            self.session.open(
                MessageBox,
                _("You have the latest version!"),
                MessageBox.TYPE_INFO,
                timeout=3)

    def update_dev(self):
        req = Request(
            b64decoder(developer_url), headers={
                "User-Agent": AgentRequest})
        page = urlopen(req).read()
        data = json.loads(page)
        remote_date = data["pushed_at"]
        strp_remote_date = datetime.strptime(remote_date, "%Y-%m-%dT%H:%M:%SZ")
        remote_date = strp_remote_date.strftime("%Y-%m-%d")
        self.session.openWithCallback(
            self.install_update, MessageBox, _(
                "Install developer update (%s)?" %
                remote_date), MessageBox.TYPE_YESNO)

    def install_update(self, answer=False):
        if answer:
            self.session.open(
                Console,
                "Upgrading...",
                cmdlist=(
                    "wget -q --no-check-certificate " +
                    b64decoder(installer_url) +
                    " -O - | /bin/sh"),
                finishedCallback=self.myCallback,
                closeOnSuccess=False)
        else:
            self.session.open(
                MessageBox,
                _("Update Aborted!"),
                MessageBox.TYPE_INFO,
                timeout=3)

    def myCallback(self, result=None):
        print("result:", result)
        return

    def get_help_content(self):
        """Compact help content"""
        help_text = _("""QUICK HELP - SOFTCOM MANAGER
            SHORTCUT KEYS:
            0-Keys Update  1-CCcam Info
            2-OSCam Info   3-NCam Info
            4-Create Bkp   5-Restore Bkp
            8-This Help    9-Restart GUI

            CONFIG PATHS:
            CCcam: /etc/CCcam.cfg
            OScam: /etc/tuxbox/config/oscam.server
            NCam: /etc/tuxbox/config/ncam.server
            Keys: /usr/keys/SoftCam.Key

            BLUE BUTTON: Opens active cam info
            GREEN: Start/Restart cam
            RED: Stop cam
            YELLOW: Download cams""")
        return help_text

    def get_resource_content(self):
        """System resource content"""
        try:
            # Basic system info
            arc = popen("uname -m").read().strip() or "N/A"
            python = popen("python -V").read().strip() or "N/A"

            # Memory info
            memory = "N/A"
            if exists("/proc/meminfo"):
                with open("/proc/meminfo", "r") as f:
                    content = f.read()
                    if "MemTotal" in content and "MemAvailable" in content:
                        # Simplified memory calculation
                        pass
            # Disk info
            disk = "N/A"
            success, disk_info = safe_system_call(
                "df -h / | tail -1 | awk '{print $4\"/\"$2\" (\"$5\" used)\"}'", timeout=3)
            if success:
                disk = disk_info.decode().strip() if isinstance(
                    disk_info, bytes) else disk_info.strip()
            resource_text = _("""SYSTEM RESOURCES
                Architecture: %s
                Python: %s
                Memory: %s
                Disk: %s
                ACTIVE CAM: %s""") % (arc, python, memory, disk, self.get_active_cam())
            return resource_text

        except Exception as e:
            return _("Error loading system info: " + str(e))

    def get_system_content(self):
        """System information content"""
        try:
            arc = popen("uname -m").read().strip() or "N/A"
            python = popen("python -V").read().strip() or "N/A"
            arch_info = self.arckget() or "N/A"
            libssl = "N/A"
            success, libs = safe_system_call(
                "ls -1 /usr/lib/libssl.so* 2>/dev/null | head -1", timeout=3)
            if success and libs:
                libssl = libs.decode().strip() if isinstance(libs, bytes) else libs.strip()
            system_text = _("""SYSTEM INFORMATION
                CPU Arch: %s
                Platform: %s
                Python: %s
                LibSSL: %s
                Image: %s""") % (arc, arch_info, python, libssl, self.get_image_info())
            return system_text
        except Exception as e:
            return _("Error loading system information: " + str(e))

    def get_active_cam(self):
        """Get active cam name"""
        try:
            if hasattr(
                    self,
                    'session') and hasattr(
                    self.session,
                    'softcam_manager'):
                return self.session.softcam_manager.curCam or "None"
            return "None"
        except BaseException:
            return "None"

    def get_image_info(self):
        """Get image information"""
        try:
            if exists("/etc/issue"):
                with open("/etc/issue", "r") as f:
                    return f.read().strip()
            elif exists("/etc/image-version"):
                with open("/etc/image-version", "r") as f:
                    return f.read().strip()
            return "Unknown"
        except BaseException:
            return "Unknown"

    def arckget(self):
        """Get architecture information"""
        try:
            if exists("/usr/bin/apt-get"):
                return popen(
                    "dpkg --print-architecture").read().strip() or "N/A"
            else:
                return popen(
                    "opkg print-architecture | head -1").read().strip() or "N/A"
        except BaseException:
            return "N/A"

    def toggleContent(self):
        """Switch between help, resources and system with BLUE key"""
        contents = ["help", "resources", "system"]
        current_index = contents.index(self.current_content)
        self.current_content = contents[(current_index + 1) % len(contents)]
        self.updateList()

    def updateList(self):
        """Update displayed content"""
        payp = paypal()
        self["paypal"].setText(payp)

        if self.current_content == "help":
            content = self.get_help_content()
            self["key_blue"].setText(_("Resources"))
        elif self.current_content == "resources":
            content = self.get_resource_content()
            self["key_blue"].setText(_("System"))
        else:  # system
            content = self.get_system_content()
            self["key_blue"].setText(_("Help"))

        self["list"].setText(content)

    def pageUp(self):
        """Scroll up - change content"""
        contents = ["help", "resources", "system"]
        current_index = contents.index(self.current_content)
        self.current_content = contents[(current_index - 1) % len(contents)]
        self.updateList()

    def pageDown(self):
        """Scroll down - change content"""
        contents = ["help", "resources", "system"]
        current_index = contents.index(self.current_content)
        self.current_content = contents[(current_index + 1) % len(contents)]
        self.updateList()


class DreamCCAuto:
    def __init__(self):
        self.readCurrent()

    def readCurrent(self):
        current = None
        self.FilCurr = "/etc/CurrentBhCamName" if exists(
            "/etc/CurrentBhCamName") else "/etc/clist.list"
        try:
            with open(self.FilCurr, "r", encoding="UTF-8") as clist:
                for line in clist:
                    current = line.strip()
        except Exception as e:
            print("Error reading current cam file:", e)
            return

        print("Current cam name:", current)

        scriptliste = []
        path = "/usr/camscript/"
        if not exists(path):
            print("Path does not exist:", path)
            return

        for root, dirs, files in walk(path):
            for name in files:
                scriptliste.append(name)

        for script in scriptliste:
            dat = join(path, script)
            try:
                with open(dat, "r") as file:
                    for line in file:
                        if line.startswith("OSD"):
                            nam = line[5:].strip()
                            if current == nam:
                                if exists("/etc/init.d/dccamd"):
                                    system(
                                        "mv /etc/init.d/dccamd /etc/init.d/dccamdOrig &")
                                for link, target in [
                                        ("/var/bin", "/usr/bin"), ("/var/keys", "/usr/keys"), ("/var/scce", "/usr/scce"), ("/var/script", "/usr/script")]:
                                    if not islink(link):
                                        system("ln -sf %s %s" % (target, link))
                                if system("/etc/startcam.sh") != 0:
                                    print(
                                        "Error starting the cam with /etc/startcam.sh")
                                else:
                                    print("*** running autostart ***")
                                return
            except Exception as e:
                print("Error reading script file:", e)

        print("pass autostart")
        return


def autostartsoftcam(reason, session=None, **kwargs):
    """Simplified autostart without timeout"""
    print("[Softcam] Autostart initiated")

    if reason == 0 and session is not None:
        print("Autostart reason: 0")

        try:
            # Backup dccamd file if exists
            if exists("/etc/init.d/dccamd"):
                system("mv /etc/init.d/dccamd /etc/init.d/dccamdOrig &")

            # Create symbolic links if needed
            links = [
                ("/var/bin", "/usr/bin"),
                ("/var/keys", "/usr/keys"),
                ("/var/scce", "/usr/scce"),
                ("/var/script", "/usr/script")
            ]

            for link, target in links:
                if not islink(link):
                    system("ln -sf %s %s" % (target, link))

            print("Starting softcam in background...")
            system("/bin/bash /etc/startcam.sh &")
            print("[Softcam] Start command executed")

        except Exception as e:
            print("Autostart error: %s" % str(e))


def main(session, **kwargs):
    try:
        cleanup_temp_files()
        missing_deps = check_dependencies()
        if missing_deps:
            print("Missing dependencies: %s" % ", ".join(missing_deps))

        session.open(tvManager)
    except Exception as e:
        print("Error in main: %s" % str(e))
        import traceback
        traceback.print_exc()


def startConfig(session, **kwargs):
    session.open(tvManager)


def mainmenu(menu_id):
    if menu_id == "setup":
        return [
            (
                _("Softcam Manager"),
                startConfig,
                "Softcam Manager",
                50
            )
        ]
    else:
        return []


def Plugins(**kwargs):
    ICONPIC = "logo.png"
    return [
        PluginDescriptor(
            name=_(NAME_PLUG),
            where=PluginDescriptor.WHERE_MENU,
            fnc=mainmenu),
        PluginDescriptor(
            name=_(NAME_PLUG),
            description=_(TITLE_PLUG),
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART],
            needsRestart=True,
            fnc=autostartsoftcam,
        ),
        PluginDescriptor(
            name=_(NAME_PLUG),
            description=_(TITLE_PLUG),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon=ICONPIC,
            fnc=main),
        PluginDescriptor(
            name=_(NAME_PLUG),
            description=_(TITLE_PLUG),
            where=PluginDescriptor.WHERE_EXTENSIONSMENU,
            fnc=main),
    ]
