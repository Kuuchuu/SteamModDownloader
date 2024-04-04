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

def downloadCollection(url):
    mods = []
    gameid = fetchConfiguration('gameID')
    dwn = fetchConfiguration('downloadDir')
    res = requests.get(url)
    doc = BeautifulSoup(res.text,"html.parser")
    itemList = doc.find_all(class_="collectionItemDetails")
    for item in itemList: # To-Do: Rework to just use title and id/mod_url from item, instead of scraping additional page.
        mod_url = item.find("a", href=True)['href']
        _id = processURL(mod_url)
        if title_div := item.find(class_="workshopItemTitle"):
            title = title_div.text.strip()
        else:
            title = _id
        print(f'Queuing: {title}, {_id}')
        mods.append({
            'gameId': gameid,
            'id': _id,
            'name': title
        })
    downloadCollectionSCMD(mods, dwn)
