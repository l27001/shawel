#!/usr/bin/python3
from PIL import Image, ImageFont, ImageDraw
import os, requests, random
dir_path = os.path.dirname(os.path.realpath(__file__))

def text(file, text):
    p = requests.get(file)
    if(os.path.isdir(dir_path+"/files") == False):
        os.mkdir(dir_path+"/files")
    nme = f"{dir_path}/files/{random.randint(1,655355)}.jpg"
    #nme = f"{dir_path}/files/0.jpg"
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
    im.save(nme)
    return nme