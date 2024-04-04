import requests
from bs4 import BeautifulSoup
from scripts.steamcmd import download,downloadCollectionSCMD
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

def downloadMod(url):
    dwn = fetchConfiguration('downloadDir')
    gameid = fetchConfiguration('gameID')
    res = requests.get(url)
    doc = BeautifulSoup(res.text, "html.parser")
    title = doc.head.title.text.split("::")[1]
    _id = processURL(url)
    download(_id, gameid, title, dwn)

# def downloadCollection(url):
#     res = requests.get(url)
#     doc = BeautifulSoup(res.text,"html.parser")
#     itemList = doc.find_all(class_="collectionItemDetails")
#     for item in itemList:
#         downloadMod(item.find("a", href=True)['href'])

def downloadCollection(url):
    mods = []
    gameid = fetchConfiguration('gameID')
    dwn = fetchConfiguration('downloadDir')
    res = requests.get(url)
    doc = BeautifulSoup(res.text,"html.parser")
    itemList = doc.find_all(class_="collectionItemDetails")
    for item in itemList:
        mod_url = item.find("a", href=True)['href']
        res = requests.get(mod_url)
        doc = BeautifulSoup(res.text, "html.parser")
        title = doc.head.title.text.split("::")[1].strip()
        _id = processURL(url)
        print(f'Queuing: {title}, {_id}')
        mods.append({
            'gameId': gameid,
            'id': _id,
            'name': title
        })
    print(f'\n\nSending Mod Collection:\n{json.dumps(mods, indent=4)}')
    downloadCollectionSCMD(mods)
