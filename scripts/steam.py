import requests
from bs4 import BeautifulSoup
from scripts.steamcmd import downloadModListSCMD
from scripts.config import fetchConfiguration

def processURL(url):
    result = url.split('id=')[1]
    if 'searchtext' in url:
        result = result.split('&searchtext')[0]
    return result

def checkType(url):
    if "https" not in url:
        return None
    res=requests.get(url)
    doc=BeautifulSoup(res.text,"html.parser")
    if cItems := doc.find_all(class_="collectionItemDetails"):
        return "collection"
    else:
        return "mod"

def processMod(url, Collection=False):
    mods = []
    res = requests.get(url)
    doc = BeautifulSoup(res.text, "html.parser")
    if Collection:
        itemList = doc.find_all(class_="collectionItemDetails")
        for item in itemList:
            mod_url = item.find("a", href=True)['href']
            _id = processURL(mod_url)
            if title_div := item.find(class_="workshopItemTitle"):
                title = title_div.text.strip()
            else:
                title = _id
            print(f'Queuing: {title}, {_id}')
            mods.append({
                'name': title,
                'id': _id
            })
    else:
        title = doc.head.title.text.split("::")[1]
        _id = processURL(url)
        print(f'Queuing: {title}, {_id}')
        mods.append({
            'name': title,
            'id': _id
        })
    return mods

def downloadModList(modList=None):
    mods = []
    gameid = fetchConfiguration('gameID')
    dwn = fetchConfiguration('downloadDir')
    if modList is None:
        print('(ERROR) No mods provided!')
        return 1
    for mod_dict in modList:
        collections_urls = mod_dict["collections"]
        modURLs = mod_dict["mods"]
        mods.extend(processMod(url, True) for url in collections_urls)
        for url in modURLs:
            mods.append(processMod(url))
    downloadModListSCMD(gameid, mods, dwn)
    
    # To-Do: Remove duplicates