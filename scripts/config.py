import base64
import json
import os
import re
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from tkinter import Tk
from tkinter.filedialog import askopenfilename,asksaveasfilename
from typing import Union, ByteString

encryptionKey=None

def configureSetting(setting, val):
    from scripts.init import _CONFIG
    if _CONFIG is not None:
        _CONFIG[setting] = val
    else:
        with open("conf.json", "r+") as f:
            js = json.load(f)
            js[setting] = str(val)
            f.seek(0)
            json.dump(js, f, indent=4)
            f.truncate()

def getYN(prompt, default=None):
    """Prompt the user for a yes/no answer with an optional default value."""
    from scripts.init import rPrint
    if default is not None:
        default_indicator = 'y/N' if default.lower().startswith("n") else 'Y/n'
        rPrint(f'{prompt} \[{default_indicator}]', "prompt", "skip-input")
        # prompt = f"{prompt} [{default_indicator}] => "
    else:
        rPrint(f'{prompt} \[y/n]', "prompt", "skip-input")
        # prompt = f"{prompt} [y/n] => "

    while True:
        # user_input = input(prompt).lower().strip()
        user_input = input().lower().strip()
        if user_input == '' and default is not None:
            return not default.lower().startswith('n')
        elif user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            rPrint('Please enter \'y\' for yes, \'n\' for no, or press [Enter] for the default value.', "warn")

def getCredentials(skip=None):
    """
    Prompt the user for their steam credentials.
        If skip is set to None, the default value, collect & return `username, password, encrypted_status`.
        If skip is set to True, skip the password/encryption collection, return only `username`.
        If skip is set to False, skip the username collection, return only `password, encrypted_status`.
    """
    def getName():
        from scripts.init import rPrint
        pattern = r'^[a-zA-Z0-9_]{2,32}$'
        name = rPrint('Steam Username', "prompt")
        while not name or not re.match(pattern, name):
            name = rPrint('Please enter a valid Steam Username', "prompt")
        return name
    def getPass(pass_=None):
        from scripts.init import rPrint
        pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{6,}$'
        if pass_ is None:
            pass_ = rPrint('Steam Password', "getpass")
            while not re.search(pattern, pass_):
                pass_ = rPrint('Please enter a valid Steam Password', "getpass")

            confirm = rPrint('Re-enter Steam Password', "getpass")
            while pass_ != confirm:
                rPrint('Passwords do not match, please try again.', "warn")
                pass_ = rPrint('Steam Password', "getpass")
                confirm = rPrint('Re-enter Steam Password', "getpass")

        if getYN("Encrypt password?", "y"):
            if key_location := keySave():
                if generate_key(key_location):
                    key = read_key(key_location)
                    pass_ = encrypt_pass(pass_, key)
                    rPrint('Password Encrypted.', "success")
                    return pass_, True
                else:
                    rPrint('Key generation failed, exiting.', "error")
                    exit(1)
            else:
                rPrint('Key save failed, exiting.', "error")
                exit(1)
        elif getYN("Continue without encryption?", "n"):
            rPrint('Password stored in plain text.', "warn")
            return pass_, False
        else:
            return getPass(pass_)
    if skip is None:
        return getName(), getPass()
    elif skip:
        return getName()
    else:
        return getPass()

def generate_key(key_location: str) -> bool:
    """
    Generates a cryptographic key and saves it to the specified location, overwriting any existing file.

    Args:
        key_location: The file path where the key should be saved.

    Returns:
        True on success, raises an exception on failure.

    Raises:
        Exception: If the key file could not be written.
    """
    key = Fernet.generate_key()
    try:
        with open(key_location, 'wb') as key_file:
            key_file.write(key)
        return True
    except Exception as e:
        raise Exception(f"Failed to write the key to {key_location}") from e
    
def read_key(key_location: str) -> bytes:
    """
    Reads a cryptographic key from the specified file.

    Args:
        key_location: The file path from which the key should be read.

    Returns:
        The cryptographic key as bytes.

    Raises:
        FileNotFoundError: If the key file does not exist.
        Exception: If there was an issue reading the file.
    """
    if not os.path.exists(key_location):
        raise FileNotFoundError(f"No key file found at {key_location}")
    try:
        with open(key_location, 'rb') as key_file:
            key = key_file.read()
        return key
    except Exception as e:
        raise Exception(f"Failed to read the key from {key_location}") from e

