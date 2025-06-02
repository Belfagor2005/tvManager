from threading import Thread
import requests
import re
import shutil
from os.path import exists


class MyCCcamCollector(object):
    def __init__(self, output_path="/etc/tuxbox/config/oscam.server"):
        self.output_path = output_path
        self.sources = [
            {
                "url": "http://www.cccam-world.com/free-cccam/",
                "regex": r"C:\s+(\S+)\s+(\d+)\s+(\S+)\s+(\S+)"
            },
            {
                "url": "http://cccamiptvworld.com/free-cccam/",
                "regex": r"C:\s+(\S+)\s+(\d+)\s+(\S+)\s+(\S+)"
            },
            {
                "url": "https://cccamiptv.life/free-cccam/",
                "regex": r"C:\s+(\S+)\s+(\d+)\s+(\S+)\s+(\S+)"
            },
            {
                "url": "https://freecccam24.com/",
                "regex": r"(C:\s+\S+\s+\d+\s+\S+\s+\S+)"
            },
        ]
        self.collected = []

    def fetch_url_content(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            print("received {} chars from {}".format(len(response.text), url))
            return response.text
        except Exception as err:
            print("problem reading {}: {}".format(url, err))
            return ""

    def is_valid_server(self, host, port):
        if not host or not port.isdigit():
            return False
        port_number = int(port)
        return 1 <= port_number <= 65535

    def build_config(self, lines):
        result = "# personal readers config generated internally\n\n"
        for index, entry in enumerate(lines, 1):
            parts = entry.split()
            if len(parts) >= 4:
                host = parts[1]
                port = parts[2]
                username = parts[3]
                passwd = parts[4] if len(parts) > 4 else ""
                result += (
                    "[reader]\n"
                    "label = myreader_{}\n"
                    "protocol = cccam\n"
                    "device = {},{}\n"
                    "user = {}\n"
                    "password = {}\n"
                    "group = 1\n"
                    "cccversion = 2.1.2\n"
                    "ccckeepalive = 1\n\n"
                ).format(index, host, port, username, passwd)
        return result

    def fetch_from_cccamx(self):
        try:
            url = "https://cccamx.com/wp-admin/admin-ajax.php?action=get_random_line"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("success") and "C:" in data.get("data", ""):
                return [data["data"]]
        except Exception as e:
            print("Error fetching from cccamx.com:", e)
        return []

    def run(self, status_callback=None):
        def task():
            self.collected = []

            # Step 1: Raccolta dai siti
            for source in self.sources:
                if status_callback:
                    status_callback("Fetching from {}".format(source["url"]))

                raw = self.fetch_url_content(source["url"])
                pattern = re.compile(source["regex"], re.IGNORECASE)

                for match in pattern.finditer(raw):
                    items = match.groups()
                    if len(items) == 4:
                        host, port, user, pwd = items
                    elif len(items) == 1:
                        tokens = items[0].split()
                        if len(tokens) >= 5 and tokens[0].lower(
                        ).startswith("c:"):
                            host = tokens[1]
                            port = tokens[2]
                            user = tokens[3]
                            pwd = tokens[4]
                        else:
                            continue
                    else:
                        continue

                    pwd = pwd.split("<")[0].strip()
                    line = "C: {} {} {} {}".format(host, port, user, pwd)

                    if self.is_valid_server(host, port):
                        self.collected.append(line)
                    else:
                        if status_callback:
                            status_callback("Invalid: {}".format(line))

            # Step 2: Aggiunta da cccamx
            self.collected += self.fetch_from_cccamx()
            self.collected = list(set(self.collected))

            if not self.collected:
                if status_callback:
                    status_callback("No valid entries found.")
                return

            try:
                # Step 3: Leggi contenuto esistente (se esiste)
                existing_content = ""
                if exists(self.output_path):
                    try:
                        shutil.copy2(
                            self.output_path, self.output_path + ".bak")
                        if status_callback:
                            status_callback("Backup created")
                    except Exception as e:
                        if status_callback:
                            status_callback("No backup created: {}".format(e))

                    with open(self.output_path, "r") as handle:
                        existing_content = handle.read()

                # Step 4: Costruzione nuovi reader e scrittura non duplicata
                config_text = self.build_config(self.collected)

                with open(self.output_path, "a") as handle:
                    for reader_block in config_text.strip().split("\n\n"):
                        if reader_block not in existing_content:
                            handle.write(reader_block + "\n\n")

                if status_callback:
                    status_callback("Stored {} entries in {}".format(
                        len(self.collected), self.output_path))
            except Exception as err:
                if status_callback:
                    status_callback("Write error: {}".format(err))

            if status_callback:
                status_callback("finished")

        # Avvia il thread
        thread = Thread(target=task)
        thread.start()
