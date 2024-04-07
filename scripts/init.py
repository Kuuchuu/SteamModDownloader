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
Original_Repo_Owner,Repo_Owner="NBZion",""
Original_Repo_Name,Repo_Name="SteamModDownloader",""

def checkVersion():
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

def verifyConf(failCount={'emptyList':0, 'downloadDir':0, 'anonymousMode':0, 'steamAccountName':0, 'steamPassword':0, 'encrypted':0 'gameID':0}):
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
        if conf.fetchConfiguration('encrypted') != "" and conf.fetchConfiguration('encrypted').lower() not in ("true", "false"):
            failCount['encrypted'] += 1
            raise confErr('Invalid encrypted mode value!', prompt=5)
        if conf.fetchConfiguration('gameID') != "" and not conf.fetchConfiguration('gameID').isdigit():
            failCount['gameID'] += 1
            raise confErr('Invalid gameID!', prompt=1)
    except confErr as e:
        if any(value > 3 for value in failCount.values()):
            print(f'(ERROR) {e}\nToo many failures!\nPlease run `smd reinstall`, or manually fix conf.json.')
            exit()
        print(f'(ERROR) {e}')
        if e.prompt is not None:
            configure(e.prompt)
        print('Continuing configuration check...')
        verifyConf(failCount)

def checkConfig():
    # Make configuration file if missing
    if not os.path.exists('./conf.json'):
        with open('conf.json', 'w') as f:
            f.write('{"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","encrypted":"","gameID":""}')

    verifyConf()

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
        print("(DISCLAIMER) Information isn't gathered, and is only stored locally.\nPassword can be encrypted.")
        if anonymous := getYN("Use anonymous mode?", True):
            conf.configureSetting('anonymousMode', "true")
        else:
            conf.configureSetting('anonymousMode', "false")

    # Check if anonymous mode is off and ask for credentials
    if conf.fetchConfiguration("anonymousMode") == "false" and conf.fetchConfiguration("steamAccountName") == "":
        username, password, encrypted = conf.getCredentials()
        conf.configureSetting('steamAccountName', username)
        conf.configureSetting('steamPassword', password)
        conf.configureSetting('encrypted', encrypted)

def downloadMods(mods=None):
    modURLs = []
    ColURLs = []
    if mods is None:
        mods = []
        mods.extend(input("Comma Separated Mod/Collection Workshop URL/IDs: ").split(","))
    for i, item in enumerate(mods):
        urlAttempts = 0
        while True:
            if urlAttempts > 3:
                print('(ERROR) Too many failures!')
                return 1
            if mods[i] == "":
                break
            if not mods[i].startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
            URLCheck = steam.checkType(mods[i])
            if URLCheck == "mod":
                modURLs.append(mods[i])
                break
            elif URLCheck == "collection":
                ColURLs.append(mods[i])
                break
            else:
                print(f'(ERROR) Invalid URL "{URLCheck}", awaiting new.\nLeave empty to skip.')
                urlAttempts += 1
                mods[i] = input("Mod/Collection Workshop URL/IDs: ").split(",")
    modList = [{"mods": modURLs, "collections": ColURLs}]
    print('(PROCESS) Processing Mod(s)...')
    steam.downloadModList(modList)

def listMods():
    print("--------------------------------------------------")
    print("MODS IN '"+conf.fetchConfiguration("downloadDir")+"'...\n")
    for dir in os.listdir(conf.fetchConfiguration('downloadDir')):
        smbDir=os.path.join(conf.fetchConfiguration('downloadDir'),os.path.join(dir, 'smbinfo.json'))
        if os.path.exists(smbDir):
            jsonData=json.load(open(smbDir, 'r'))
            print(jsonData['name'])
    print("--------------------------------------------------")

def configure(prompt=None):
    nonInteractive=False
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
    else:
        nonInteractive=True
    #print('--------------------------------------------------')
    if prompt not in [4, 5]:
        print('What value do you want to change it to?')
    if prompt == '2':
        Tk().withdraw()
        value = askdirectory()
    elif prompt 4
        value = conf.getCredentials(True)
    elif prompt 5
        value, encrypted = conf.getCredentials(False)
        conf.configureSetting('encrypted', encrypted)
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
    print(f'Configured {setting}.')
    if not nonInteractive:
        start(Repo_Owner, Repo_Name)
    else:
        return True

