#!/usr/bin/env python
import requests
import platform
import json
from collections import namedtuple
import tempfile
import subprocess
import argparse
import sqlite3
import pandas as pd
import time

pd.options.mode.copy_on_write = True

Cask = namedtuple(
    "Cask", "token name desp version homepage installed update url sha256"
)
version_code_map = {
    "10.11": "el_caption",
    "10.12": "sierra",
    "10.13": "high_sierra",
    "10.14": "mojove",
    "10.15": "catalina",
    "11": "big_sur",
    "12": "monterey",
    "13": "ventura",
    "14": "sonoma",
}
code_version_map = {v: k for k, v in version_code_map.items()}


class PyCask:
    def __init__(self, args):
        self.api_base = "https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api/"
        self.api = self.api_base + "cask.json"
        self.config_path = os.path.expanduser("~/.local/share/pycask")
        self.json_file = os.path.join(self.config_path, "cask.json")
        self.arch = platform.machine()
        self.code = self.get_version_code()
        self.args = args
        self.db_fname = os.path.join(self.config_path, "pycask.db")

        self.df_all = None
        self.jsons = None

        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)

        if os.path.exists(self.json_file):
            stat = os.stat(self.json_file)
            if time.time() - stat.st_mtime < 3600:
                self.load_json()

        if os.path.exists(self.db_fname):
            self.from_sql_db()

        if self.jsons is None:
            self.get_refresh()

        if self.df_all is None:
            self.build_df()

    def to_sql_db(self, name="casks"):
        conn = sqlite3.connect(self.db_fname)
        self.df_all.to_sql(name, conn, index=True, if_exists="replace")
        conn.close()

    def from_sql_db(self, name="casks"):
        conn = sqlite3.connect(self.db_fname)
        self.df_all = pd.read_sql(f"select * from {name}", conn)
        self.df_all = self.df_all.set_index("token")
        conn.close()

    def get_version_code(self):
        version = platform.mac_ver()[0]
        code = "sonoma"
        for v in version_code_map:
            if version.startswith(v):
                code = version_code_map[v]
                break
        return code

    def get_refresh(self):
        print("refresh database")
        res = requests.get(self.api)
        if res.status_code == 200:
            self.jsons = json.loads(res.content.decode())
            f = open(self.json_file, "w")
            f.write(res.content.decode())
            self.build_df()
        else:
            print("return error")

    def load_json(self):
        self.jsons = json.load(open(self.json_file))

    def get_json_results(self):
        results = []
        for cask in self.jsons:

            token = cask["token"]
            name = cask["name"][0]
            desc = cask["desc"]
            homepage = cask["homepage"]
            url = cask["url"]
            sha256 = cask["sha256"]
            installed = 0
            # remove = cask["zap"][
            # ]
            version = cask["version"]
            if self.arch != "arm64":
                variations = cask["variations"]
                url_code = variations.get(self.code, {}).get("url", "")
                sha256_code = variations.get(self.code, {}).get("sha256", "")

                url = url_code if len(url_code) > 0 else url
                sha256 = sha256_code if len(sha256_code) > 0 else sha256
            c = Cask(token, name, desc, version, homepage, installed, None, url, sha256)
            results.append(c)
        return results

    def build_df(self):
        results = self.get_json_results()
        if self.df_all is None:  # initial, no db, df_all not initialized
            self.df_all = pd.DataFrame(results)
            self.df_all = self.df_all.set_index("token")
            # print(self.df_all)
            self.to_sql_db()
        else:
            for cask in results:
                token = cask.token
                if token not in self.df_all.index:
                    # new_casks.append(cask)
                    # print(token)
                    # print(cask)
                    self.df_all.loc[token] = cask[1:]
                    # self.to_sql_db()
                else:
                    df_pkg = self.df_all.loc[token]

                    if df_pkg.version != cask.version:
                        print(
                            f"{cask.token}\r\t\t\t{df_pkg.version.split(',')[0]}\r\t\t\t\t---->\t{cask.version.split(',')[0]}"
                        )
                        self.df_all.loc[token, "url"] = cask.url
                        self.df_all.loc[token, "sha256"] = cask.sha256

                        if df_pkg.installed == 0:
                            self.df_all.loc[token, "version"] = cask.version
                        else:
                            self.df_all.loc[token, "update"] = cask.version
            self.to_sql_db()

    def search(self, key):
        # results = []
        if len(key) < 3:
            print("search key must >= 3")
            return None

        df = self.df_all.query(f"token.str.contains('{key}')")
        return df

    def print_cask(self, cask):
        print(
            f"{cask.installed} {cask.name}\r\t\t\t{cask.version.split(',')[0]}\r\t\t\t\t\t{cask.desp}"
        )

    def download(self, cask, token, upgrade=False):
        if cask["installed"] == 1 and cask["update"] == cask["version"]:
            print(f"{token} with version {cask['version']} alreay installed")
            return True
        print(f"starting download {token}")
        url = cask.url
        dest = tempfile.gettempdir()
        f = os.path.basename(url)
        version_new = cask["update"] if upgrade else cask["version"]
        f = self.get_latest_fname(f, token, version_new)
        command = ["aria2c", "-c", url, "-d", dest, "-o", f]
        print(command)
        popen = subprocess.Popen(command, stdout=sys.stdout)
        out = popen.wait()
        if upgrade and out == 0:
            out == self.remove(token, upgrade)
        if out == 0:  # success
            version_new = cask["update"] if upgrade else cask["version"]
            self.install(os.path.join(dest, f), token=token, version=version_new)
        else:
            print("download failed")
            return False
        return True

    def get_latest_fname(self, fname, token, version):
        format = fname[-3:]
        if format in ["zip", "pkg", "dmg", ".gz", ".xz"]:
            return fname
        fname = f"{token}-{version}.dmg"
        return fname
        
    def install(self, fname, token, version):
        print(f"start install {fname}")
        format = fname[-3:]
        if format not in ["zip", "pkg", "dmg"]:
            format = "dmg"

        getattr(self, f"install_{format}")(fname)

        print(f"{token} installed with version {version}")
        print(f"temp file {fname} removed")
        os.system(f"rm -rf {fname}")
        self.df_all.loc[token, "installed"] = 1
        self.df_all.loc[token, "version"] = version
        self.to_sql_db()

    def remove(self, token, upgrade=False):
        # api = f"{self.api_base}/cask/{token}.json"
        # res = requests.get(api)
        # if res.status_code == 200:
        #     jsons = json.loads(res.content)
        #
        # else:
        #     pass
        jsons = None
        for cask in self.jsons:
            if cask["token"] == token:
                jsons = cask
                break
        if jsons is None:
            print(f"App with name = {token} not found")
            return
        artifacts = jsons["artifacts"]
        for artifact in artifacts:
            apps = artifact.get("app", [])
            for app in apps:

                if " " in app:
                    app = app.replace(" ", "\\ ")
                print(f"rm -rf ~/Applications/{app}")
                os.system(f"rm -rf ~/Applications/{app}")
            if not upgrade:  # when upgrade, not zap apps
                zaps = artifact.get("zap", [])
                for zap in zaps:
                    trashes = zap.get("trash", [])
                    for trash in trashes:
                        print(f"removing... {trash}")
                        os.system(f"rm -rf {trash}")
        if not upgrade:  # when upgrade, not update db when remove
            self.df_all.loc[token, "installed"] = 0
            self.df_all.loc[token, "update"] = None
            self.to_sql_db()

    # def install_dmg(self, fname):
    #    from dmginstall import installDmg
    #    installDmg(fname)

    def install_pkg(self, fname):
        os.system(f"sudo installer -pkg {fname} -target /")

    def install_zip(self, fname):
        temp_dir = tempfile.mkdtemp()
        unzip_cmd = f"unzip -q '{fname}' -d '{temp_dir}'"
        os.system(unzip_cmd)
        self.install_archive(temp_dir)

    def list_pkgs(self):
        df = self.df_all.query("installed==1")
        for idx in df.index:
            pkg = df.loc[idx,]
            self.print_cask(pkg)

    def get_output(self, cmd):
        return subprocess.check_output(cmd, shell=True, universal_newlines=True)

    def copy_app(self, path):
        copy_cmd = f"cp -R '{path}' ~/Applications"
        os.system(copy_cmd)

    def install_dmg(self, path):
        cmd = f"hdiutil attach -noautoopen '{path}'|grep /Volumes"
        block = self.get_output(cmd).split("\t")

        app_path = block[-1].strip()

        second_dmg_cmd = f'find "{app_path}" -maxdepth 1 -iname "*.dmg"'
        second_dmg_path = self.get_output(second_dmg_cmd)
        if second_dmg_path != "":
            second_dmg_path = second_dmg_path.strip()
            temp_dmg_path = "/tmp/_install_tmp.dmg"
            os.system(f"cp '{second_dmg_path}' {temp_dmg_path}")
            self.install_dmg(temp_dmg_path)
            os.system(f"rm -rf {temp_dmg_path}")

        self.install_archive(app_path)
        os.system(f"hdiutil detach {block[0].strip()}")

    def install_archive(self, path):
        formats = ["app", "pkg", "dmg"]
        fmt_path = f"find '{path}' -maxdepth {{}} -name '*.{{}}'"
        for depth in (1, 2):
            for fmt in formats:
                cmd = fmt_path.format(depth, fmt)
                output = self.get_output(cmd).strip()
                if output != "":
                    if depth == 1 and fmt == "dmg":
                        self.install_dmg(output)
                        continue
                    else:
                        if fmt == "app":
                            self.copy_app(output)
                            return
                        elif fmt == "pkg":
                            install_cmd = f'sudo installer -pkg "{output}" -target /'
                            os.system(install_cmd)
                            return
        print("No usable files found")

    def main(self):
        if self.args.search:
            res = self.search(self.args.search)
            if res is None:
                return
            if len(res) == 0:
                print(f"Not found App contains {self.args.search}")
            else:
                for idx in res.index:
                    cask = res.loc[idx]
                    # print(cask)
                    self.print_cask(cask)

        elif self.args.install:

            token = self.args.install
            res = self.search(token)
            if res is None:
                return

            if len(res) == 0:
                print(f"Package with name ({token}) not found")

            elif token in res.index:
                cask = res.loc[token]
                out = self.download(cask, token)
                if out == 0:
                    print(f"Installing. {token} Success!")
            else:
                
                for idx in res.index:
                    self.print_cask(res.loc[idx])
                num = input(f"There are multiple casks, install which one :(1--{len(res.index)})")
                num = int(num)
                if num > 0 and num < len(res.index):
                    token = res.index[num]
                    self.download(res.loc[idx], token)

        elif self.args.upgrade:
            stat = os.stat(self.json_file)
            if time.time() - stat.st_mtime > 600:  # 10min
                self.get_refresh()
            if self.args.upgrade == "*": # upgrade all pkgs
                update_pkgs = self.df_all.query("update.notnull() and update != version")
                if len(update_pkgs) == 0:
                    return
                for idx in update_pkgs.index:
                    pkg = update_pkgs.loc[idx]
                    print(
                        f"{idx}\r\t\t{pkg['name']}\r\t\t\t\t{pkg.version.split(',')[0]}\r\t\t\t\t\t\t--->\t{pkg['update'].split(',')[0]}"
                    )
                choice = input("upgrade all these apps? (y/n)")
                if choice.lower().strip() == "y":
                    for idx in update_pkgs.index:
                        pkg = update_pkgs.loc[idx]
                        self.download(pkg, idx, upgrade=True)
            else:
                token = self.args.upgrade
                if token in self.df_all.index:
                    pkg = self.df_all.loc[token]
                    if pkg["installed"] == 0:
                        print(f"{token} not installed, cannot upgrade")
                    elif pkg["update"] is None or pkg["update"] == pkg["version"]:
                        print(f"{token} No need to upgrade")
                    elif pkg["update"] != pkg["version"]:
                        self.download(pkg, token, upgrade=True)
                        
                else:
                    print(f"No app named {token}")

        elif self.args.list:
            self.list_pkgs()

        elif self.args.remove:
            self.remove(self.args.remove)

        elif self.args.marked:
            token = self.args.marked
            if token in self.df_all.index:
                self.df_all.loc[token, "installed"] = 1
                self.to_sql_db()
            else:
                print(f"Package with {token} not found")


if __name__ == "__main__":
    import os
    import sys

    parser = argparse.ArgumentParser("search cask to install")

    parser.add_argument("-s", "--search", type=str, help="search apps")
    parser.add_argument("-l", "--list", action="store_true", help="list apps")
    parser.add_argument("-i", "--install", type=str, help="install apps")
    parser.add_argument("-r", "--remove", type=str, help="remove apps")
    parser.add_argument("-u", "--upgrade", type=str, nargs="?", const="*", help="update apps or for all")
    parser.add_argument("-m", "--marked", type=str, help="mark a package as installed")

    args = parser.parse_args()
    cask = PyCask(args)
    cask.main()
    # if len(sys.argv) >= 2:
    #    res = cask.search(sys.argv[1])
    #    #cask.download(res[0])
    # else:
    #    print("you should run with ./pycask.py xxxx")
