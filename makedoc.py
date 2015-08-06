__author__ = 'thorvald'


import os,glob

def makedocs():
    for file in glob.glob("*.py"):
        name = file[:-3]
        if name == "runlocal":
            continue
        os.system("pydoc3 -w {0}".format(name))
        os.system("mv -f {0}.html doc/{0}.html".format(name))

if __name__ == "__main__":
    makedocs()