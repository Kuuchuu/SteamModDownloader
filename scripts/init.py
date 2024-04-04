from scripts.steamcmd import checkAndDownloadSteamCmd
import os
import json
import re
import scripts.config as conf
import scripts.steam as steam
from tkinter import Tk
from tkinter.filedialog import askdirectory
from sys import exit
import requests

# Defaults to original repo if not provided to `start()` function. Shouldn't need changed, change values in smd.py instead.
Original_Repo_Owner="NBZion"
Original_Repo_Name="SteamModDownloader"

def checkVersion(Repo_Owner, Repo_Name):
    currentVersion = open('version.txt','r').readline()
    listedVersion = requests.get(f"https://raw.githubusercontent.com/{Repo_Owner}/{Repo_Name}/master/version.txt").text

    if currentVersion != listedVersion:
        print("[WARNING] Please update SMD with smd update!")
        print(f"Client Version: {currentVersion}")
        print(f"Listed Version: {listedVersion}")
        print("--------------------------------------------------")

def check_empty_list(config):
    for key, value in config.items():
        if isinstance(value, list) and not value:
            print(f"Configuration for '{key}' is an empty list.")
            conf.configureSetting(key, "")
            return True
    return False

def verifyConf(Repo_Owner, Repo_Name, failCount={'emptyList':0, 'downloadDir':0, 'anonymousMode':0, 'steamAccountName':0, 'steamPassword':0, 'gameID':0}):
    # class confErr(Exception, prompt):
    #     pass
    class confErr(Exception):
        def __init__(self, message="", prompt=None):
            super().__init__(message)
            self.prompt = prompt
    try:
        if check_empty_list(conf.fetchConfiguration()):
            failCount['emptyList'] += 1
            raise confErr('conf.json data malformed!\nValue cleared')
        if conf.fetchConfiguration('downloadDir') != "" and not os.path.exists(conf.fetchConfiguration('downloadDir')):
            failCount['downloadDir'] += 1
            raise confErr('downloadDir does not exist or is invalid!', prompt=2)
        if conf.fetchConfiguration('anonymousMode') != "" and conf.fetchConfiguration('anonymousMode').lower() not in ("true", "false"):
            failCount['anonymousMode'] += 1
            raise confErr('Invalid anonymous mode value!', prompt=3)
        pattern = r'^[a-zA-Z0-9_]{2,32}$'
        if conf.fetchConfiguration('steamAccountName') != "" and not re.match(pattern, conf.fetchConfiguration('steamAccountName')):
            failCount['steamAccountName'] += 1
            raise confErr('Invalid steam account name!', prompt=4)
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,}$'
        if conf.fetchConfiguration('steamPassword') != "" and not re.search(pattern, conf.fetchConfiguration('steamPassword')):
            failCount['steamPassword'] += 1
            raise confErr('Invalid steam password!', prompt=5)
        if conf.fetchConfiguration('gameID') != "" and not conf.fetchConfiguration('gameID').isdigit():
            failCount['gameID'] += 1
            raise confErr('Invalid gameID!', prompt=1)
    except confErr as e:
        if any(value > 3 for value in failCount.values()):
            print(f'(ERROR) {e}\nToo many failures!\nPlease run `smd reinstall`, or manually fix conf.json.')
            exit()
        print(f'(ERROR) {e}')
        if e.prompt is not None:
            configure(Repo_Owner, Repo_Name, e.prompt)
        print('Continuing configuration check...')
        verifyConf(Repo_Owner, Repo_Name, failCount)

def checkConfig(Repo_Owner, Repo_Name):
    # Make configuration file if missing
    if not os.path.exists('./conf.json'):
        with open('conf.json', 'w') as f:
            f.write('{"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","gameID":""}')

    verifyConf(Repo_Owner, Repo_Name)

    # Reconfigure download directory setting if invalid
    if not os.path.exists(conf.fetchConfiguration('downloadDir')):
        Tk().withdraw()
        print('Non-existent mod download directory, please enter a new one => ')
        prompt = askdirectory()
        conf.configureSetting('downloadDir', prompt)

    # Reconfigure gameID if empty
    if conf.fetchConfiguration('gameID') == "":
        prompt = input('gameID setting empty, please enter a new one => ')
        conf.configureSetting('gameID', prompt)

    # Reconfigure anonymous mode if empty
    if conf.fetchConfiguration('anonymousMode') == "":
        print("(DISCLAIMER) Information isn't gathered, and is only stored locally.")
        anonymous = input("Use anonymous mode? [Y\\N]\n> ").lower()
        if anonymous == "y":
            conf.configureSetting('anonymousMode', "true")
        elif anonymous == "n":
            conf.configureSetting('anonymousMode', "false")
        else:
            print('(ERROR) Invalid input passed, exiting.')
            exit()

    # Check if anonymous mode is off and ask for credentials
    if conf.fetchConfiguration("anonymousMode") == "false" and conf.fetchConfiguration("steamAccountName") == "":
        username, password = conf.getCredentials()
        conf.configureSetting('steamAccountName', username)
        conf.configureSetting('steamPassword', password)

