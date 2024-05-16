#!/usr/bin/env python
import requests
import platform
import json
from pprint import pprint
from collections import namedtuple
import tempfile
import shutil
import subprocess
import argparse
import sqlite3
import pandas as pd
import time
pd.options.mode.copy_on_write = True

Cask = namedtuple("Cask", "token name desp version homepage installed update url sha256")
version_code_map = {
    '10.11': 'el_caption',
    '10.12': 'sierra',
    '10.13': 'high_sierra',
    '10.14': 'mojove',
    '10.15': 'catalina',
    '11': 'big_sur',
    '12': 'monterey',
    '13': 'ventura',
    '14': 'sonoma'
}
code_version_map = {v:k for k,v in version_code_map.items()}


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
        code = 'sonoma'
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
            f = open(self.json_file, 'w')
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
            #remove = cask["zap"][
            #]
            version = cask["version"]
            if self.arch != "arm64":
                veriations = cask["veriations"]
                url_code = veriations.get(self.code, {}).get("url", "")
                sha256_code = veriations.get(self.code, {}).get("sha256", "")

                url = (url_code if len(url_code) > 0 else url)
                sha256 = (sha256_code if len(sha256_code) > 0 else sha256)
            c = Cask(token, name, desc, version, homepage, installed, None, url, sha256)
            results.append(c)
        return results
    
    def build_df(self):
        if self.df_all is None:
            update = False
        else:
            update = True
        results = self.get_json_results()
        if not update: #initial 
            self.df_all = pd.DataFrame(results)
            self.df_all = self.df_all.set_index("token")
            #print(self.df_all)
            self.to_sql_db()
        else:
            for cask in results:
                token = cask.token
                if token not in self.df_all.index:
                    #new_casks.append(cask)
                    #print(token)
                    #print(cask)
                    self.df_all.loc[token] = cask[1:] 
                    #self.to_sql_db()
                else:
                    df_pkg = self.df_all.loc[token]

                    if df_pkg.version != cask.version:
                        print(f"{cask.token}\r\t\t\t{df_pkg.version.split(',')[0]}\r\t\t\t\t---->\t{cask.version.split(',')[0]}")
                        #df_pkg.url = cask.url
                        self.df_all.loc[token, "url"] = cask.url
                        df_pkg.sha256 = cask.sha256
                        #self.df_all.loc[token, "sha256"] = cask.sha256
                        if df_pkg.installed == 0:
                            #df_pkg.version = cask.version
                            self.df_all.loc[token, "version"] = cask.version
                        else:
                            #df_pkg.update = cask.version
                            self.df_all.loc[token, "update"] = cask.version
            self.to_sql_db()
                
                        
    def search(self, key):
        #results = []
        if len(key) < 3:
            print("search key must >= 3")
            return []

        df = self.df_all.query(f"token.str.contains('{key}')")
        return df
            

    def print_cask(self, cask):
        print(f"{cask.installed} {cask.name}\r\t\t\t{cask.version}\r\t\t\t\t\t{cask.desp}")
        

    def download(self, c, token, upgrade=False):
        print(f"starting download {token}")
        url = c.url
        dest = tempfile.gettempdir()
        f = os.path.basename(url)
        command = ["aria2c", "-c", url,  "-d", dest, "-o", f]
        print(command)
        popen = subprocess.Popen(command, stdout=sys.stdout)
        out = popen.wait()
        if upgrade and out == 0:
            out == self.remove(token, upgrade)
        if out == 0: #success
            version_new = (c["update"] if upgrade else c["version"])
            self.install(os.path.join(dest, f), token=token, version=version_new)
        else:
            print("download failed")
            return False
        return True

    def install(self, fname, token, version):
        print(f"start install {fname}")
        format = fname[-3:]
        if format not in ["zip", "pkg", "dmg"]:
            format = "dmg"

        getattr(self, f"install_{format}")(fname)
        
        print(f"{token} installed with version {version}")
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
        for cask in self.jsons:
            if cask["token"] == token:
                jsons = cask
                break
        artifacts = jsons["artifacts"]
        for artifact in artifacts:
            apps = artifact.get("app", [])
            for app in apps:
                os.system(f"rm -rf ~/Applications/{app}")
            if not upgrade: # when upgrade, not zap apps
                zaps = artifact.get("zap", [])
                for zap in zaps:
                    trashes = zap.get("trash", [])
                    for trash in trashes:
                        os.system(f"rm -rf {trash}")
        if not upgrade: # when upgrade, not update db when remove
            self.df_all.loc[token, "installed"] = 0
            self.df_all.loc[token, "update"] = None
            self.to_sql_db()
                
            
        
    #def install_dmg(self, fname):
    #    from dmginstall import installDmg
    #    installDmg(fname)

    def install_pkg(self, fname):
        os.system(f"sudo installer -pkg {fname} -target /")

    def install_zip(self, fname):
        temp_dir = tempfile.mkdtemp()
        os.system(f"unzip '{fname}' -d '{temp_dir}'")
        self.install_archive(temp_dir)

    def list_pkgs(self):
        df = self.df_all.query("installed==1")
        for idx in df.index:
            pkg = df.loc[idx,]
            self.print_cask(pkg)

    def get_output(self, cmd):
        return subprocess.check_output(cmd, shell=True, universal_newlines=True)

    def copy_app(self, path):
        os.system(f"cp -R '{path}' ~/Applications")

    def install_dmg(self, path):
        cmd = f"hdiutil attach '{path}'|grep /Volumes"
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
                if output != '':
                    if depth == 1 and fmt == 'dmg':
                        self.install_dmg(output)
                        continue
                    else:
                        if fmt == 'app':
                            self.copy_app(output)
                            return
                        elif fmt == 'pkg':
                            os.system(f'sudo installer -pkg "{output}" -target /')
                            return
        print("No usable files found")
        
    def main(self):
        if self.args.search:
            res = self.search(self.args.search)
            if len(res) == 0:
                print(f"Not found {self.args.search}")
            else:
                for idx in res.index:
                    cask = res.loc[idx]
                    #print(cask)
                    self.print_cask(cask)


                    
        elif self.args.install:

            token = self.args.install
            res = self.search(token)

            if len(res) == 0:
                print(f"Package with name ({token}) not found")
                
            elif token in res.index:
                cask = res.loc[token]
                out = self.download(cask, token)
                if out == 0:
                    print(f"Installing. {token} Success!")
            else:
                print("There are multiple casks:")
                for idx in res.index:
                    self.print_cask(res.loc[idx])
 
        elif self.args.update:
            stat = os.stat(self.json_file)
            if time.time() - stat.st_mtime > 600: # 10min
                self.get_refresh()
            update_pkgs = self.df_all.query("update.notnull() and update != version")
            for idx in update_pkgs.index:
                pkg = update_pkgs.loc[idx]
                print(f"{idx}\r\t\t{pkg['name']}\r\t\t\t\t{pkg.version.split(',')[0]}\r\t\t\t\t\t\t--->\t{pkg['update'].split(',')[0]}")
                self.download(pkg, idx, upgrade=True)
                
        elif self.args.list:
            self.list_pkgs()

        elif self.args.remove:
            self.remove(self.args.remove)
            
if __name__ == "__main__":
    import os
    import sys
    parser = argparse.ArgumentParser("search cask to install")
    
    parser.add_argument("-s", "--search", type=str, help="search apps")
    parser.add_argument("-l", "--list", action="store_true", help="list apps")
    parser.add_argument("-i", "--install", type=str, help="install apps")
    parser.add_argument("-r", "--remove", type=str, help="remove apps")
    parser.add_argument("-u", "--update", action="store_true", help="update database")

    args = parser.parse_args()

    cask = PyCask(args)
    cask.main()
    #if len(sys.argv) >= 2:
    #    res = cask.search(sys.argv[1])
    #    #cask.download(res[0])
    #else:
    #    print("you should run with ./pycask.py xxxx")
