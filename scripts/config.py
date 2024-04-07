from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
import json
import re
from scripts.init import _CONFIG
from getpass import getpass
from tkinter import Tk
from tkinter.filedialog import askopenfilename,asksaveasfilename

encryptionKey=None

def configureSetting(setting, val):
    if _CONFIG is not None:
        _CONFIG[setting] = val
    else:
        with open("conf.json", "r+") as f:
            js = json.load(f)
            js[setting] = val
            f.seek(0)
            json.dump(js, f, indent=4)
            f.truncate()

def getYN(prompt, default=None):
    """Prompt the user for a yes/no answer with an optional default value."""
    if default is not None:
        default_indicator = 'Y/n' if default else 'y/N'
        prompt = f"{prompt} [{default_indicator}] => "
    else:
        prompt = f"{prompt} [y/n] => "

    while True:
        user_input = input(prompt).lower().strip()
        if user_input == '' and default is not None:
            return default
        elif user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes, 'n' for no, or press [Enter] for the default value.")

def getCredentials(skip=None):
    """
    Prompt the user for their steam credentials.
        If skip is set to None, the default value, collect & return `username, password, encryption_status`.
        If skip is set to True, skip the password/encryption collection, return only `username`.
        If skip is set to False, skip the username collection, return only `password, encryption_status`.
    """
    def getName():
        pattern = r'^[a-zA-Z0-9_]{2,32}$'
        name = input("What is your steam name? => ")
        while not name or not re.match(pattern, name):
            name = input("Please enter a valid steam name. => ")
        return name
    def getPass():
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,}$'
        pass_ = getpass("What is your steam password? => ")
        while not pass_ or not re.search(pattern, pass_):
            pass_ = getpass("Please enter a valid steam password. => ")

        confirm = getpass("Re-enter your password to confirm. => ")
        while pass_ != confirm:
            print("Passwords do not match, please try again.")
            pass_ = getpass("What is your steam password? => ")
            while not pass_:
                pass_ = input("Please enter a valid steam password. => ")
            confirm = getpass("Re-enter your password to confirm. => ")

        if encrypt := getYN("Encrypt password?", True):
            if encryptionKey := keySave():
                if keyGeneration(encryptionKey):
                    pass_ = encryptPassword(pass_, encryptionKey)
                    print('(INFO) Password Encrypted.')
                else:
                    print('(ERROR) Key generation failed, exiting.')
                    exit()
            else:
                print('(ERROR) Key save failed, exiting.')
                exit()
        elif encrypt := getYN(
            "(WARN) Password will be stored in plain text,\nContinue without encryption?",
            False,
        ):
            print('(WARN) Password stored in plain text.')
        elif encryptionKey := keySave():
            if keyGeneration(encryptionKey):
                pass_ = encryptPassword(pass_, encryptionKey)
                print('(INFO) Password Encrypted.')
            else:
                print('(ERROR) Key generation failed, exiting.')
                exit()
        else:
            print('(ERROR) Key save failed, exiting.')
            exit()
        return pass_, str(bool(encrypt or encryptionKey is not None)).lower()
    if skip is None:
        return getName(), getPass()
    elif skip:
        return getName()
    else:
        return getPass()

def keyGeneration(key_location):
    key = Fernet.generate_key()
    with open(key_location, 'wb') as keyfile:
        try:
            keyfile.write(key)
        except Exception as e:
            print(f'Key save failed!\n{e}')
            return False
    return True

def encryptPassword(password, key_file):
    try:
        with open(key_file, 'rb') as keyfile:
            key = keyfile.read()
        fernet = Fernet(key)
        return fernet.encrypt(password.encode())
    except (InvalidToken, OSError) as e:
        print(f"Error encrypting password: {e}")
        return None

def decryptPassword(encrypted_password, key_file):
    try:
        with open(key_file, 'rb') as keyfile:
            key = keyfile.read()
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_password).decode()
    except (InvalidToken, OSError) as e:
        print(f"Error decrypting password: {e}")
        return None

def keySelection():
    print("Path to Steam Password encryption key => ")
    Tk().withdraw()
    if encryptionKey := askopenfilename(
        title="Select the Steam Password encryption key file",
        filetypes=(
            ("Key files", "*.key"),
            ("All files", "*.*"),
        ),
    ):
        print(f"Selected key file: {encryptionKey}")
        conf.configureSetting('encryptionKey', prompt)
        return encryptionKey
    else:
        print("(ERROR) No encryption key selected!")
        return None

def keySave():
    print("Save path for Steam Password encryption key => ")
    Tk().withdraw()
    if encryption_key_file := asksaveasfilename(
        title="Choose a location to save the encryption key",
        filetypes=(("Key files", "*.key"), ("All files", "*.*")),
        defaultextension=".key",
    ):
        conf.configureSetting('encryption', 'true')
        return encryption_key_file
    else:
        print('(ERROR) No encryption key file location provided!')
        return None

def fetchConfiguration(val=None):
    if _CONFIG is not None:
        return _CONFIG if val is None else str(_CONFIG[val])
    with open("conf.json", "r") as f:
        js = json.load(f)
    return js if val is None else str(js[val])
