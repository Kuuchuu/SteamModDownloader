import datetime
import json
import os
import re
import requests
import scripts.config as conf
import scripts.steam as steam
import sys
from getpass import getpass
from rich import box
from rich.console import Console; console = Console()
from rich.panel import Panel
from rich.table import Table
from scripts.steamcmd import check_and_download_steamcmd
from sys import exit
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Defaults to original repo if not provided to `start()` function. Shouldn't need changed, change values in smd.py instead.
original_repo_owner,repo_owner="NBZion",""
original_repo_name,repo_name="SteamModDownloader",""

def rprint(message=None, type=None, custom_style=None, table_data=None):
    if custom_style is None:
        custom_style = ""
    match str(type).lower():
        case 'rule':
            console.rule(message, style=custom_style)
            return
        case 'panel':
            ptitle = ""
            pmessage = ""
            if message is not None:
                ptitle = message.get('title')
                pmessage = message.get('message')
            console.print(Panel(pmessage, title=ptitle), style=custom_style)
            return
        case 'table':
            if table_data is not None:
                console.print(table_data, style=custom_style)
            else:
                console.print(message, style=custom_style)
            return
        case 'log':
            global _VERBOSE
            if _VERBOSE:
                console.log(f"{str(datetime.datetime.now())} | {message}", style=custom_style)
            return
        case 'error':
            message = f'❌  {str(message)}'
            custom_style = f'bold red {custom_style} '
        case 'warn':
            message = f'⚠️  {str(message)}'
            custom_style = f'bold yellow {custom_style}'
        case 'info':
            message = f'ℹ️  {str(message)}'
            custom_style = f'bold cyan {custom_style}'
        case 'pop':
            message = str(message)
            custom_style = f'bold magenta {custom_style}'
        case 'success':
            message = f'✅  {str(message)}'
            custom_style = f'bold green {custom_style}'
        case 'getpass':
            message = f'❔  {str(message)} » '
            custom_style = f'bold cyan {custom_style}'
            console.print(f'{message}', style=custom_style, end=""); sys.stdout.flush()
            return getpass(prompt='')
        case 'prompt':
            message = f'❔  {str(message)} » '
            if "skip-input" in custom_style:
                custom_style = custom_style.replace("skip-input", "")
                type = "skip-prompt"
            custom_style = f'bold cyan {custom_style}'
            console.print(f'{message}', style=custom_style, end=""); sys.stdout.flush()
            if type == "skip-prompt":
                return
            return input()
        # case _:
    console.print(message, style=custom_style)
    return

def check_version():
    current_version = open('version.txt','r').readline()
    listed_version = requests.get(f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/version.txt").text

    if current_version != listed_version:
        cl_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        cl_response = requests.get(cl_url)
        cl_data = cl_response.json()
        changelog = cl_data.get("body", "No description available.")
        rprint("Please update SMD with smd update!", "warn")
        #rprint("Please update SMD with smd update!", None, "bold yellow")
        rprint(f"Current Version: {current_version}")
        rprint(f"New Version: {listed_version}", "pop")
        rprint({"title":"Changelog","message":changelog}, "panel")

def check_empty_list(config):
    for key, value in config.items():
        if isinstance(value, list) and not value:
            rprint(f"Configuration for '{key}' is an empty list.", "warn")
            conf.configure_setting(key, "")
            return True
    return False

def verify_conf(fail_count={'emptyList':0, 'downloadDir':0, 'anonymousMode':0, 'steamAccountName':0, 'steamPassword':0, 'encrypted':0, 'gameID':0}):
    class conf_err(Exception):
        def __init__(self, message="", prompt=None):
            super().__init__(message)
            self.prompt = prompt
    try:
        if check_empty_list(conf.fetch_configuration()):
            fail_count['emptyList'] += 1
            raise conf_err('conf.json data malformed!\nValue cleared')
        if conf.fetch_configuration('downloadDir') != "" and not os.path.exists(conf.fetch_configuration('downloadDir')):
            fail_count['downloadDir'] += 1
            raise conf_err('downloadDir does not exist or is invalid!', prompt=2)
        if conf.fetch_configuration('anonymousMode') != "" and conf.fetch_configuration('anonymousMode').lower() not in ("true", "false"):
            fail_count['anonymousMode'] += 1
            raise conf_err('Invalid anonymous mode value!', prompt=3)
        pattern = r'^[a-zA-Z0-9_]{2,32}$'
        if conf.fetch_configuration('steamAccountName') != "" and not re.match(pattern, conf.fetch_configuration('steamAccountName')):
            fail_count['steamAccountName'] += 1
            raise conf_err('Invalid steam account name!', prompt=4)
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,}$'
        if conf.fetch_configuration('steamPassword') != "" and not re.search(pattern, conf.fetch_configuration('steamPassword')):
            fail_count['steamPassword'] += 1
            raise conf_err('Invalid steam password!', prompt=5)
        if conf.fetch_configuration('encrypted') != "" and conf.fetch_configuration('encrypted').lower() not in ("true", "false"):
            fail_count['encrypted'] += 1
            raise conf_err('Invalid encrypted mode value!', prompt=5)
        if conf.fetch_configuration('gameID') != "" and not conf.fetch_configuration('gameID').isdigit():
            fail_count['gameID'] += 1
            raise conf_err('Invalid gameID!', prompt=1)
    except conf_err as e:
        if any(value > 3 for value in fail_count.values()):
            rprint(f'{e}\nToo many failures!\nPlease run `smd reinstall`, or manually fix conf.json.', "error")
            exit()
        rprint(f'{e}', "error")
        if e.prompt is not None:
            configure(e.prompt)
        rprint('Continuing configuration check...')
        verify_conf(fail_count)

