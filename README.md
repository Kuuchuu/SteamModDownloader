# SteamModDownloader
A Steam Workshop Downloader CLI-tool for linux,

Developed by NBZion.  
Extended by Kuuchuu.

## Installation
Make sure you have the following installed in your system
```
git
python3
python3-env or virtualenv
```

Navigate to the directory you would like to unpack smd in then run the following commands:
```bash
wget https://github.com/Kuuchuu/SteamModDownloader/releases/latest/download/smd.py -O smd.py # Or manually download the latest `smd.py` from releases tab.
chmod +x ./smd.py
./smd.py install # Execute script
```
If you want to replace your already existing installation completely:
```bash
./smd.py reinstall
```

## Usage
To start SMD (assuming it has been installed properly), run this command:
```bash
./smd.py launch --optionalFlags
```
Here's a list of all the settings and what they are:
```js
'downloadDir': the directory mods will be downloaded to.
'anonymousMode': whether or not to use a real account.
'steamAccountName': account username if not using anonymous mode.
'steamPassword': account password if not using anonymous mode.
'gameID': ID of the game you want the workshop mods for.
```
These are configured at startup once, and can be changed in settings.
To download your mods, simply select the "Download Mods" option and
paste your workshop url/link. It will be downloaded to `downloadDir`.

Optional launch Flags:
```bash
    -c/--config '{"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","encrypted":"","gameID":""":""}'

    -f/--configFile '/path/to/smd_config.json'

    -t/--tempConfig # Passed configuration data will not be stored. BOOLEAN, Defaults to True

    -g/--game GAME_ID

    -m/--mod 'ID_NUMBER,https://steam.../?id=...,ID_NUMBER,https://steam.../?id=...'

    -c/--collection 'ID_NUMBER,ID_NUMBER' OR 'https://steam.../?id=...,https://steam.../?id=...' # Mod/Collection URLs/IDs can be mix-matched

    -o/--outputDir '/path/to/modDL/output'

    -a/--anonymousMode # Skip Steam authentication. NOTE: Some downloads may fail without authentication. BOOLEAN, Defaults to True when passed

    -u/--steamUsername 'Username'

    -p/--steamPassword 'Plain text password' # NOTE: Can first be encrypted by calling `smd.py launch` with the -n/--encryptPassword flag followed by the password.

    -e/--encrypted # Is password encrypted? Set this to have SMD prompt for the key file during operation. BOOLEAN, Defaults to True when passed

    -k/--encryptionKey '/path/to/smd.key'

    -n/--encryptPassword 'Plain text password' # Prompts for key file save location and returns encrypted password.

    -l/--list # List installed mods

    -v/--verbose # Extra chatty output.

    -m/--minimal # Very basic output. Useful for non-interactive scripts.

    -s/--silent # What's it doing? When will it finish? Who knows...

    -h/--help
```
Example:
```bash
# DL Mods
./smd.py launch -c '{"downloadDir":"/tmp/dlDir","anonymousMode":"false,"steamAccountName":"kuuchuu","steamPassword":"⠏⠁⠎⠎⠺⠕⠗⠙","gameID":"001492"}' -g 294100 -p 'https://steamcommunity.com/sharedfiles/filedetails/?id=2457667915,2899200937' -m 'https://steamcommunity.com/sharedfiles/filedetails/?id=2009463077,836308268,https://steamcommunity.com/sharedfiles/filedetails/?id=1874644848'
# Notes:
# - 'anonymousMode' boolean value should be lowercase
# - Flags are applied in the same order as "Optional launch Flags" guide; In the example above the game ID "294100" would take precedence over the config's gameID value of "001492"

# List Downloaded Mods
./smd.py launch --list
```

## Features
- Collection Support
  - Batch Collection Support
 
## Currently Known Issues
- Downloading a mod may not work until you delete the steamcmd folder and try to re-download it.

## Some Things To Note...
- This project is currently only built for the linux python version.
  - Windows support soon, Mac support eventually.
- Some mods may not download in anonymous mode, if so please use steam account option in config.
- My code is messy, so feel free to pull-request any changes!
- This project is still being updated, it's just that I'm either busy or don't have a feature to add, so please suggest potential features or report bugs in the issues page.

## TODO
- [ ] Windows Support
- [x] Wrapper Scripts 
- [ ] Compile into whl

