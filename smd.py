#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import sys
option = sys.argv[1] if len(sys.argv) > 1 else None

Repo_Owner = "Kuuchuu"
Repo_Name = "Steam-Workshop-Toolkit"

def install():
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
    for p in Path(directory).glob('*'):
        if p.is_file() or p.is_symlink():
            p.unlink()
            print(f"Removed: {p}")
        else:
            shutil.rmtree(p, onerror=lambda func, path, exc_info: print(f"Error removing {path}"))
            print(f"Removed directory: {p}")

def reinstall():
    # Warning and continue prompt
    input("[WARN] This action will delete all files in this directory, and re-download SMD in your local directory.\n"
          "[WARN] Make sure there are no important files in this directory before continuing! (This will also destroy your configuration, save it.)\n"
          "[PROMPT] (Press CTRL+C to quit, or ENTER to continue) ")

    # Delete SMD files
    fcount = len([name for name in os.listdir('.') if os.path.isfile(name)]) - 1
    print(f"[PROCESS] Deleting {fcount} files/folders.")
    clear_directory('.')
    # for root, dirs, files in os.walk('.', topdown=False):
    #     for name in files:
    #         file_path = os.path.join(root, name)
    #         os.remove(file_path)
    #     for name in dirs:
    #         dir_path = os.path.join(root, name)
    #         try:
    #             os.rmdir(dir_path)
    #         except OSError:
    #             # If os.rmdir fails due to symlink or non-empty directory, use shutil.rmtree
    #             shutil.rmtree(dir_path, ignore_errors=True)

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

def update():
    # Create temporary folder for update
    os.system(f"git clone https://github.com/{Repo_Owner}/{Repo_Name}.git update/")

    # Remove and update scripts, smd, and version.txt
    update_items = ["scripts", "smd", "version.txt"]
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

def launch():
    print("[PROCESS] Starting SMD.")
    # Run tool. (Assume python3 available)
    os.system(f"./.clientEnv/bin/python3 __main__.py {Repo_Owner} {Repo_Name}")

def move_and_clean():
    for item in os.listdir(f'./{Repo_Name}'):
        s_path = os.path.join(f'./{Repo_Name}', item)
        d_path = os.path.join('.', item)
        if os.path.isdir(s_path) and os.path.exists(d_path):
            shutil.rmtree(d_path)
        shutil.move(s_path, '.')
    shutil.rmtree(f'./{Repo_Name}')

options = {
    "install": install,
    "reinstall": reinstall,
    "update": update,
    "launch": launch
}

if option in options:
    options[option]()
else:
    print("[ERROR] Invalid option passed, exiting with code 1.")
    sys.exit(1)
