__author__ = 'Thorvald'

import os,os.path, glob, shutil
from PIL import Image
from itertools import count

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

def change_image(file):
    newindex = ImagePath.new()
    print("start saving")
    file.save(ImagePath.get(newindex))
    print("end saving")
    return(newindex)

def rotate_image(oldpath,newpath,orient):
    im = Image.open(oldpath)
    imr = im.rotate(90*orient)
    imr.save(newpath)

def destroy_subs(index):
    paths = glob.glob(ImagePath.get_wild(index))
    for p in paths:
        os.remove(p)


def copy_images(person):
    name = person.uname
    source = name_to_path(name)
    if not os.path.exists(source):
        return name, 0
    number = ImagePath.new()
    path = ImagePath.get(number)
    shutil.copy(source, path)
    return name, number


class ImagePath:
    @staticmethod
    def new():
        for i in count():
            path = ImagePath.get(i)
            if not os.path.exists(path):
                return i


    @staticmethod
    def get(number,orient=0,genstring="StamboomServer/static/images/IM{:06}{}.jpg"):
        suffix = ["","_r","_o","_l"][orient]
        base = "StamboomServer/static/images/IM{:06}{}.jpg".format(number,"")
        rot = "StamboomServer/static/images/IM{:06}{}.jpg".format(number,suffix)
        assert os.path.exists(base),"{} does not exist".format(base)
        if not os.path.exists(rot):
            rotate_image(base,rot,orient)
        return(genstring.format(number,suffix))

    @staticmethod
    def get_static(number,orient=0):
        return(ImagePath.get(number,orient,"images/IM{:06}{}.jpg"))
    @staticmethod
    def get_wild(number):
        return(ImagePath.get(number,0,"StamboomServer/static/images/IM{:06}_*.jpg"))

