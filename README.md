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
    -c/--config='{"downloadDir":"","anonymousMode":"","steamAccountName":"","steamPassword":"","gameID":""}'

    -f/--configFile='/path/to/smd_config.json'

    -g/--game=GAME_ID

    -m/--mod='ID_NUMBER,ID_NUMBER' OR 'https://steam.../?id=...,https://steam.../?id=...'

    -p/--pack='ID_NUMBER,ID_NUMBER' OR 'https://steam.../?id=...,https://steam.../?id=...'

    -o/--outputDir='/path/to/modDL/output'

    -l/--list # List installed mods

    -h/--help
```

## Features
- Collection Support
 
## Currently Known Issues
- Downloading a mod may not work until you delete the steamcmd folder and try to re-download it.
- steamCMD currently prompts for Steam Guard key for every single mod in a collection 😬

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

