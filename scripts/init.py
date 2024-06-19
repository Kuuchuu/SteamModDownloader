from rich.console import Console; console = Console()
from rich.panel import Panel
from rich.table import Table
from rich import box
from scripts.steamcmd import checkAndDownloadSteamCmd
from getpass import getpass
import datetime
import os, sys
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

def rPrint(message=None, type=None, customStyle=None, tableData=None):
    if customStyle is None:
        customStyle = ""
    match str(type).lower():
        case 'rule':
            console.rule(message, style=customStyle)
            return
        case 'panel':
            pTitle = ""
            pMessage = ""
            if message is not None:
                pTitle = message.get('title')
                pMessage = message.get('message')
            console.print(Panel(pMessage, title=pTitle), style=customStyle)
            return
        case 'table':
            if tableData is not None:
                console.print(tableData, style=customStyle)
            else:
                console.print(message, style=customStyle)
            return
        case 'log':
            global _VERBOSE
            if _VERBOSE:
                console.log(f"{str(datetime.datetime.now())} | {message}", style=customStyle)
            return
        case 'error':
            message = f'❌  {str(message)}'
            customStyle = f'bold red {customStyle} '
        case 'warn':
            message = f'⚠️  {str(message)}'
            customStyle = f'bold yellow {customStyle}'
        case 'info':
            message = f'ℹ️  {str(message)}'
            customStyle = f'bold cyan {customStyle}'
        case 'pop':
            message = str(message)
            customStyle = f'bold magenta {customStyle}'
        case 'success':
            message = f'✅  {str(message)}'
            customStyle = f'bold green {customStyle}'
        case 'getpass':
            message = f'❔  {str(message)} » '
            customStyle = f'bold cyan {customStyle}'
            console.print(f'{message}', style=customStyle, end=""); sys.stdout.flush()
            return getpass(prompt='')
        case 'prompt':
            message = f'❔  {str(message)} » '
            if "skip-input" in customStyle:
                customStyle = customStyle.replace("skip-input", "")
                type = "skip-prompt"
            customStyle = f'bold cyan {customStyle}'
            console.print(f'{message}', style=customStyle, end=""); sys.stdout.flush()
            if type == "skip-prompt":
                return
            return input()
        # case _:
    console.print(message, style=customStyle)
    return

def checkVersion():
    currentVersion = open('version.txt','r').readline()
    listedVersion = requests.get(f"https://raw.githubusercontent.com/{Repo_Owner}/{Repo_Name}/master/version.txt").text

    if currentVersion != listedVersion:
        clURL = f"https://api.github.com/repos/{Repo_Owner}/{Repo_Name}/releases/latest"
        clResponse = requests.get(clURL)
        clData = clResponse.json()
        changelog = clData.get("body", "No description available.")
        rPrint("Please update SMD with smd update!", "warn")
        #rPrint("Please update SMD with smd update!", None, "bold yellow")
        rPrint(f"Current Version: {currentVersion}")
        rPrint(f"New Version: {listedVersion}", "pop")
        rPrint({"title":"Changelog","message":changelog}, "panel")

def check_empty_list(config):
    for key, value in config.items():
        if isinstance(value, list) and not value:
            rPrint(f"Configuration for '{key}' is an empty list.", "warn")
            conf.configureSetting(key, "")
            return True
    return False

def verifyConf(failCount={'emptyList':0, 'downloadDir':0, 'anonymousMode':0, 'steamAccountName':0, 'steamPassword':0, 'encrypted':0, 'gameID':0}):
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
            rPrint(f'{e}\nToo many failures!\nPlease run `smd reinstall`, or manually fix conf.json.', "error")
            exit()
        rPrint(f'{e}', "error")
        if e.prompt is not None:
            configure(e.prompt)
        rPrint('Continuing configuration check...')
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
        rPrint('Non-existent mod download directory, please enter a new one', "prompt", "skip-input")
        prompt = askdirectory(); print('')
        conf.configureSetting('downloadDir', prompt)

    # Reconfigure gameID if empty
    if conf.fetchConfiguration('gameID') == "":
        prompt = rPrint('gameID setting empty, please enter a new one', "prompt")
        conf.configureSetting('gameID', prompt)

    # Reconfigure anonymous mode if empty
    if conf.fetchConfiguration('anonymousMode') == "":
        rPrint("[DISCLAIMER] Information isn't gathered, and is only stored locally.\nPassword can be encrypted.", None, "yellow bold italic")
        if anonymous := conf.getYN("Use anonymous mode?", "n"):
            conf.configureSetting('anonymousMode', "true")
        else:
            conf.configureSetting('anonymousMode', "false")

    # Check if anonymous mode is off and ask for credentials
    if conf.fetchConfiguration("anonymousMode") == "false" and conf.fetchConfiguration("steamAccountName") == "":
        username, password = conf.getCredentials()
        conf.configureSetting('steamAccountName', username)
        if isinstance(password, (list, tuple, set, dict)):
            conf.configureSetting('steamPassword', password[0])
            conf.configureSetting('encrypted', password[1])
        else:
            conf.configureSetting('steamPassword', password)

