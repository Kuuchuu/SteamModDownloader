import requests
from bs4 import BeautifulSoup
from scripts.config import fetch_configuration
from scripts.steamcmd import download_mod_list_scmd

def process_url(url):
    result = url.split('id=')[1]
    if 'searchtext' in url:
        result = result.split('&searchtext')[0]
    return result

def check_type(url):
    if "https" not in url:
        return None
    res=requests.get(url)
    doc=BeautifulSoup(res.text,"html.parser")
    if c_items := doc.find_all(class_="collectionItemDetails"):
        return "collection"
    else:
        return "mod"

def process_mod(url, collection=False):
    mods = []
    res = requests.get(url)
    doc = BeautifulSoup(res.text, "html.parser")
    if collection:
        item_list = doc.find_all(class_="collectionItemDetails")
        for item in item_list:
            mod_url = item.find("a", href=True)['href']
            _id = process_url(mod_url)
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
        _id = process_url(url)
        print(f'Queuing: {title}, {_id}')
        mods.append({
            'name': title,
            'id': _id
        })
    return mods

def download_mod_list(mod_list=None):
    mods = []
    gameid = fetch_configuration('gameID')
    dwn = fetch_configuration('downloadDir')
    if mod_list is None:
        print('(ERROR) No mods provided!')
        return 1
    for mod_dict in mod_list:
        collections_urls = mod_dict["collections"]
        mod_urls = mod_dict["mods"]
        mods.extend(process_mod(url, True) for url in collections_urls)
        for url in mod_urls:
            mods.append(process_mod(url))
    download_mod_list_scmd(gameid, mods, dwn)