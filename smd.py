#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

# Change following to fork's repo name/owner:
Repo_Owner = "Kuuchuu"
Repo_Name = "SteamModDownloader"

# To-Do:
# - Add support for password encryption
# - Verbose & Silent modes
# - If conf supplied via arg, require saveConf flag for passed conf to be written to conf.json, otherwise conf is not saved after session.
# - Fancy output (Color INFO, WARN, ERROR)
# /To-Do

def install(args):
    """
    Installs SteamModDownloader (SMD) in the current directory if not already installed.
    If already installed, it reinstalls SMD.

    Args:
        args (argparse.Namespace): Command-line arguments passed to the function. NOT USED.

    Returns:
        None
    """
    # Check if files already exist
    if os.path.exists("scripts") and os.path.exists("__main__.py"):
        reinstall()
        return

    # Make venv (due to recent python changes)
    os.system("python3 -m venv .clientEnv")

    # Warning and continue prompt
    input("[WARN] This action will download SMD in your local directory.\n[PROMPT] (Press CTRL+C to quit, or ENTER to continue) ")

    # Clone SMD to current directory
    os.system(f"git clone https://github.com/{Repo_Owner}/{Repo_Name}.git")

    # Move files to current directory and dispose of cloned folder
    move_and_clean()

    # Remove [.git] and install dependencies
    if os.path.exists(".git"):
        shutil.rmtree(".git")
    os.system("./.clientEnv/bin/pip install -r requirements.txt")

    # Success message
    print("[SUCCESS] You can now launch SMD.")

def clear_directory(directory):
    """
    Clears all files and subdirectories within the specified directory.

    Args:
        directory (str): The path to the directory to be cleared.

    Returns:
        None
    """
    for p in Path(directory).glob('*'):
        if p.is_file() or p.is_symlink():
            p.unlink()
            print(f"Removed: {p}")
        else:
            shutil.rmtree(p, onerror=lambda func, path, exc_info: print(f"Error removing {path}"))
            print(f"Removed directory: {p}")

def reinstall(args):
    """
    Reinstalls SteamModDownloader (SMD) in the current directory by deleting existing files and re-downloading SMD.

    Args:
        args (argparse.Namespace): Command-line arguments passed to the function. NOT USED.

    Returns:
        None
    """
    # Warning and continue prompt
    input("[WARN] This action will delete all files in this directory, and re-download SMD in your local directory.\n"
          "[WARN] Make sure there are no important files in this directory before continuing! (This will also destroy your configuration, save it.)\n"
          "[PROMPT] (Press CTRL+C to quit, or ENTER to continue) ")

    # Delete SMD files
    fcount = len([name for name in os.listdir('.') if os.path.isfile(name)]) - 1
    print(f"[PROCESS] Deleting {fcount} files/folders.")
    clear_directory('.')

    # Clone SMD to current directory
    os.system(f"git clone https://github.com/{Repo_Owner}/{Repo_Name}.git")
    
    # Make venv(due to recent python changes)
    os.system("python3 -m venv .clientEnv")
    
    # Move files to current directory and dispose of cloned folder
    move_and_clean()

    # Remove [.git] and install dependencies
    if os.path.exists(".git"):
        shutil.rmtree(".git")
    os.system("./.clientEnv/bin/pip install -r requirements.txt")
    
    # Success message
    print("[SUCCESS] You can now launch SMD.")

def update(args):
    """
    Updates SteamModDownloader (SMD) by cloning the latest version from the repository and replacing specific files.

    Args:
        args (argparse.Namespace): Command-line arguments passed to the function. NOT USED.

    Returns:
        None
    """
    # Create temporary folder for update
    os.system(f"git clone https://github.com/{Repo_Owner}/{Repo_Name}.git update/")

    # Remove and update scripts, smd, and version.txt
    update_items = ["scripts", "smd.py", "requirements.txt", "version.txt"]
    for item in update_items:
        print(f"[PROCESS] Updating {item}")
        item_path = os.path.join('.', item)
        if os.path.exists(item_path):
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)
        update_path = os.path.join('update', item)
        if os.path.isfile(update_path):
            shutil.move(update_path, '.')
        else:
            shutil.move(update_path, item_path)

    # Remove temporary folder
    shutil.rmtree('./update')

    # Success message
    print("[SUCCESS] Updated SMD.")

def launch(args):
    """
    Launches SteamModDownloader (SMD) tool with any provided command-line arguments.

    Args:
        args (argparse.Namespace): Command-line arguments to be passed to the SMD tool.

    Returns:
        None
    """
    print("[PROCESS] Starting SMD.")
    from scripts.init import start
    args_dict = {k: v for k, v in vars(args).items() if v is not None}
    # print(f'smd.py | Repo Owner: {Repo_Owner}')
    # print(f'smd.py | Repo Name: {Repo_Name}')
    # print(f'smd.py | Options: {args_dict}')
    start(Repo_Owner, Repo_Name, options=args_dict)

def move_and_clean():
    """
    Moves necessary files to the current directory and cleans up the cloned repository folder.

    Args:
        None

    Returns:
        None
    """
    for item in os.listdir(f'./{Repo_Name}'):
        s_path = os.path.join(f'./{Repo_Name}', item)
        d_path = os.path.join('.', item)
        if os.path.isdir(s_path) and os.path.exists(d_path):
            shutil.rmtree(d_path)
        if os.path.isfile(s_path) and item == "smd.py":
            with open(s_path, 'r', encoding='utf-8') as file:
                new_smd = file.read()
            with open(__file__, 'w', encoding='utf-8') as file:
                file.write(new_smd)
            os.chmod(__file__, 0o755)
            os.remove(s_path)
        else:
            shutil.move(s_path, '.')
    shutil.rmtree(f'./{Repo_Name}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SteamModDownloader - A Steam Workshop Downloader CLI-tool for linux")
    
    subparsers = parser.add_subparsers(help='commands', dest='command')

    install_parser = subparsers.add_parser('install', help='Install smd.')
    install_parser.set_defaults(func=install)

    reinstall_parser = subparsers.add_parser('reinstall', help='Reinstall smd.')
    reinstall_parser.set_defaults(func=reinstall)

    update_parser = subparsers.add_parser('update', help='Update smd.')
    update_parser.set_defaults(func=update)

    launch_parser = subparsers.add_parser('launch', help='Launch smd. Accepts optional arguments, `install -h` for more information.')
    launch_parser.set_defaults(func=launch)
    
    launch_parser.add_argument('-c', '--config', type=json.loads,
                        help='Configuration in JSON format. Example: \'{"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","gameID":""}\'')
    launch_parser.add_argument('-f', '--configFile', type=str,
                        help='Path to the configuration file. Example: \'/path/to/smd_config.json\'')
    launch_parser.add_argument('-g', '--game', type=str,
                        help='Game\'s Steam ID. Example: 294100')
    launch_parser.add_argument('-m', '--mod', type=str,
                        help='ID_NUMBER,ID_NUMBER or URLs. Example: \'ID_NUMBER,ID_NUMBER\' OR \'https://steam.../?id=...,https://steam.../?id=...\'')
    launch_parser.add_argument('-p', '--pack', type=str,
                        help='ID_NUMBER,ID_NUMBER or URLs. Example: \'ID_NUMBER,ID_NUMBER\' OR \'https://steam.../?id=...,https://steam.../?id=...\'')
    launch_parser.add_argument('-o', '--outputDir', type=str,
                        help='Path to the mod download output directory. Example: \'/path/to/modDL/output\'')
    launch_parser.add_argument('-l', '--list', action='store_true',
                        help='List all currently downloaded mods.')
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)