def downloadMods(mods=None):
    modURLs = []
    ColURLs = []
    rPrint(f'downloadMods: {mods}', "log")
    if mods == [] or mods == [''] or mods is None:
        rPrint('mods is None', "log")
        mods = []
        mods.extend(rPrint("Comma Separated Mod/Collection Workshop URL/IDs", "prompt").split(","))
        rPrint(f'downloadMods: {mods}', "log")
        if mods == ['']:
            rPrint('No mods/collections provided.', "error")
            return 1
        #mods.extend(input("Comma Separated Mod/Collection Workshop URL/IDs: ").split(","))
    for i, item in enumerate(mods):
        urlAttempts = 0
        while True:
            if urlAttempts > 3:
                rPrint('Too many failures!', "error")
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
                rPrint(f'Invalid URL "{URLCheck}", awaiting new.\nLeave empty to skip.', "warn")
                urlAttempts += 1
                mods[i] = rPrint("Mod/Collection Workshop URL/IDs", "prompt").split(",")
                #mods[i] = input("Mod/Collection Workshop URL/IDs: ").split(",")
    modList = [{"mods": modURLs, "collections": ColURLs}]
    rPrint('Processing Mod(s)...', "info")
    steam.downloadModList(modList)

def listMods():
    modList = []
    for dir in os.listdir(conf.fetchConfiguration('downloadDir')):
        smbDir=os.path.join(conf.fetchConfiguration('downloadDir'),os.path.join(dir, 'smbinfo.json'))
        if os.path.exists(smbDir):
            jsonData=json.load(open(smbDir, 'r'))
#            modList.append(f"{jsonData['name']} | [dark_khaki]{jsonData['author']}[/dark_khaki] | {jsonData['version']} | [wheat4]{jsonData['description']}[/wheat4]")
            modList.append(f"{jsonData['name']} | [dark_khaki]AUTHOR PLACEHOLDER[/dark_khaki] | VERSION PLACEHOLDER | [wheat4]DESCRIPTION PLACEHOLDER[/wheat4]")
    modListTable = Table(show_header=False, box=None, padding=1)
    for i, mod in enumerate(modList):
        # style = "underline" if (i + 1) % 2 == 0 else "" # Underline every other row. Opting for padding instead.
        modListTable.add_row(f'[bold magenta][{i+1}][/bold magenta]', mod)
    rPrint({"title":"Current Mods","message":modListTable}, "panel", "yellow")

def configure(prompt=None):
    nonInteractive=False
    if prompt is None:
        rPrint("[DISCLAIMER] ALL data stored locally.", None, "yellow bold italic")
        settingsTable = Table(title="Setting List", show_header=False, box=None)
        settingsTable.add_row("[1]", "Game ID")
        settingsTable.add_row("[2]", "Download Directory")
        settingsTable.add_row("[3]", "Anonymous Mode")
        settingsTable.add_row("[4]", "Steam Username")
        settingsTable.add_row("[5]", "Steam Password")
        console.print(settingsTable, style="bold")
        prompt = rPrint('\nWhich setting would you like to change?', "prompt")
    else:
        nonInteractive=True
    #console.rule()
    # if prompt not in [4, 5]:
    #     console.print('What value do you want to change it to?')
    if prompt == '2':
        Tk().withdraw()
        rPrint('What directory would you like to change it to?', "prompt", "skip-input")
        value = askdirectory()
    elif prompt == '4':
        value = conf.getCredentials(True)
    elif prompt == '5':
        value, encrypted = conf.getCredentials(False)
        conf.configureSetting('encrypted', encrypted)
    else:
        value = rPrint('What value would you like to change it to?', "prompt")
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
            rPrint('Invalid setting id, exiting.', 'error')
            exit()
    conf.configureSetting(setting, value)
    rPrint(f'Configured {setting}.', 'info')
    if not nonInteractive:
        start(Repo_Owner, Repo_Name)
    else:
        return True

