#!/usr/bin/python3
from PIL import Image, ImageFont, ImageDraw
import os, requests, random
dir_path = os.path.dirname(os.path.realpath(__file__))

def text(file, text):
    p = requests.get(file)
    tmp_dir_path = tmp_dir+"/text"
    if(os.path.isdir(tmp_dir_path) == False):
        os.mkdir(tmp_dir_path)
    nme = f"{tmp_dir_path}/{random.randint(1,655355)}.jpg"
    with open(nme, "wb") as out:
        out.write(p.content)
    im = Image.open(nme)
    w,h = (0,0)
    W,H = im.size
    if(W > H):
        razm = W
        razmm = H
    else:
        razm = H
        razmm = W
    font = ImageFont.truetype(dir_path+'/NP.ttf', razm//17)
    text = [text]
    #i = 0
    out = []
    w1,h1 = font.getsize(text[0])
    while len(text) != 0:
        w1,h1 = font.getsize(text[0])
        while w1 > W-10:
            t = text[0].split()
            try:
                nm = text[1].split()
            except IndexError:
                nm = []
            nm.insert(0,t[-1])
            text = [" ".join(t[:-1])," ".join(nm)]
            w1,h1 = font.getsize(text[0])
        out.append(text[0])
        del(text[0])
        #i+=1
    draw = ImageDraw.Draw(im)
    k = len(out)-1
    for n in out:
        w1,h1 = font.getsize(n)
        text_position = (W//2-w1//2,H-h1-razm//25)
        draw.text((text_position[0],text_position[1]-(razm//20)*k), n, (255,255,255), font)
        k-=1

    wm = Image.open(dir_path+"/../demotivator/200.png")
    wm = wm.resize((razmm//4,razmm//4))
    wmw,wmh = wm.size
    im.paste(wm,(W-wmw,H-wmh),wm)

    im.save(nme)
    return nme