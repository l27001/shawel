#!/usr/bin/python3
from PIL import ImageFont, ImageOps, Image, ImageDraw 
import random,requests,os
dir_path = os.path.dirname(os.path.realpath(__file__))

def demotiv(text,text2,img1):
	text = str(text)
	text2 = str(text2)
	p = requests.get(img1)
	if(os.path.isdir(tmp_dir+"/demotiv") == False):
		os.mkdir(tmp_dir+"/demotiv")
	nme = tmp_dir+'/demotiv/'+str(random.randint(1,655355))+'.jpg'
	with open(nme, "wb") as out:
		out.write(p.content)
	img1 = Image.open(nme)
	W1,H1 = img1.size
	if(W1 < 100 or H1 < 100):
		return nme
	W = int(W1//2.7+W1)
	H = int(H1//1.5+H1)
	if(W > H):
		razm = W
		razmm = H
	else:
		razm = H
		razmm = W
	n = H//10+10

	font = ImageFont.truetype(dir_path+'/11874.ttf', razm//15)
	font2 = ImageFont.truetype(dir_path+'/11874.ttf', razm//21)

	w1,h1 = font.getsize(text)
	w,h = font2.getsize(text2)
	if(w1 > W or w > W):
		if(w1 > w):
			W = w1 + w1//20
		elif(w > w1):
			W = w + w//20
	text_position = ((W-w1)//2, H-H//4)
	text_position2 = ((W-w)//2, (H-H//4)+n-10)
	if(text_position[1]+razm//15 >= text_position2[1]):
		text_position2 = ((W-w)//2, (H-H//4)+n-10+razm//40)
	H = H+razm//40

	text_color = (255,255,255)
	img1 = ImageOps.expand(img1, border=razm//150, fill='black')
	img1 = ImageOps.expand(img1, border=razm//300, fill='white')
	img = Image.new("RGB",(W,H),color=0)
	draw = ImageDraw.Draw(img)
	x = int((W - W1)//2)
	y = int(H//9)
	img.paste(img1,(x,y))
	draw.text(text_position, text, text_color, font)
	wm = Image.open(dir_path+"/200.png")
	wm = wm.resize((razmm//4,razmm//4))
	wmw,wmh = wm.size
	draw.text(text_position2, text2, text_color, font2)
	img.paste(wm,(W-wmw,H-wmh),wm)
	img.save(nme)
	return nme
