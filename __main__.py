from scripts.init import start
from sys import argv

Repo_Owner = argv[1] if len(argv) > 1 else None
Repo_Name = argv[2] if len(argv) > 1 else None

if __name__=="__main__":
    start(Repo_Owner, Repo_Name)