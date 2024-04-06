from cryptography.fernet import Fernet
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

def keyGeneration(key_location):
    if not os.path.exists(os.path.join(key_location, 'smd.key')):
        raise ValueError("Invalid key location!")
    key = Fernet.generate_key()
    with open(os.path.join(key_location, 'smd.key'), 'wb') as keyfile:
        keyfile.write(key)
    return os.path.join(key_location, 'smd.key')

def encryptPassword(password, key_file):
    with open(key_file, 'rb') as keyfile:
        key = keyfile.read()
    fernet = Fernet(key)
    return fernet.encrypt(password.encode())

def decryptPassword(encrypted_password, key_file):
    # Load the key from the key file
    with open(key_file, 'rb') as keyfile:
        key = keyfile.read()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password).decode()

def fetchConfiguration(val=None):
    with open("conf.json", "r") as f:
        js = json.load(f)
    return js if val is None else js[val]