_VERBOSE = False
_MINIMAL = False
_DEBUG = False
_CONFIG = None
def start(_Repo_Owner=Original_Repo_Owner, _Repo_Name=Original_Repo_Name, options=None):
    global Repo_Owner
    global Repo_Name
    Repo_Owner = _Repo_Owner
    Repo_Name = _Repo_Name
    if options is None:
        options = {}
    mods = []
    prompt=None
    nonInteractive=False
    
    if options.get('verbose'):
        global _VERBOSE
        _VERBOSE = True
    if options.get('minimal'):
        global _MINIMAL
        _MINIMAL = True
        rPrint('Quiet mode enabled but currently not implemented!', 'warn')
    if options.get('debug'):
        global _DEBUG
        _DEBUG = True
        rPrint('Debug mode enabled but currently not implemented!', 'warn')
    if options.get('silent'):
        rPrint('Silent mode enabled but clearly not working!', 'warn')
    
    checkVersion()

    if options.get('tempConfig'):
        _CONFIG = {"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","encrypted":"","gameID":""}
        rPrint('Temporary config in use!', 'info')

    if options.get('config'):
        config_data = options['config']
        #console.print(f'Config data: {config_data}')
        try:
            for key, value in config_data.items():
                conf.configureSetting(key, value)
                if key == 'steamPassword':
                    value = '********'
                rPrint(f"Configured {key} with value {value} from --config", 'info')
        except KeyError:
            rPrint(f'Config data {config_data} invalid!', 'error')
            exit()

    if options.get('configFile'):
        config_file_path = options['configFile']
        if not os.path.exists(config_file_path):
            rPrint(f'Config file {config_file_path} does not exist!', 'error')
            exit()
        with open(config_file_path, 'r') as file:
            try:
                config_data = json.load(file)
            except json.decoder.JSONDecodeError:
                rPrint(f'Config file {config_file_path} is not valid JSON!', 'error')
                exit()
        for key, value in config_data.items():
            conf.configureSetting(key, value)
            if key == 'steamPassword':
                value = '********'
            rPrint(f"Configured {key} with value {value} from --configFile", 'info')

    if options.get('outputDir'):
        outputDir_value = options['outputDir']
        conf.configureSetting('downloadDir', outputDir_value)
        rPrint(f"Configured downloadDir with value {outputDir_value}", 'info')

    if options.get('anonymousMode'):
        anonymous_value = options['anonymousMode']
        conf.configureSetting('anonymousMode', anonymous_value)
        rPrint(f"Configured anonymousMode with value {anonymous_value}", 'info')

    if options.get('steamAccountName'):
        steamAccountName_value = options['steamAccountName']
        conf.configureSetting('steamAccountName', steamAccountName_value)
        rPrint(f"Configured steamAccountName with value {steamAccountName_value}", 'info')

    if options.get('steamPassword'):
        steamPassword_value = options['steamPassword']
        conf.configureSetting('steamPassword', steamPassword_value)
        rPrint(f"Configured steamPassword with value {steamPassword_value}", 'info')

    if options.get('encrypted'):
        encrypted_value = options['encrypted']
        conf.configureSetting('encrypted', encrypted_value)
        rPrint(f"Configured encrypted with value {encrypted_value}", 'info')

    if options.get('encryptionKey'):
        encryptionKey_value = options['encryptionKey']
        conf.configureSetting('encryptionKey', encryptionKey_value)
        rPrint(f"Configured encryptionKey with value {encryptionKey_value}", 'info')

    if options.get('game'):
        game_value = options['game']
        conf.configureSetting('gameID', game_value)
        rPrint(f"Configured gameID with value {game_value}", 'info')

    if options.get('mod'):
        rPrint(f"Mod value: {options['mod']}", 'info')
        mods.extend(options['mod'].split(","))
        for i, item in enumerate(mods):
            if not item.startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
        if not options.get('collection'):
            rPrint(f'Requested Mods:\n{mods}', 'info')
        prompt = '1'

    if options.get('collection'):
        rPrint(f"Collection value: {options['collection']}", 'info')
        mods.extend(options['collection'].split(","))
        for i, item in enumerate(mods):
            if not item.startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
        rPrint(f'Requested Mods:\n{mods}', 'info')
        prompt = '1'

    if options.get('list'):
        prompt = '2'

    #if options.get('encryptPassword'):
        #prompt = '2'

    checkConfig()
    checkAndDownloadSteamCmd()
    while True:
        if prompt is None:
            settingsTable = Table(title="Welcome to SWD!", show_header=False, box=box.SIMPLE)
            settingsTable.add_row("[1]", "Download Mods")
            settingsTable.add_row("[2]", "List Mods")
            settingsTable.add_row("[3]", "Open Settings")
            settingsTable.add_row("[4]", "Exit")
            console.print(settingsTable, style="bold")
            prompt = rPrint('Please make a selection', "prompt")
        else:
            nonInteractive = True
        if prompt == '1':
            downloadMods(mods)
            break
            # if nonInteractive:
            #     exit()
        elif prompt == '2':
            listMods()
            prompt = None
            if nonInteractive:
                exit()
        elif prompt == '3':
            configure(Repo_Owner, Repo_Name)
            break
        elif prompt == '4':
            exit()
        else:
            rPrint('Invalid option passed, exiting.', 'error')
            exit()
