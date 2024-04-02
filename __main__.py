from scripts.init import start
import argparse

def main():
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
    start(args.Repo_Owner, args.Repo_Name, vars(args))

if __name__=="__main__":
    main()