_DEBUG = False
_SILENT = False
_CONFIG = None
def start(_Repo_Owner=Original_Repo_Owner, _Repo_Name=Original_Repo_Name, options=None):
    Repo_Owner = _Repo_Owner
    Repo_Name = _Repo_Name
    if options is None:
        options = {}
    mods = []
    prompt=None
    nonInteractive=False
    
    if options.get('verbose'):
        _DEBUG = True
        print('(WARN) Verbose mode enabled but currently not implemented!')
    elif options.get('silent'):
        _SILENT = True
        print('(WARN) Silent mode enabled but currently not implemented!')
    
    checkVersion(Repo_Owner, Repo_Name)

    if options.get('tempConfig'):
        _CONFIG = {"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","encrypted":"","gameID":""}
        print('(INFO) Temporary config in use!')

    if options.get('config'):
        config_data = options['config']
        #print(f'Config data: {config_data}')
        try:
            for key, value in config_data.items():
                conf.configureSetting(key, value)
                if key == 'steamPassword':
                    value = '********'
                print(f"Configured {key} with value {value} from --config")
        except KeyError:
            print(f'Config data {config_data} invalid!')
            exit()

    if options.get('configFile'):
        config_file_path = options['configFile']
        if not os.path.exists(config_file_path):
            print(f'Config file {config_file_path} does not exist!')
            exit()
        with open(config_file_path, 'r') as file:
            try:
                config_data = json.load(file)
            except json.decoder.JSONDecodeError:
                print(f'Config file {config_file_path} is not valid JSON!')
                exit()
        for key, value in config_data.items():
            conf.configureSetting(key, value)
            if key == 'steamPassword':
                value = '********'
            print(f"Configured {key} with value {value} from --configFile")

    if options.get('outputDir'):
        outputDir_value = options['outputDir']
        conf.configureSetting('downloadDir', outputDir_value)
        print(f"Configured downloadDir with value {outputDir_value}")

    if options.get('anonymousMode'):
        anonymous_value = options['anonymousMode']
        conf.configureSetting('anonymousMode', anonymous_value)
        print(f"Configured anonymousMode with value {anonymous_value}")

    if options.get('steamAccountName'):
        steamAccountName_value = options['steamAccountName']
        conf.configureSetting('steamAccountName', steamAccountName_value)
        print(f"Configured steamAccountName with value {steamAccountName_value}")

    if options.get('steamPassword'):
        steamPassword_value = options['steamPassword']
        conf.configureSetting('steamPassword', steamPassword_value)
        print(f"Configured steamPassword with value {steamPassword_value}")

    if options.get('encrypted'):
        encrypted_value = options['encrypted']
        conf.configureSetting('encrypted', encrypted_value)
        print(f"Configured encrypted with value {encrypted_value}")

    if options.get('encryptionKey'):
        encryptionKey_value = options['encryptionKey']
        conf.configureSetting('encryptionKey', encryptionKey_value)
        print(f"Configured encryptionKey with value {encryptionKey_value}")

    if options.get('game'):
        game_value = options['game']
        conf.configureSetting('gameID', game_value)
        print(f"Configured gameID with value {game_value}")

    if options.get('mod'):
        print(f"Mod value: {options['mod']}")
        mods.extend(options['mod'].split(","))
        for i, item in enumerate(mods):
            if not item.startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
        if not options.get('collection'):
            print(f'Requested Mods:\n{mods}')
        prompt = '1'

    if options.get('collection'):
        print(f"Collection value: {options['collection']}")
        mods.extend(options['collection'].split(","))
        for i, item in enumerate(mods):
            if not item.startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
        print(f'Requested Mods:\n{mods}')
        prompt = '1'

    if options.get('list'):
        prompt = '2'

    if options.get('encryptPassword'):
        #prompt = '2'

    checkConfig(Repo_Owner, Repo_Name)
    checkAndDownloadSteamCmd()
    while True:
        if prompt is None:
            print('Welcome to SWD!')
            print('[1] => Download Mods\n[2] => List Mods\n[3] => Open Settings\n[4] => Exit')
            prompt = input('> ')
        else:
            nonInteractive = True
        if prompt == '1':
            downloadMods(mods)
            break
            # if nonInteractive:
            #     exit()
        elif prompt == '2':
            listMods()
            if nonInteractive:
                exit()
        elif prompt == '3':
            configure(Repo_Owner, Repo_Name)
            break
        elif prompt == '4':
            exit()
        else:
            print('(ERROR) Invalid option passed, exiting.')
            exit()
