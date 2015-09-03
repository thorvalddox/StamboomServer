__author__ = 'thorvald'


import os,glob

def makedocs():
    os.system("make -C doc/ html")

def createdoc_pydoc(name):
    os.system("pydoc3 -w {}".format(name))
    os.system("mv {0} doc_pydoc/{0}".format(name))

if __name__ == "__main__":
    makedocs()