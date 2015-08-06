__author__ = 'thorvald'


import os,glob

def makedocs():
    os.system("make -C doc/ html")

if __name__ == "__main__":
    makedocs()