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

def rotate_image(index,clockwize=True):
    destroy_subs(index)
    path = ImagePath.get(index)
    im = Image.open(path)
    imr = im.rotate([90, -90][clockwize])
    newindex = ImagePath.new()
    path = ImagePath.get(newindex)
    imr.save(path)
    return(newindex)

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
    def get(number):
        return("StamboomServer/static/images/IM{:06}.jpg".format(number))

    @staticmethod
    def get_static(number):
        return("images/IM{:06}.jpg".format(number))

    @staticmethod
    def get_wild(number):
        return("StamboomServer/static/images/IM{:06}_*.jpg".format(number))