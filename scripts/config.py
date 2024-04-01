import json
import re
from getpass import getpass

def configureSetting(setting, val):
    with open("conf.json", "r+") as f:
        js = json.load(f)
        js[setting] = val
        f.seek(0)
        json.dump(js, f, indent=4)
        f.truncate()

def getCredentials():
    pattern = r'^[a-zA-Z0-9_]{2,32}$'
    name = input("What is your steam name?\n> ")
    while not name or not re.match(pattern, name):
        name = input("Please enter a valid steam name.\n> ")

    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,}$'
    pass_ = getpass("What is your steam password?\n> ")
    while not pass_ or not re.search(pattern, pass_):
        pass_ = getpass("Please enter a valid steam password.\n> ")

    confirm = getpass("Re-enter your password to confirm.\n> ")
    while pass_ != confirm:
        print("Passwords do not match, please try again.")
        pass_ = getpass("What is your steam password?\n> ")
        while not pass_:
            pass_ = input("Please enter a valid steam password.\n> ")
        confirm = getpass("Re-enter your password to confirm.\n> ")

    return name, pass_

def fetchConfiguration(val=None):
    with open("conf.json", "r") as f:
        js = json.load(f)
    return js if val is None else js[val]
