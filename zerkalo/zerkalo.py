#!/usr/bin/python3
from PIL import Image
import os, requests, random
dir_path = os.path.dirname(os.path.realpath(__file__))

def zerkalo(file, typ=1):
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
    obj = im.load()
    if(typ == 1):
        k = half
        for n in range(half,W):
            for x in range(0,H):
                obj[n,x] = obj[k,x]
            k-=1
    else:
        k = W-1
        for n in range(0,half):
            for x in range(0,H):
                obj[n,x] = obj[k,x]
            k-=1

    im.save(nme)
    return nme