#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
===============================================================================
 CCcam Auto Collector - Advanced version
 ===============================================================================
 This module collects free CCcam lines from multiple sources, tests them,
 and writes active servers to the specified oscam.server file.
 It preserves personal readers and uses markers to replace only the generated
 section, preventing file bloat.
===============================================================================
"""

import re
import socket
import time
import os
import requests
import urllib3
from datetime import datetime, timedelta
from threading import Thread

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MyCCcamCollector(object):
    def __init__(self, output_path="/etc/tuxbox/config/oscam.server"):
        self.output_path = output_path
        self.tag = "lululla"                # Marker for generated readers
        self.max_servers = 40
        self.min_stars = 0                  # 0 = all
        self.max_output = 30

    # ----- Helper: extract CCcam line from HTML -----
    def _extract_cccam_line(self, html, source_name, source_icon):
        servers = []
        pattern = r'[Cc]:\s+(\S+)\s+(\d+)\s+(\S+)\s+([^\s<]+)'
        for match in re.finditer(pattern, html):
            host, port, user, password = match.groups()
            password = re.sub(r'<[^>]+>', '', password).strip()
            if len(user) > 2 and len(password) > 2 and host and port:
                servers.append({
                    'host': host.strip(),
                    'port': port.strip(),
                    'username': user.strip(),
                    'password': password.strip(),
                    'source': source_name,
                    'source_icon': source_icon,
                })
        return servers

    # ----- Scrapers -----
    def _fetch_testious(self):
        """testious.com – tries today and yesterday"""
        servers = []
        for days in range(2):
            date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            url = "https://testious.com/old-free-cccam-servers/{}/".format(
                date)
            try:
                r = requests.get(url, timeout=8, verify=False)
                if r.status_code == 200:
                    servers.extend(
                        self._extract_cccam_line(
                            r.text, 'testious', '[T]'))
                    if len(servers) >= 8:
                        break
            except BaseException:
                pass
        return servers[:8]

    def _fetch_cccamnet(self):
        try:
            url = 'https://cccam.net/freecccam'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            }
            r = requests.get(url, headers=headers, timeout=8, verify=False)
            if r.status_code == 200:
                return self._extract_cccam_line(r.text, 'cccamnet', '[CN]')[:5]
        except BaseException:
            pass
        return []

    def _fetch_cccamlive(self):
        try:
            url = 'https://cccam.live/freetest1/test2.php'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            }
            r = requests.get(url, headers=headers, timeout=8, verify=False)
            if r.status_code == 200:
                return self._extract_cccam_line(
                    r.text, 'cccamlive', '[CL]')[:3]
        except BaseException:
            pass
        return []

    def _fetch_cccampremium(self):
        try:
            url = 'https://cccam-premium.pro/free-cccam/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            }
            r = requests.get(url, headers=headers, timeout=8, verify=False)
            if r.status_code == 200:
                return self._extract_cccam_line(
                    r.text, 'cccampremium', '[CM]')[:5]
        except BaseException:
            pass
        return []

    def _fetch_cccamhub(self):
        try:
            r = requests.get(
                'https://cccamhub.com/cccamfree/',
                timeout=6,
                verify=False)
            if r.status_code == 200:
                return self._extract_cccam_line(r.text, 'cccamhub', '[CH]')[:5]
        except BaseException:
            pass
        return []

    def _fetch_cccamiptv(self):
        try:
            r = requests.get(
                'https://cccamiptv.club/free-cccam/',
                timeout=6,
                verify=False)
            if r.status_code == 200:
                return self._extract_cccam_line(
                    r.text, 'cccamiptv', '[CI]')[:5]
        except BaseException:
            pass
        return []

    def _fetch_tvcccamnet(self):
        try:
            url = 'https://tv.cccam.net/free'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            }
            r = requests.get(url, headers=headers, timeout=8, verify=False)
            if r.status_code == 200:
                return self._extract_cccam_line(
                    r.text, 'tvcccamnet', '[TV]')[:3]
        except BaseException:
            pass
        return []

    # ----- Connection test -----
    def _test_server(self, server):
        host = server['host']
        port = int(server['port'])
        try:
            ip = socket.gethostbyname(host)
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, port))
            elapsed = int((time.time() - start) * 1000)
            sock.close()
            if result == 0:
                if elapsed < 100:
                    stars = 5
                elif elapsed < 200:
                    stars = 4
                elif elapsed < 400:
                    stars = 3
                elif elapsed < 800:
                    stars = 2
                else:
                    stars = 1
                return True, elapsed, stars
            else:
                return False, 0, 0
        except Exception:
            return False, 0, 0

    # ----- Collect and test servers -----
    def _collect_servers(self, status_callback=None):
        all_servers = []
        scrapers = [
            self._fetch_testious,
            self._fetch_cccamnet,
            self._fetch_cccampremium,
            self._fetch_cccamhub,
            self._fetch_cccamiptv,
            self._fetch_cccamlive,
            self._fetch_tvcccamnet,
        ]
        for scraper in scrapers:
            if status_callback:
                status_callback("Scraping {}...".format(scraper.__name__))
            try:
                servers = scraper()
                all_servers.extend(servers)
                if status_callback:
                    status_callback("  Found {} servers".format(len(servers)))
            except Exception as e:
                if status_callback:
                    status_callback("  Error: {}".format(e))

        # Deduplicate
        unique = {}
        for s in all_servers:
            key = "{}:{}:{}".format(s['host'], s['port'], s['username'])
            if key not in unique:
                unique[key] = s
        servers = list(unique.values())
        if len(servers) > self.max_servers:
            servers = servers[:self.max_servers]

        if status_callback:
            status_callback(
                "Testing {} unique servers...".format(
                    len(servers)))

        # Test each
        active = []
        for idx, s in enumerate(servers, 1):
            ok, ping, stars = self._test_server(s)
            s['status'] = 'active' if ok else 'failed'
            s['ping'] = ping
            s['stars'] = stars
            if ok:
                active.append(s)
            if status_callback and idx % 5 == 0:
                status_callback(
                    "  Tested {}/{} – {} active".format(idx, len(servers), len(active)))

        # Quality filter
        if self.min_stars > 0:
            active = [s for s in active if s.get('stars', 0) >= self.min_stars]

        # Sort: higher stars first, then lower ping
        active.sort(key=lambda x: (x['stars'], -x['ping']), reverse=True)

        return active[:self.max_output]

    # ----- Generate OSCam reader blocks -----
    def _generate_reader_blocks(self, servers):
        blocks = []
        for i, s in enumerate(servers, 1):
            stars = s.get('stars', 0)
            stars_txt = '★' * stars
            ping = s.get('ping', 0)
            src_icon = s.get('source_icon', '[?]')
            src_name = s.get('source', 'unknown')

            if stars >= 5:
                priority = "EXCELLENT"
                nice = -20
                lb_weight = 500
            elif stars >= 4:
                priority = "VERY GOOD"
                nice = -10
                lb_weight = 400
            elif stars >= 3:
                priority = "GOOD"
                nice = 0
                lb_weight = 300
            else:
                priority = "FAIR"
                nice = 5
                lb_weight = 200

            # Build the reader block without using f-strings
            block = "# [{i}] {src_icon} {stars_txt} - {ping}ms - {priority} - {src_name}\n".format(
                i=i, src_icon=src_icon, stars_txt=stars_txt, ping=ping, priority=priority, src_name=src_name)
            block += "[reader]\n"
            block += "label = {tag}_{i:03d}\n".format(tag=self.tag, i=i)
            block += "enable = 1\n"
            block += "protocol = cccam\n"
            block += "device = {host},{port}\n".format(
                host=s['host'], port=s['port'])
            block += "user = {user}\n".format(user=s['username'])
            block += "password = {password}\n".format(password=s['password'])
            block += "group = 1,2,3,4,5,6,7,8,9,10\n"
            block += "cccversion = 2.3.2\n"
            block += "cccmaxhops = 2\n"
            block += "cccreconnect = 1\n"
            block += "ccckeepalive = 1\n"
            block += "audisabled = 1\n"
            block += "disablecrccws = 1\n"

            if ping < 200:
                block += "cccping = 2\n"
                block += "cccpingmax = 20\n"
                block += "cccbusycarddelay = 1000\n"
            else:
                block += "cccping = 3\n"
                block += "cccpingmax = 30\n"
                block += "cccbusycarddelay = 1500\n"

            block += "lb_weight = {lb_weight}\n".format(lb_weight=lb_weight)
            block += "nice = {nice}\n".format(nice=nice)
            block += "fallback = 0\n"
            block += "disablecrccws_only_for = 0500:030B00,032830,050F00;098C:000000;098D:000000;09C4:000000;1884:000000;1708:000000;1709:000000;1841:000000;1811:003311\n\n"

            blocks.append(block)

        return blocks

    # ----- Write to oscam.server (or any .server file) -----
    def _write_server_config(self, filepath, new_blocks):
        # Ensure directory exists
        dirname = os.path.dirname(filepath)
        if dirname and not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                pass

        # Backup
        if os.path.exists(filepath):
            backup = "{}.backup.{}".format(filepath, int(time.time()))
            os.system("cp '{}' '{}' 2>/dev/null".format(filepath, backup))

        lines_keep = []
        in_generated_section = False
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("# {} start".format(self.tag)):
                        in_generated_section = True
                        continue
                    elif stripped.startswith("# {} end".format(self.tag)):
                        in_generated_section = False
                        continue
                    if in_generated_section:
                        continue
                    lines_keep.append(line.rstrip('\n'))

        new_section = []
        new_section.append("# {} start - {}".format(self.tag,
                                                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        new_section.append(
            "# {} - Auto-generated config".format(self.tag.upper()))
        new_section.append(
            "# Date: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        new_section.append("# Active servers: {}".format(len(new_blocks)))
        new_section.append("")
        new_section.append("# ========================================")
        new_section.append(
            "# READERS GENERATED BY {}".format(
                self.tag.upper()))
        new_section.append("# ========================================")
        new_section.append("")
        new_section.extend(new_blocks)
        new_section.append("# {} end".format(self.tag))

        with open(filepath, 'w') as f:
            for line in lines_keep:
                f.write(line + '\n')
            if lines_keep and not lines_keep[-1].endswith('\n'):
                f.write('\n')
            f.write('\n'.join(new_section) + '\n')

    # ----- Main run method -----
    def run(self, status_callback=None):
        """
        Main entry point. Called from the plugin's thread.
        status_callback is a function that accepts a string for UI updates.
        """
        def task():
            try:
                if status_callback:
                    status_callback("Starting CCcam collector...")

                # Collect and test servers
                active_servers = self._collect_servers(status_callback)

                if not active_servers:
                    if status_callback:
                        status_callback("No active CCcam lines found.")
                    return

                if status_callback:
                    status_callback(
                        "Found {} active servers. Generating config...".format(
                            len(active_servers)))

                # Generate reader blocks
                new_blocks = self._generate_reader_blocks(active_servers)

                # Write to the configured output path
                self._write_server_config(self.output_path, new_blocks)

                if status_callback:
                    status_callback(
                        "Config written to {}".format(
                            self.output_path))

            except Exception as e:
                if status_callback:
                    status_callback("ERROR: {}".format(e))
                else:
                    print("ERROR: {}".format(e))
                raise

        # Run in a separate thread to avoid blocking the GUI
        thread = Thread(target=task)
        thread.start()
