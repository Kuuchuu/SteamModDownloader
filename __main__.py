from scripts.init import start

# This whole file is fecked. Oops

def main(Repo_Owner=None, Repo_Name=None, config=None, configFile=None, game=None, mod=None, collection=None, outputDir=None, list=False):
    args = {"config"=config, "configFile"=configFile, "game"=game, "mod"=mod, "collection"=collection, "outputDir"=outputDir, "list"=list}
    start(Repo_Owner, Repo_Name, options=args)


if __name__=="__main__":
    main()