def downloadMods():
    while True:
        workshopURL = input("Mod/Collection Workshop URL: ")
        workshopURLType = steam.checkType(workshopURL)
        if workshopURLType == "mod":
            print('(PROCESS) Downloading mod...')
            steam.downloadMod(workshopURL)
            break
        elif workshopURLType == "collection":
            print('(PROCESS) Downloading collection...')
            steam.downloadCollection(workshopURL)
            break
        else:
            print('(ERROR) Invalid URL, awaiting new.')
    #print('--------------------------------------------------')

def listMods():
    print("--------------------------------------------------")
    print("MODS IN '"+conf.fetchConfiguration("downloadDir")+"'...\n")
    for dir in os.listdir(conf.fetchConfiguration('downloadDir')):
        smbDir=os.path.join(conf.fetchConfiguration('downloadDir'),os.path.join(dir, 'smbinfo.json'))
        if os.path.exists(smbDir):
            jsonData=json.load(open(smbDir, 'r'))
            print(jsonData['name'])
    print("--------------------------------------------------")

def configure(Repo_Owner, Repo_Name, prompt=None):
    if prompt is None:
        print("(DISCLAIMER) Information isn't gathered, and is only stored locally.")
        print(
            'Setting List:\n'
            '[1] Game ID \n'
            '[2] Download Directory\n'
            '[3] Anonymous Mode\n'
            '[4] Steam Username\n'
            '[5] Steam Password'
        )
        prompt = input('> ')
    #print('--------------------------------------------------')
    print('What value do you want to change it to?')
    if prompt == '2':
        Tk().withdraw()
        value = askdirectory()
    else:
        value = input('> ')
    match prompt:
        case '1':
            setting='gameID'
        case '2':
            setting='downloadDir'
        case '3':
            setting='anonymousMode'
        case '4':
            setting='steamAccountName'
        case '5':
            setting='steamPassword'
        case _:
            print('(ERROR) Invalid setting id, exiting.')
            exit()
    conf.configureSetting(setting, value)
    start(Repo_Owner, Repo_Name)

def start(Repo_Owner=Original_Repo_Owner, Repo_Name=Original_Repo_Name, options=None):
    if options is None:
        options = {}
    # print(f'Repo Owner: {Repo_Owner}')
    # print(f'Repo Name: {Repo_Name}')
    # print(f'Options: {options}')
    prompt=None
    checkVersion(Repo_Owner, Repo_Name)

    if options.get('config'):
        config_data = options['config']
        try:
            json.loads(config_data)
        except json.JSONDecodeError:
            print(f'Config data {config_data} invalid!')
            exit()
        for key, value in config_data.items():
            conf.configureSetting(key, value)
            print(f"Configured {key} with value {value} from --config")

    if options.get('configFile'):
        config_file_path = options['configFile']
        if not os.path.exists(config_file_path):
            print(f'Config file {config_file_path} does not exist!')
            exit()
        with open(config_file_path, 'r') as file:
            config_data = json.load(file)
        for key, value in config_data.items():
            conf.configureSetting(key, value)
            print(f"Configured {key} with value {value} from --configFile")

    if options.get('game'):
        game_value = options['game']
        conf.configureSetting('gameID', game_value)
        print(f"Configured gameID with value {game_value}")

    if options.get('mod'):
        print(f"Mod value: {options['mod']}")
        prompt = '1'

    if options.get('pack'):
        print(f"Pack value: {options['pack']}")
        prompt = '1'

    if options.get('outputDir'):
        outputDir_value = options['outputDir']
        conf.configureSetting('outputDir', outputDir_value)
        print(f"Configured outputDir with value {outputDir_value}")
        
    if options.get('list'):
        print("list called...")
        prompt = '2'

    checkConfig(Repo_Owner, Repo_Name)
    checkAndDownloadSteamCmd()
    while True:
        print('Welcome to SWD!')
        print('[1] => Download Mods\n[2] => List Mods\n[3] => Open Settings\n[4] => Exit')
        if prompt is None:
            prompt = input('> ')
        if prompt == '1':
            downloadMods()
            break
        elif prompt == '2':
            listMods()
        elif prompt == '3':
            configure(Repo_Owner, Repo_Name)
            break
        elif prompt == '4':
            exit()
        else:
            print('(ERROR) Invalid option passed, exiting.')
            exit()
#start()
