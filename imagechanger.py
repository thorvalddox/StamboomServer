__author__ = 'Thorvald'

import os,os.path

allowed_extensions = [".jpg"]

def check_valid(filename:str):
    return any(filename.endswith(a) for a in allowed_extensions)

def name_to_path(name):
    name = name.replace(" ","_")
    return("StamboomServer/static/kopkes/{}.jpg".format(name))

def makeversion(name):
    location = name_to_path(name)
    version = location
    i = 0
    while os.path.isfile(version):
        version = location + "v" + str(i)
        i += 1
    return(version)

def change_image(name,file):
    source = file.filename
    version = makeversion(name)
    location = name_to_path(name)
    print("start renaming")
    if version != location:
        os.rename(location,version)
    print("start saving")
    file.save(location)
    print("end saving")