def generate_salt(saltLen: int = 32) -> str:
    """
    Make a salt of specific length using cryptographically secure random generator.

    Args:
        saltLen: Length of the constructed salt.

    Returns:
        A cryptographically secure random salt string.
    """
    import string, secrets
    charChoice = string.ascii_letters + string.digits + string.punctuation
    #charChoice = string.ascii_letters + string.digits
    return ''.join(secrets.choice(charChoice) for _ in range(saltLen))

def encrypt_pass(password: str, key: Union[str, ByteString, bytes]) -> str:
    """
    Encrypts a given password with a key. Generates and prepends a salt to the password before encryption.

    Args:
        password: Current value to encrypt.
        key: A base64-encoded 32-byte key.

    Returns:
        A single string containing the salt length, salt, and encrypted value.
    """
    salt = generate_salt(32)
    salt_len = len(salt)
    if isinstance(key, str):
        key = base64.urlsafe_b64encode(key.encode()).decode()
    encryptor = Fernet(key)
    salted_password = salt + password
    encrypted_pass = encryptor.encrypt(salted_password.encode('utf-8'))
    return f'{salt_len}:{salt}{encrypted_pass.decode("utf-8")}'

def decrypt_pass(salted_pass: str, key: Union[str, ByteString, bytes]) -> str:
    """
    Decrypts a given value from a key and salt that were used during encryption.

    Args:
        salted_pass: The combined string containing salt length, salt, and encrypted value.
        key: A URL-safe base64-encoded 32-byte key.

    Returns:
        The original plaintext value, decrypted and with the salt removed.
    """
    from scripts.init import rPrint
    rPrint(f'Salted Pass: {salted_pass}', "log")
    rPrint(f'Supplied Key: {key}', "log")
    salt_len_end_index = salted_pass.find(':')
    rPrint(f'Salt Len End Index: {salt_len_end_index}', "log")
    salt_len = int(salted_pass[:salt_len_end_index])
    rPrint(f'Salt Len: {salt_len}', "log")
    salt = salted_pass[salt_len_end_index+1:salt_len_end_index+1+salt_len]
    rPrint(f'Salt: {salt}', "log")
    encrypted_pass = salted_pass[salt_len_end_index+1+salt_len:]
    rPrint(f'Encrypted Pass: {encrypted_pass}', "log")
    if isinstance(key, str):
        rPrint("Key is string", "log")
        key = base64.urlsafe_b64decode(key.encode())
        rPrint(f'Key: {key}', "log")
    elif isinstance(key, ByteString):
        rPrint("Key is ByteString", "log")
    decryptor = Fernet(key)
    decrypted_pass = decryptor.decrypt(encrypted_pass).decode('utf-8')[salt_len:]
    rPrint('Decrypted Pass: ' + '*' * len(decrypted_pass), "log")
    return decrypted_pass

def keySelection():
    from scripts.init import rPrint
    rPrint('Path to Steam Password encryption key', "prompt", "skip-input")
    Tk().withdraw()
    if encryptionKey := askopenfilename(
        title="Select the Steam Password encryption key file",
        filetypes=(
            ("Key files", "*.key"),
            ("All files", "*.*"),
        ),
    ):
        rPrint(f"Selected key file: {encryptionKey}", "log")
        configureSetting('encryptionKey', encryptionKey)
        return encryptionKey
    else:
        rPrint('No encryption key selected!', "error")
        return None

def keySave():
    from scripts.init import rPrint
    rPrint('Save path for Steam Password encryption key', "prompt", "skip-input")
    Tk().withdraw()
    if encryption_key_file := asksaveasfilename(
        title="Choose a location to save the encryption key",
        filetypes=(("Key files", "*.key"), ("All files", "*.*")),
        defaultextension=".key",
    ):
        configureSetting('encrypted', 'true')
        return encryption_key_file
    else:
        rPrint('No encryption key file location provided!', "error")
        return None

def fetchConfiguration(val=None):
    from scripts.init import _CONFIG
    if _CONFIG is not None:
        return _CONFIG if val is None else str(_CONFIG[val])
    with open("conf.json", "r") as f:
        js = json.load(f)
    try:
        return js if val is None else str(js[val])
    except KeyError:
        return ""
