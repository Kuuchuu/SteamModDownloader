from scripts.init import start
import argparse

def main(Repo_Owner=None, Repo_Name=None, config=None, configFile=None, game=None, mod=None, pack=None, outputDir=None, list=False, args=None):
    parser = argparse.ArgumentParser(description="Launch SMD")
    parser.add_argument("Repo_Owner", help="Repository Owner", nargs='?', default="Kuuchuu")
    parser.add_argument("Repo_Name", help="Repository Name", nargs='?', default="SteamModDownloader")
    parser.add_argument("-c", "--config", type=json.loads, help="Configuration in JSON format.")
    parser.add_argument("-f", "--configFile", help="Path to the configuration file.")
    parser.add_argument("-g", "--game", help="Game's Steam ID.")
    parser.add_argument("-m", "--mod", help="Mod ID numbers or URLs.")
    parser.add_argument("-p", "--pack", help="Pack ID numbers or URLs.")
    parser.add_argument("-o", "--outputDir", help="Path to the mod download output directory.")
    parser.add_argument('-l', '--list', action='store_true', help='List all currently downloaded mods.')
    
    args = parser.parse_args()
    
    if args is not None:
        args_dict = {k: v for k, v in vars(args).items() if v is not None}
        start(args_dict.get('Repo_Owner', Repo_Owner), args_dict.get('Repo_Name', Repo_Name), vars(args_dict))
    else:
        args = parser.parse_args()
        start(args.Repo_Owner, args.Repo_Name, vars(args))

if __name__=="__main__":
    main()