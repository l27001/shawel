#!/usr/bin/python3
from PIL import Image
import os, requests, random
dir_path = os.path.dirname(os.path.realpath(__file__))

def zerkalo(file):
    p = requests.get(file)
    if(os.path.isdir(dir_path+"/files") == False):
        os.mkdir(dir_path+"/files")
    nme = dir_path+'/files/'+str(random.randint(1,655355))+'.jpg'
    with open(nme, "wb") as out:
        out.write(p.content)
    im = Image.open(nme)
    w,h = (0,0)
    W,H = im.size
    half = W//2
    out = []
    while h < H:
        w = 0
        while w < W:
            if(w > half):
                pixel = (im.getpixel((half-(w-half),h)))
                im.putpixel((w,h), pixel)
            w+=1
        h+=1

    im.save(nme)
    return nme