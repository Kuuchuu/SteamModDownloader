import json
import os
import scripts.config as conf
import shutil
import subprocess
import time
import wget
from re import sub
from rich.console import Console; console = Console()
#from scripts.init import rprint

steam_cmd_url="https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
steam_cmd_path="./scripts/steamcmd/"
work_directory = f'{os.getcwd()}/scripts/steamcmd/workshop'
con_dir = f'{work_directory}/steamapps/workshop/content/'
tar_file=None
encryption_key=None

def anon_check():
    global encryption_key
    if conf.fetch_configuration("anonymousMode").lower() != "false":
        return "anonymous"
    steam_password = conf.fetch_configuration("steamPassword")
    if str(conf.fetch_configuration("encrypted")).lower() != "false":
        if encryption_key is None:
            if encryption_key := conf.fetch_configuration("encryptionKey") or conf.key_selection():
                key = conf.read_key(encryption_key)
                steam_password = conf.decrypt_pass(steam_password, key)
            else:
                print("No encryption key selected.\nAttempting anonymous login...")
                return "anonymous"
        else:
            key = conf.read_key(encryption_key)
            steam_password = conf.decrypt_pass(steam_password, key)
    return f'{conf.fetch_configuration("steamAccountName")}  {steam_password}'

def check_and_download_steamcmd():
    if not os.path.exists(steam_cmd_path):
        os.mkdir(steam_cmd_path)
    if len(os.listdir(steam_cmd_path)) != 0:
        return
    print("SteamCMD not present, Downloading...")
    wget.download(steam_cmd_url,steam_cmd_path)
    subprocess.call(
        [
            'tar',
            '-xvf',
            f'{steam_cmd_path}steamcmd_linux.tar.gz',
            '-C',
            steam_cmd_path,
        ]
    )
    os.remove(f'{steam_cmd_path}steamcmd_linux.tar.gz')
    os.mkdir('./scripts/steamcmd/workshop')

def download_mod_list_scmd(game_id, mods, insDir):
    #print('--------------------------------------------------')
    #print('Downloading Mods...')
    # print(f'DEBUG: {mods}')
    with open('download_script.txt', 'w') as script_file:
        script_file.write(f'force_install_dir {work_directory}\n')
        script_file.write(f'login {anon_check()}\n')
        for mod in mods[0]:
            mod_id = mod['id']
            script_file.write(f'workshop_download_item {game_id} {mod_id}\n')
        script_file.write('quit')
    dl_script_path = os.path.abspath('download_script.txt')
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Running SteamCMD against Mod List...')
    start_time = time.time()
    with console.status('[bold cyan]Running SteamCMD against Mod List...[/bold cyan]'): #spinner
        subprocess.run([f'{steam_cmd_path}steamcmd.sh', f'+runscript {dl_script_path}'])
    print(f'Downloads finished in {time.time()-start_time} seconds.')
    os.remove(dl_script_path)
    print('\n--------------------------------------------------')
    print('Moving and Renaming Mods...')
    for mod in mods[0]:
        mod_fol = f'{con_dir}/{game_id}/{mod["id"]}/'
        out_path_name = f'{insDir}/{mod["name"]}'
        if os.path.exists(out_path_name): print(f'Updating {mod["name"]} (Existing Mod)')
        # Prepare info.json for mod
        with open(os.path.join(mod_fol,'smbinfo.json'), 'w') as json_file:
            info_data= {
                "name": mod["name"],
                "gameID": game_id
            }
            json.dump(info_data,json_file,indent=4)
        shutil.copytree(mod_fol,out_path_name,dirs_exist_ok=True)
        shutil.rmtree(mod_fol)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Mod Download(s) Complete!')