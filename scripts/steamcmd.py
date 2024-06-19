import scripts.config as conf
#from scripts.init import rPrint
from rich.console import Console; console = Console()
import os
from re import sub
import wget
import subprocess
import shutil
import json
import time

steamCmdUrl="https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
steamCmdPath="./scripts/steamcmd/"
workDirectory = f'{os.getcwd()}/scripts/steamcmd/workshop'
conDir = f'{workDirectory}/steamapps/workshop/content/'
tarFile=None
encryptionKey=None

def anonCheck():
    global encryptionKey
    if conf.fetchConfiguration("anonymousMode").lower() != "false":
        return "anonymous"
    steamPassword = conf.fetchConfiguration("steamPassword")
    if str(conf.fetchConfiguration("encrypted")).lower() != "false":
        if encryptionKey is None:
            if encryptionKey := conf.fetchConfiguration("encryptionKey") or conf.keySelection():
                key = conf.read_key(encryptionKey)
                steamPassword = conf.decrypt_pass(steamPassword, key)
            else:
                print("No encryption key selected.\nAttempting anonymous login...")
                return "anonymous"
        else:
            key = conf.read_key(encryptionKey)
            steamPassword = conf.decrypt_pass(steamPassword, key)
    return f'{conf.fetchConfiguration("steamAccountName")}  {steamPassword}'

def checkAndDownloadSteamCmd():
    if not os.path.exists(steamCmdPath):
        os.mkdir(steamCmdPath)
    if len(os.listdir(steamCmdPath)) != 0:
        return
    print("SteamCMD not present, Downloading...")
    wget.download(steamCmdUrl,steamCmdPath)
    subprocess.call(
        [
            'tar',
            '-xvf',
            f'{steamCmdPath}steamcmd_linux.tar.gz',
            '-C',
            steamCmdPath,
        ]
    )
    os.remove(f'{steamCmdPath}steamcmd_linux.tar.gz')
    os.mkdir('./scripts/steamcmd/workshop')

def downloadModListSCMD(gameid, mods, insDir):
    #print('--------------------------------------------------')
    #print('Downloading Mods...')
    # print(f'DEBUG: {mods}')
    with open('download_script.txt', 'w') as scriptFile:
        scriptFile.write(f'force_install_dir {workDirectory}\n')
        scriptFile.write(f'login {anonCheck()}\n')
        for mod in mods[0]:
            modId = mod['id']
            scriptFile.write(f'workshop_download_item {gameid} {modId}\n')
        scriptFile.write('quit')
    dlScriptPath = os.path.abspath('download_script.txt')
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Running SteamCMD against Mod List...')
    startTime = time.time()
    with console.status('[bold cyan]Running SteamCMD against Mod List...[/bold cyan]'): #spinner
        subprocess.run([f'{steamCmdPath}steamcmd.sh', f'+runscript {dlScriptPath}'])
    print(f'Downloads finished in {time.time()-startTime} seconds.')
    os.remove(dlScriptPath)
    print('\n--------------------------------------------------')
    print('Moving and Renaming Mods...')
    for mod in mods[0]:
        modFol = f'{conDir}/{gameid}/{mod["id"]}/'
        outPathName = f'{insDir}/{mod["name"]}'
        if os.path.exists(outPathName): print(f'Updating {mod["name"]} (Existing Mod)')
        # Prepare info.json for mod
        with open(os.path.join(modFol,'smbinfo.json'), 'w') as jsonFile:
            infoData= {
                "name": mod["name"],
                "gameID": gameid
            }
            json.dump(infoData,jsonFile,indent=4)
        shutil.copytree(modFol,outPathName,dirs_exist_ok=True)
        shutil.rmtree(modFol)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Mod Download(s) Complete!')