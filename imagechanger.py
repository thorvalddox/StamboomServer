__author__ = 'Thorvald'

import os,os.path, glob
from PIL import Image

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
    destroy_thumbnail(name)
    source = file.filename
    version = makeversion(name)
    location = name_to_path(name)
    print("start renaming")
    if version != location:
        os.rename(location,version)
    print("start saving")
    file.save(location)
    print("end saving")

def rotate_image(name,clockwize=True):
    destroy_thumbnail(name)
    path = name_to_path(name)
    Image.open(path).rotate([90, -90][clockwize]).save(path)

def destroy_thumbnail(name):
    paths = glob.glob(name_to_path(name+"_*x*"))
    for p in paths:
        os.remove(p)