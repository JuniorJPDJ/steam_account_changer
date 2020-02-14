#!/usr/bin/env python3
import os
import vdf
from pathlib import Path
import subprocess
import time

from steam import SteamID

STEAMDIR = Path.home() / ".local/share/Steam"
STEAMUSERDATA = STEAMDIR / "userdata"
STEAMREGISTRY = Path.home() / ".steam/registry.vdf"

# TODO: function to link app config
# TODO: SteamApp class
# TODO: steam runapp protocol handling and auto-account changing (choose account with wanted app, if more - most recenty played, if none just run first/main/currently logged in)
# TODO: function to run steam in offline mode

class SteamAccount(SteamID):
    @property
    def path(self) -> Path:
        return STEAMUSERDATA/str(self.id)

    def get_login(self):
        '''Returns account login name'''
        with open(STEAMDIR/"config/config.vdf", 'r') as f:
            cfg = vdf.load(f)
        
        accs = cfg['InstallConfigStore']['Software']['Valve']['Steam']['Accounts']
        for a in accs:
            if accs[a]['SteamID'] == str(self.as_64):
                return a

    def _get_app_localconfig(self, appid: int):
        with open(self.path/"config/localconfig.vdf", 'r') as f:
            cfg = vdf.load(f)
        
        apps = cfg['UserLocalConfigStore']['Software']['Valve']['Steam']['Apps']
        appid = str(appid)
        if appid in apps:
            return apps[appid]
        return {}

    def get_name(self):
        '''Returns account persona name/nickname/profile name'''
        with open(self.path/"config/localconfig.vdf", 'r') as f:
            cfg = vdf.load(f)
        
        return cfg['UserLocalConfigStore']['friends']['PersonaName']

    def get_app_config_owner(self, appid: int) -> 'SteamAccount':
        '''Returns SteamAccount, which app userdata is symlinked to'''
        cfgpath = self.path/str(appid)
        if not cfgpath.exists():
            return None
        if cfgpath.is_symlink():
            return self.__class__((cfgpath/"..").resolve().name)
        return self

    def get_app_launchopts(self, appid: int) -> str:
        '''Returns app launch options (commandline parameters)'''
        cfg = self._get_app_localconfig(appid)
        if 'LaunchOptions' in cfg:
            return cfg['LaunchOptions']
        return ""

    def set_app_launchopts(self, appid: int, params: str):
        '''Sets app launch options (commandline parameters)'''
        with open(self.path/"config/localconfig.vdf", 'r') as f:
            cfg = vdf.load(f, mapper=vdf.VDFDict)
        
        meh = cfg['UserLocalConfigStore']['Software']['Valve']['Steam']['Apps'][str(appid)]
        if 'LaunchOptions' in meh:
            del meh['LaunchOptions']
        meh['LaunchOptions'] = params
    
        with open(self.path/"config/localconfig.vdf", 'w') as f:
            cfg = vdf.dump(cfg, f, pretty=True)

    def get_app_playtime(self, appid: int) -> int:
        '''Returns whole app playtime in minutes'''
        cfg = self._get_app_localconfig(appid)
        if 'Playtime' in cfg:
            return int(cfg['Playtime'])
        elif 'playTime' in cfg:
            return int(cfg['playTime'])
        return 0

    def get_2week_app_playtime(self, appid: int) -> int:
        '''Returns 2 week app playtime in minutes'''
        ret 
        cfg = self._get_app_localconfig(appid)
        if 'Playtime2wks' in cfg:
            return int(cfg['Playtime2wks'])
        return 0