def check_config():
    # Make configuration file if missing
    if not os.path.exists('./conf.json'):
        with open('conf.json', 'w') as f:
            f.write('{"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","encrypted":"","gameID":""}')

    verify_conf()

    # Reconfigure download directory setting if invalid
    if not os.path.exists(conf.fetch_configuration('downloadDir')):
        dlmsg="Non-existent mod download directory, please enter a new one"
        prompt=None
        if sys.stdout.isatty():
            prompt = rprint(dlmsg, "prompt")
        else:
            rprint(dlmsg, "prompt", "skip-input")
            Tk().withdraw()
            prompt = askdirectory(); print('')
        conf.configure_setting('downloadDir', prompt)

    # Reconfigure gameID if empty
    if conf.fetch_configuration('gameID') == "":
        prompt = rprint('gameID setting empty, please enter a new one', "prompt")
        conf.configure_setting('gameID', prompt)

    # Reconfigure anonymous mode if empty
    if conf.fetch_configuration('anonymousMode') == "":
        rprint("[DISCLAIMER] Information isn't gathered, and is only stored locally.\nPassword can be encrypted.", None, "yellow bold italic")
        if anonymous := conf.get_yn("Use anonymous mode?", "n"):
            conf.configure_setting('anonymousMode', "true")
        else:
            conf.configure_setting('anonymousMode', "false")

    # Check if anonymous mode is off and ask for credentials
    if conf.fetch_configuration("anonymousMode") == "false" and conf.fetch_configuration("steamAccountName") == "":
        username, password = conf.get_credentials()
        conf.configure_setting('steamAccountName', username)
        if isinstance(password, (list, tuple, set, dict)):
            conf.configure_setting('steamPassword', password[0])
            conf.configure_setting('encrypted', password[1])
        else:
            conf.configure_setting('steamPassword', password)

def download_mods(mods=None):
    mod_urls = []
    col_urls = []
    rprint(f'download_mods: {mods}', "log")
    if mods == [] or mods == [''] or mods is None:
        rprint('mods is None', "log")
        mods = []
        mods.extend(rprint("Comma Separated Mod/Collection Workshop URL/IDs", "prompt").split(","))
        rprint(f'download_mods: {mods}', "log")
        if mods == ['']:
            rprint('No mods/collections provided.', "error")
            return 1
        #mods.extend(input("Comma Separated Mod/Collection Workshop URL/IDs: ").split(","))
    for i, item in enumerate(mods):
        url_attempts = 0
        while True:
            if url_attempts > 3:
                rprint('Too many failures!', "error")
                return 1
            if mods[i] == "":
                break
            if not mods[i].startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
            url_check = steam.check_type(mods[i])
            if url_check == "mod":
                mod_urls.append(mods[i])
                break
            elif url_check == "collection":
                col_urls.append(mods[i])
                break
            else:
                rprint(f'Invalid URL "{url_check}", awaiting new.\nLeave empty to skip.', "warn")
                url_attempts += 1
                mods[i] = rprint("Mod/Collection Workshop URL/IDs", "prompt").split(",")
                #mods[i] = input("Mod/Collection Workshop URL/IDs: ").split(",")
    mod_list = [{"mods": mod_urls, "collections": col_urls}]
    rprint('Processing Mod(s)...', "info")
    steam.download_mod_list(mod_list)

