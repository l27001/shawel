#!/usr/bin/python3
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
import random,requests,os
dir_path = os.path.dirname(os.path.realpath(__file__))

def demotiv(text,text2,img1):
	text = str(text)
	text2 = str(text2)
	p = requests.get(img1)
	if(os.path.isdir(dir_path+"/files") == False):
		os.mkdir(dir_path+"/files")
	img11 = dir_path+'/files/TEMP_'+str(random.randint(400000,9999999))+'.jpg'
	with open(img11, "wb") as out:
		out.write(p.content)

	nme = dir_path+'/files/'+str(random.randint(1,655355))+'.jpg'
	img1 = Image.open(img11)

	os.remove(img11)

	W1,H1 = img1.size
	W = int(W1/2.7)+W1
	H = int(H1/1.5)+H1

	n = H/10+10

	font = ImageFont.truetype(dir_path+'/11874.ttf', int(round(H/15,0)))
	font2 = ImageFont.truetype(dir_path+'/11874.ttf', int(round(H/21,0)))

	wm = ImageFont.truetype(dir_path+'/11874.ttf', int(round(H/80,0)))

	w,h = font.getsize(text)
	x = (W-w)/2
	text_position = (x, H-H/4)

	w,h = font2.getsize(text2)

	x = (W-w)/2
	text_position2 = (x, (H-H/4)+n-10)
	text_color = (255,255,255)

	img1 = ImageOps.expand(img1, border=W//150, fill='black')
	img1 = ImageOps.expand(img1, border=H//300, fill='white')

	img = Image.new("RGB",(W,H),color=0)
	draw = ImageDraw.Draw(img)

	x = int((W - W1)/2)
	y = int(H/9)

	watermark = "Made by @shawelbot"

	waterw,waterh = wm.getsize(watermark)

	img.paste(img1,(x,y))
	draw.text(text_position, text, text_color, font)
	draw.text((W-waterw,H-waterh), watermark, text_color, wm)
	draw.text(text_position2, text2, text_color, font2)

	img.save(nme)
	return nme

if(__name__ == '__main__'):
	import sys
	text = sys.argv[1]
	text2 = sys.argv[2]
	img1 = sys.argv[3]

	demotiv(text,text2,img1)
