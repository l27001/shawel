#!/usr/bin/python3
from PIL import Image
import os, requests, random
dir_path = os.path.dirname(os.path.realpath(__file__))

def zerkalo(file, typ=1):
    p = requests.get(file)
    if(os.path.isdir(tmp_dir+"/zerkalo") == False):
        os.mkdir(tmp_dir+"/zerkalo")
    nme = tmp_dir+'/zerkalo/'+str(random.randint(1,655355))+'.jpg'
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

    W,H = im.size
    if(W > H):
        razm = W
        razmm = H
    else:
        razm = H
        razmm = W

    wm = Image.open(dir_path+"/../demotivator/200.png")
    wm = wm.resize((razmm//4,razmm//4))
    wmw,wmh = wm.size
    im.paste(wm,(W-wmw,H-wmh),wm)

    im.save(nme)
    return nme