def list_mods():
    mod_list = []
    for dir in os.listdir(conf.fetch_configuration('downloadDir')):
        smb_dir=os.path.join(conf.fetch_configuration('downloadDir'),os.path.join(dir, 'smbinfo.json'))
        if os.path.exists(smb_dir):
            json_data=json.load(open(smb_dir, 'r'))
#            mod_list.append(f"{json_data['name']} | [dark_khaki]{json_data['author']}[/dark_khaki] | {json_data['version']} | [wheat4]{json_data['description']}[/wheat4]")
            mod_list.append(f"{json_data['name']} | [dark_khaki]AUTHOR PLACEHOLDER[/dark_khaki] | VERSION PLACEHOLDER | [wheat4]DESCRIPTION PLACEHOLDER[/wheat4]")
    mod_list_table = Table(show_header=False, box=None, padding=1)
    for i, mod in enumerate(mod_list):
        # style = "underline" if (i + 1) % 2 == 0 else "" # Underline every other row. Opting for padding instead.
        mod_list_table.add_row(f'[bold magenta][{i+1}][/bold magenta]', mod)
    rprint({"title":"Current Mods","message":mod_list_table}, "panel", "yellow")

def configure(prompt=None):
    non_interactive=False
    if prompt is None:
        rprint("[DISCLAIMER] ALL data stored locally.", None, "yellow bold italic")
        settings_table = Table(title="Setting List", show_header=False, box=None)
        settings_table.add_row("[1]", "Game ID")
        settings_table.add_row("[2]", "Download Directory")
        settings_table.add_row("[3]", "Anonymous Mode")
        settings_table.add_row("[4]", "Steam Username")
        settings_table.add_row("[5]", "Steam Password")
        console.print(settings_table, style="bold")
        prompt = rprint('\nWhich setting would you like to change?', "prompt")
    else:
        non_interactive=True
    #console.rule()
    # if prompt not in [4, 5]:
    #     console.print('What value do you want to change it to?')
    if prompt == '2':
        dldirmsg="What directory would you like to change it to?"
        if not sys.stdout.isatty():
            Tk().withdraw()
            rprint(dldirmsg, "prompt", "skip-input")
            value = askdirectory()
        else:
            value = rprint(dldirmsg, "prompt")
    elif prompt == '4':
        value = conf.get_credentials(True)
    elif prompt == '5':
        value, encrypted = conf.get_credentials(False)
        conf.configure_setting('encrypted', encrypted)
    else:
        value = rprint('What value would you like to change it to?', "prompt")
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
            rprint('Invalid setting id, exiting.', 'error')
            exit()
    conf.configure_setting(setting, value)
    rprint(f'Configured {setting}.', 'info')
    if not non_interactive:
        start(repo_owner, repo_name)
    else:
        return True