class Steam(object):
    @staticmethod
    def get_accounts() -> (SteamAccount,):
        for accdir in os.scandir(STEAMUSERDATA):
            if not accdir.is_dir():
                continue
            
            acc = accdir.name
            yield SteamAccount(acc)

    @staticmethod
    def account_by_login(login: str):
        '''Gets SteamAccount by login name (need to be logged in Steam instance at least once)'''
        with open(STEAMDIR/"config/config.vdf", 'r') as f:
            cfg = vdf.load(f)
        
        accs = cfg['InstallConfigStore']['Software']['Valve']['Steam']['Accounts']
        if login in accs and 'SteamID' in accs[login]:
            return SteamAccount(accs[login]['SteamID'])

    @classmethod
    def logged_user(cls) -> SteamAccount:
        # TODO: Windows
        with open(STEAMREGISTRY, 'r') as f:
            registry = vdf.load(f)

        return cls.account_by_login(registry["Registry"]["HKCU"]["Software"]["Valve"]["Steam"]["AutoLoginUser"])

    @staticmethod
    def change_user(acc: SteamAccount):
        # TODO: Windows need registry edit, no VDF
        with open(STEAMREGISTRY, 'r') as f:
            registry = vdf.load(f, mapper=vdf.VDFDict)

        steam = registry["Registry"]["HKCU"]["Software"]["Valve"]["Steam"]
        steam[(0, "AutoLoginUser")] = acc.get_login()
        steam[(0, "RememberPassword")] = "1"

        with open(STEAMREGISTRY, 'w') as f:
            vdf.dump(registry, f, pretty=True)

    @staticmethod
    def start(*args):
        # TODO: Check if works on Windows
        with open(os.devnull, 'w') as null:
            subprocess.Popen(('steam',) + args, stdout=null, stderr=null)

    @staticmethod
    def is_running() -> bool:
        # TODO: Windows implementation
        with open(os.devnull, 'w') as null:
            return not subprocess.run(("killall", "-0", "steam"), stderr=null, stdout=null).returncode

    @classmethod
    def shutdown(cls):
        if cls.is_running():
            with open(os.devnull, 'w') as null:
                subprocess.run(("steam", "-shutdown"), stderr=null, stdout=null)
                while cls.is_running():
                    time.sleep(0.2)

    @classmethod
    def start_app(cls, appid: int):
        cls.start(f'steam://rungameid/{appid}')
    
def main():
    from datetime import datetime
    import argparse
    import json
    from csgo.features import player
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='login', type=str, required=False, default='', help="relog steam to account with that login")
    args = parser.parse_args()
    
    if args.login:
        acc = Steam.account_by_login(args.login)
        if acc is not None:
            Steam.shutdown()
            Steam.change_user(acc)
            Steam.start()
        else:
            print('Account not found')

        return

    accs = {}
    if Path('acc.json').exists():
        with open('acc.json', 'r') as f:
            accs = json.load(f)
    
    for a in Steam.get_accounts():
        print(f"  SteamID3: {a.as_steam3}")
        print(f"  | Login: {a.get_login()}".ljust(50), end='')
        print(f"  | Name: {a.get_name()}")

        # TODO: wallet
        
        csacc = a.get_app_config_owner(730)
        if csacc is not None:
            print(f"  | CS:GO:",)
            print(f"    | Profile: {'Independent' if csacc == a else f'Linked to {csacc.get_login()}'}".ljust(50), end='')

            o = a.get_app_launchopts(730)
            if o:
                print(f'  | Launch options: "{o}"')
            else:
                print()
        
        
        if a.get_login() in accs:
            stats = accs[a.get_login()]
            if csacc is not None:
                if 'csgo_profile' in stats:
                    csprof = stats['csgo_profile']
                    if 'csgo_penalty_end' in stats:
                        date = datetime.fromtimestamp(stats['csgo_penalty_end'])
                        if date > datetime.now():
                            print(f"    | Cooldown end: {date:%Y-%m-%d %H:%M}".ljust(50), end='')
                            print(f"  | Cooldown reason: {stats['csgo_penalty_reason']}")
                    if 'ranking' in csprof:
                        print(f"    | Rank: {player.Player.ranks_map[csprof['ranking']['rankId']]}".ljust(50), end='')
                        print(f"  | Wins: {csprof['ranking']['wins']}")
                    print(f"    | Level: {csprof['playerLevel']}".ljust(50), end='')
                    if 'csgo_last_mm' in stats:
                        date = datetime.fromtimestamp(stats['csgo_last_mm'])
                        print(f"  | Last MM: {date:%Y-%m-%d %H:%M}")
                    else:
                        print()

            if 'bans' in stats:
                print(f"  | VAC bans: {stats['bans']}".ljust(50), end='')

#            if 'wallet_balance' in stats:
#                print(f"  | Wallet: {stats['wallet_balance']
        
        print()
        

if __name__=="__main__":
    main()

