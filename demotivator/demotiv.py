#!/usr/bin/python3
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import sys,random,requests,os
dir_path = os.path.dirname(os.path.realpath(__file__))

#text = sys.argv[1]
#text2 = sys.argv[2]
#img1 = sys.argv[3]

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

	#W,H = 500,200

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

	img = Image.new("RGB",(W,H),color=0)

	draw = ImageDraw.Draw(img)

	blw = int(W1*1.02)
	blh = int(H1*1.02)

	x = int((W - W1)/2)
	y = int(H/9)

	blimg = Image.new("RGB",(blw,blh),color=(255,255,255))

	blww = x-(blw - W1)//2
	blhh = y-(blw - W1)//4

	raznw = (blw - W1)//6
	raznh = (blh - H1)//6

	nnimg = Image.new("RGB",(blw-raznw*2,blh-raznh*2))

	img.paste(blimg,(blww, blhh))
	img.paste(nnimg,(blww+raznw, blhh+raznh))
	img.paste(img1,(x,y))
	draw.text(text_position, text, text_color, font)
	draw.text((0,0), "Made by @shawe1", text_color, wm)
	draw.text(text_position2, text2, text_color, font2)

	img.save(nme)
	return nme