_VERBOSE = False
_MINIMAL = False
_DEBUG = False
_CONFIG = None
def start(_repo_owner=original_repo_owner, _repo_name=original_repo_name, options=None):
    global repo_owner
    global repo_name
    repo_owner = _repo_owner
    repo_name = _repo_name
    if options is None:
        options = {}
    mods = []
    prompt=None
    non_interactive=False
    
    if options.get('verbose'):
        global _VERBOSE
        _VERBOSE = True
    if options.get('minimal'):
        global _MINIMAL
        _MINIMAL = True
        rprint('Quiet mode enabled but currently not implemented!', 'warn')
    if options.get('debug'):
        global _DEBUG
        _DEBUG = True
        rprint('Debug mode enabled but currently not implemented!', 'warn')
    if options.get('silent'):
        rprint('Silent mode enabled but clearly not working!', 'warn')
    
    check_version()

    if options.get('tempConfig'):
        _CONFIG = {"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","encrypted":"","gameID":""}
        rprint('Temporary config in use!', 'info')

    if options.get('config'):
        config_data = options['config']
        #console.print(f'Config data: {config_data}')
        try:
            for key, value in config_data.items():
                conf.configure_setting(key, value)
                if key == 'steamPassword':
                    value = '********'
                rprint(f"Configured {key} with value {value} from --config", 'info')
        except KeyError:
            rprint(f'Config data {config_data} invalid!', 'error')
            exit()

    if options.get('configFile'):
        config_file_path = options['configFile']
        if not os.path.exists(config_file_path):
            rprint(f'Config file {config_file_path} does not exist!', 'error')
            exit()
        with open(config_file_path, 'r') as file:
            try:
                config_data = json.load(file)
            except json.decoder.JSONDecodeError:
                rprint(f'Config file {config_file_path} is not valid JSON!', 'error')
                exit()
        for key, value in config_data.items():
            conf.configure_setting(key, value)
            if key == 'steamPassword':
                value = '********'
            rprint(f"Configured {key} with value {value} from --configFile", 'info')

    if options.get('outputDir'):
        output_dir_value = options['outputDir']
        conf.configure_setting('downloadDir', output_dir_value)
        rprint(f"Configured downloadDir with value {output_dir_value}", 'info')

    if options.get('anonymousMode'):
        anonymous_value = options['anonymousMode']
        conf.configure_setting('anonymousMode', anonymous_value)
        rprint(f"Configured anonymousMode with value {anonymous_value}", 'info')

    if options.get('steamAccountName'):
        steam_account_name_value = options['steamAccountName']
        conf.configure_setting('steamAccountName', steam_account_name_value)
        rprint(f"Configured steamAccountName with value {steam_account_name_value}", 'info')

    if options.get('steamPassword'):
        steam_password_value = options['steamPassword']
        conf.configure_setting('steamPassword', steam_password_value)
        rprint(f"Configured steamPassword with value {steam_password_value}", 'info')

    if options.get('encrypted'):
        encrypted_value = options['encrypted']
        conf.configure_setting('encrypted', encrypted_value)
        rprint(f"Configured encrypted with value {encrypted_value}", 'info')

    if options.get('encryptionKey'):
        encryption_key_value = options['encryptionKey']
        conf.configure_setting('encryptionKey', encryption_key_value)
        rprint(f"Configured encryptionKey with value {encryption_key_value}", 'info')

    if options.get('game'):
        game_value = options['game']
        conf.configure_setting('gameID', game_value)
        rprint(f"Configured gameID with value {game_value}", 'info')

    if options.get('mod'):
        rprint(f"Mod value: {options['mod']}", 'info')
        mods.extend(options['mod'].split(","))
        for i, item in enumerate(mods):
            if not item.startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
        if not options.get('collection'):
            rprint(f'Requested Mods:\n{mods}', 'info')
        prompt = '1'

    if options.get('collection'):
        rprint(f"Collection value: {options['collection']}", 'info')
        mods.extend(options['collection'].split(","))
        for i, item in enumerate(mods):
            if not item.startswith("https"):
                mods[i] = f'https://steamcommunity.com/sharedfiles/filedetails/?id={item}'
        rprint(f'Requested Mods:\n{mods}', 'info')
        prompt = '1'

    if options.get('list'):
        prompt = '2'

    #if options.get('encryptPassword'):
        #prompt = '2'

    check_config()
    check_and_download_steamcmd()
    while True:
        if prompt is None:
            settings_table = Table(title="Welcome to SWD!", show_header=False, box=box.SIMPLE)
            settings_table.add_row("[1]", "Download Mods")
            settings_table.add_row("[2]", "List Mods")
            settings_table.add_row("[3]", "Open Settings")
            settings_table.add_row("[4]", "Exit")
            console.print(settings_table, style="bold")
            prompt = rprint('Please make a selection', "prompt")
        else:
            non_interactive = True
        if prompt == '1':
            download_mods(mods)
            break
            # if non_interactive:
            #     exit()
        elif prompt == '2':
            list_mods()
            prompt = None
            if non_interactive:
                exit()
        elif prompt == '3':
            configure(repo_owner, repo_name)
            break
        elif prompt == '4':
            exit()
        else:
            rprint('Invalid option passed, exiting.', 'error')
            exit()
